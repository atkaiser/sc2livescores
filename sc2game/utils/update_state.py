import sys

sys.path.append('/Users/akaiser/Documents/workspace/sc2livescores')
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sc2livescores.settings")

import Image
from datetime import datetime
import time
import traceback
import ConfigParser
import subprocess
import tempfile
import errno
from livestreamer import Livestreamer
import threading
import re

from sc2game.models import Game, Player, Stream, Bracket

tesseract = '/usr/local/bin/tesseract'
FFMPEG_BIN = "/usr/local/bin/ffmpeg"
FNULL = open(os.devnull, 'w')
temp_dir = tempfile.gettempdir()
image_temp_file = "../temps/"

parser = ConfigParser.ConfigParser()
parser.read('/Users/akaiser/Documents/workspace/sc2livescores/configs.conf')

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

def get_image(section_name, im, pic, mode):
    l = int(parser.get(section_name, pic + '_l'))
    u = int(parser.get(section_name, pic + '_u'))
    r = int(parser.get(section_name, pic + '_r'))
    d = int(parser.get(section_name, pic + '_d'))
    temp = im.crop((l, u, r, d))
    mkdir_p(image_temp_file + section_name)
    temp.save(image_temp_file + section_name + "/" + pic + '.jpeg')
    command = [tesseract,
               image_temp_file + section_name + "/" + pic + '.jpeg',
               image_temp_file + section_name + "/" + pic,
               '-psm', '8']
    command.append(mode)
    subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)
    return open(image_temp_file + section_name + "/" + pic + '.txt').read().strip()


def get_screenshot(stream, section_name):
    stream_reader = stream.open()
    data = ''
    data += stream_reader.read(2000000)
    stream_reader.close()
    mkdir_p(image_temp_file + section_name)
    file_name = image_temp_file + section_name + '/vid.mp4'
    open(file_name, 'wb').write(data)
    command = [FFMPEG_BIN,
               '-i', file_name,
               '-r', '1',
               '-t', '1',
               image_temp_file + section_name + '/' + section_name + '-%d.jpeg']
    subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

    im = Image.open(image_temp_file + section_name + '/' + section_name + '-1.jpeg')
    return im


def get_data_from_image(im, parser, section_name):
    my_data = {}
    texts = ['l_name', 'r_name', 'map']
    for name in texts:
        if parser.has_option(section_name, name + "_l"):
            my_data[name] = get_image(section_name, im, name, "name")
            
    supplies = ['l_supply', 'r_supply']
    for supply in supplies:
        if parser.has_option(section_name, supply + "_l"):
            my_data[supply] = get_image(section_name, im, supply, "supply")
            
    if parser.has_option(section_name, "time_l"):
        my_data['time'] = get_image(section_name, im, "time", "time")

    numbers = ['l_score', 'r_score', 'l_minerals', 'r_minerals', 'l_gas', 'r_gas',
               'l_workers', 'r_workers', 'l_army', 'r_army']
    for digits_only in numbers:
        if parser.has_option(section_name, digits_only + "_l"):
            data = get_image(section_name, im, digits_only, "digits_only")
            try:
                my_data[digits_only] = int(data)
            except:
                my_data[digits_only] = -1
        else:
            my_data[digits_only] = -2

    return my_data


def get_stream(stream_url):
    # change to a stream that is actually online
    livestreamer = Livestreamer()
    stream = None
    try:
        plugin = livestreamer.resolve_url("http://www.twitch.tv/" + stream_url)
        plugin.set_option('oauth_token', 'bi6nl0zlpl4dcakk8k2k79kolpvn69p')
        streams = plugin.get_streams()
        stream = streams['best']
    except Exception:
        pass
    return stream


def get_players(stream_obj):
    players = Player.objects.filter(stream=stream_obj)
    if len(players) != 2:
        if len(players) != 0:
            print "Something really strange is going on here."
            print "Deleting old players and creating new ones."
            for player in players:
                player.delete()
        players = []
        players.append(Player(stream=stream_obj))
        players[0].save()
        players.append(Player(stream=stream_obj))
        players[1].save()
    return players


def game_live(im, data):
    num_valid_fields = 0
    for field in ['l_name', 'r_name']:
        if len(data[field]) >= 3:
            num_valid_fields += 1
    
    for field in ['l_supply', 'r_supply']:
        if re.search(r'\d+/\d+',data[field]):
            num_valid_fields += 1
            
    for field in ['l_minerals', 'r_minerals', 'l_gas', 'r_gas']:
        if data[field] >= 0:
            num_valid_fields += 1
    if num_valid_fields >= 4:
        return True
    else:
        return False


def set_up_bracket(section_name, stream_obj):
    bracket = Bracket.objects.filter(stream=stream_obj)
    if parser.has_option(section_name, 'bracket_link'):
        link = parser.get(section_name, 'bracket_link')
        if not bracket:
            bracket = Bracket(url=link, stream=stream_obj)
            bracket.save()
        else:
            bracket[0].url = link
            bracket[0].save()
    else:
        if bracket:
            bracket[0].delete()


def get_info_from_stream(section_name):
    while True:
        try:
            stream_url = parser.get(section_name, 'stream_url')
            stream_obj = Stream.objects.filter(url=stream_url)
            if not stream_obj:
                stream_obj = Stream(url=stream_url, name=parser.get(section_name, 'stream_name'))
                stream_obj.save()
            else:
                stream_obj = stream_obj[0]

            stream_data = get_stream(stream_url)

            set_up_bracket(section_name, stream_obj)

            if not stream_data:
                print str(datetime.now()) + " There doesn't seem to be any stream available for: " + stream_url
                stream_obj.up = False
                stream_obj.save()
                time.sleep(60)
                continue
            
            stream_obj.up = True
            stream_obj.save()
            
            # Get game objects
            game_objects = Game.objects.filter(stream=stream_obj)
            if not game_objects:
                game = Game(stream=stream_obj)
                game.save()
            else:
                game = game_objects[0]

            im = get_screenshot(stream_data, section_name)

            my_data = get_data_from_image(im, parser, section_name)
            
#             for key in my_data.keys():
#                 print str(key) + ": " + str(my_data[key])
            
            if not game_live(im, my_data):
                game.game_on = False
                game.save()
                time.sleep(10)
                print str(datetime.now()) + " No live game for: " + stream_url
                continue
            else:
                game.game_on = True
            
            players = get_players(stream_obj)

            p_l = players[0]
            p_r = players[1]

            categories = ['name', 'score', 'supply', 'minerals', 'gas', 'workers', 'army']
            for category in categories:
                if 'l_' + category in my_data:
                    setattr(p_l, category, my_data['l_' + category])
                    setattr(p_r, category, my_data['r_' + category])
            p_l.save()
            p_r.save()
            
            # Game stuff
            if 'time' in my_data:
                game.current_time = my_data['time']
            if 'map' in my_data:
                game.on_map = my_data['map']

            game.save()
    
            print str(datetime.now()) + " Done with loop for: " + stream_url
        except KeyboardInterrupt:
            exit()
        except Exception as e:
            print e
            traceback.print_exc()
            print "Something went wrong for stream: " + stream_url
            print datetime.now()


def get_stream_info_thread():
    # Hacky way to pass arg
    section_name = threading.currentThread().getName()
    get_info_from_stream(section_name)


if __name__ == "__main__":
    for section in parser.sections():
        t = threading.Thread(name=section, target=get_stream_info_thread)
        t.start()

