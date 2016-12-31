import sys
import os
sys.path.append(os.environ['SC2LS_PATH'])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sc2livescores.settings")
from sc2livescores import sets
from sc2livescores import settings
from PIL import Image
import time
import ConfigParser
import subprocess
import errno
from livestreamer import Livestreamer
import threading
import re
from django.utils import timezone
from sc2game.models import Game, Player, Stream, Bracket
import logging
import requests
import string
import random
from shutil import copyfile
import pdb

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.handlers.RotatingFileHandler(os.path.join(settings.LOG_DIR, 'update_state.log'),
                                               maxBytes=50 * 1024 * 1024,
                                               backupCount=5)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


FNULL = open(os.devnull, 'w')
image_temp_file = "../temps/"

parser = ConfigParser.ConfigParser()
parser.read(sets.conf_file)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise


def threshold(im, section_name, pic):
    if parser.has_option(section_name, pic + '_thresh'):
        im_grey = im.convert('L')
        return im_grey.point(lambda x: 256 if x > int(parser.get(section_name, pic + '_thresh')) else 0)
    else:
        return im


def get_image(section_name, im, pic, mode):
    logger.debug("get_image for " + section_name + " image_area " + pic)
    resolution = im.size[1]
    l = int(parser.get(section_name, pic + '_l_' + str(resolution)))
    u = int(parser.get(section_name, pic + '_u_' + str(resolution)))
    r = int(parser.get(section_name, pic + '_r_' + str(resolution)))
    d = int(parser.get(section_name, pic + '_d_' + str(resolution)))
    temp = im.crop((l, u, r, d))
    temp = threshold(temp, section_name, pic)
    mkdir_p(image_temp_file + section_name)
    temp.save(image_temp_file + section_name + "/" + pic + '.jpeg')
    command = [sets.tesseract,
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
    command = [sets.FFMPEG_BIN,
               '-i', file_name,
               '-r', '1',
               '-t', '1',
               image_temp_file + section_name + '/' + section_name + '-%d.jpeg']
    logger.debug("Call to FFMPEG: " + str(command))
    subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)

    im = Image.open(image_temp_file + section_name + '/' + section_name + '-1.jpeg')
    return im


def get_data_from_image(im, parser, section_name):
    my_data = {}
    resolution = im.size[1]
    logger.debug("resolution: " + str(resolution) + " for section: " + section_name)
    
    if parser.has_option(section_name, "same_as"):
        section_name = parser.get(section_name, "same_as")
    
    texts = ['l_name', 'r_name']
    for name in texts:
        if parser.has_option(section_name, name + "_l_" + str(resolution)):
            my_data[name] = get_image(section_name, im, name, "name")
            
    supplies = ['l_supply', 'r_supply']
    for supply in supplies:
        if parser.has_option(section_name, supply + "_l_" + str(resolution)):
            my_data[supply] = get_image(section_name, im, supply, "supply")
            
    if parser.has_option(section_name, "time_l_" + str(resolution)):
        my_data['time'] = get_image(section_name, im, "time", "time")

    numbers = ['l_score', 'r_score', 'l_minerals', 'r_minerals', 'l_gas', 'r_gas',
               'l_workers', 'r_workers', 'l_army', 'r_army']
    for digits_only in numbers:
        if parser.has_option(section_name, digits_only + "_l_" + str(resolution)):
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
        plugin.set_option('oauth_token', 'xtlhyl6uapy6znsvuhy4zfk0jbt086')
        streams = plugin.get_streams()
        stream = streams['best']
    except Exception:
        pass
    return stream


def get_players(stream_obj):
    players = Player.objects.filter(stream=stream_obj)
    if len(players) != 2:
        if len(players) != 0:
            logger.debug("Something really strange is going on here.")
            logger.debug("Deleting old players and creating new ones.")
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
            num_valid_fields += 3
    
    for field in ['l_supply', 'r_supply']:
        if re.search(r'\d+/\d+',data[field]):
            num_valid_fields += 1
            
    for field in ['l_minerals', 'r_minerals', 'l_gas', 'r_gas', 'l_score', 'r_score']:
        if data[field] >= 0:
            num_valid_fields += 1
    if num_valid_fields >= 12:
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


def save_images(section_name):
    for category in ["score", "name", "gas", "minerals", "supply"]:
        for prefix in ["l_", "r_"]:
            name = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
            path = "/home/sc2ls/pics/" + section_name + "/" + category
            mkdir_p(path)
            copyfile(image_temp_file + section_name + "/" + prefix + category + '.jpeg',
                     path + "/" + name + ".jpeg")
    name = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    path = "/home/sc2ls/pics/" + section_name + "/time"
    mkdir_p(path)
    copyfile(image_temp_file + section_name + "/time" + '.jpeg',
                     path + "/" + name + ".jpeg")


def get_info_from_stream(section_name):
    tries = 0
    while True:
        try:
            # Reload parser vars
            #parser = ConfigParser.ConfigParser()
            #parser.read(sets.conf_file)
            
            #logger.debug("Done reading conf for: " + section_name)
            
            stream_url = parser.get(section_name, 'stream_url')
            stream_obj = Stream.objects.filter(url=stream_url)
            if not stream_obj:
                stream_obj = Stream(url=stream_url, name=parser.get(section_name, 'stream_name'))
                stream_obj.save()
            else:
                stream_obj = stream_obj[0]

            logger.debug("Got stream object for: " + section_name)

            stream_data = get_stream(stream_url)

            logger.debug("Done getting stream for: " + section_name)

            set_up_bracket(section_name, stream_obj)

            if not stream_data:
                if stream_obj.up and tries <= 2:
                    logger.debug("Failed getting up stream, stream_url: " + stream_url
                                 + " tries: " + str(tries))
                    tries += 1
                    time.sleep(5)
                    continue
                logger.info("There doesn't seem to be any stream available for: " + stream_url)
                tries = 0
                stream_obj.up = False
                stream_obj.save()
                time.sleep(60)
                continue
            else:
                tries = 0
            
            headers = {'Client-ID': 'jy4zwuphqfdvh2nfygxkzb66z23wjz',
                       'Accept': 'application/vnd.twitchtv.v3+json'}
            res = requests.get("https://api.twitch.tv/kraken/channels/" + stream_url, headers=headers);
            json_res = res.json()
            if json_res["game"] != "StarCraft II":
                logger.info("Current game is not SCII for stream: " + stream_url)
                stream_obj.up = False
                stream_obj.save()
                time.sleep(60)
                continue
            if "rerun" in json_res["status"].lower():
                logger.info("Showing rerun in stream: " + stream_url)
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
            
            for key in my_data.keys():
                logger.debug(str(key) + ": " + str(my_data[key]))

            players = get_players(stream_obj)
            
                
            if 'l_name' not in my_data:
                logger.info("No correct conf for: " + stream_url)
                stream_obj.up = False
                stream_obj.save()
                time.sleep(60)
                continue
            
            if not game_live(im, my_data):
                if game.game_on:
                    game.game_off_time = timezone.now()
                game.game_on = False
                game.save()
                time.sleep(10)
                logger.info("No live game for: " + stream_url)
                continue
            else:
                game.game_on = True
            
#             save_images(section_name)

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
    
            logger.info("Done with loop for: " + stream_url)
            time.sleep(2)
        except KeyboardInterrupt:
            exit()
        except Exception as _:
            logger.error("Something went wrong for stream: " + stream_url, exc_info=True)


def get_stream_info_thread():
    # Hacky way to pass arg
    section_name = threading.currentThread().getName()
    get_info_from_stream(section_name)


if __name__ == "__main__":
    logger.debug("Start of function")
    logger.debug("Deleting old streams")
    sections = parser.sections()
    for stream in Stream.objects.all():
        if stream.name not in sections:
            stream.up = False
            stream.save()
    for section in parser.sections():
        logger.debug("Starting thread for " + section)
        t = threading.Thread(name=section, target=get_stream_info_thread)
        t.start()

