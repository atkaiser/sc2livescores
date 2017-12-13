import ConfigParser
from cStringIO import StringIO
import errno
import gc
import logging
import os
import pdb
import random
import re
from shutil import copyfile
import string
import subprocess
import sys
import threading
import time

from PIL import Image
import PIL
from django.utils import timezone
from livestreamer import Livestreamer
import objgraph
import requests

sys.path.append(os.environ['SC2LS_PATH'])
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sc2livescores.settings")
from sc2game.models import Game, Player, Stream, Bracket
from sc2livescores import sets
from sc2livescores import settings

PRINT_MEMORY_INFO = False

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler = logging.handlers.RotatingFileHandler(os.path.join(settings.LOG_DIR, 'update_state.log'),
                                                    maxBytes=50 * 1024 * 1024,
                                                    backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
# When running on a server we want to log to a file, so use this line
logger.addHandler(file_handler)
# When developing we want to log to the console so we should use this line
# logger.addHandler(console_handler)


FNULL = open(os.devnull, 'w')
image_temp_file = "../temps/"

display_type_confs = ConfigParser.ConfigParser()
display_type_conf_files = []
for file_name in os.listdir(sets.display_type_confs_dir):
    if file_name.endswith(".conf"):
        display_type_conf_files.append(os.path.join(
            sets.display_type_confs_dir, file_name))
display_type_confs.read(display_type_conf_files)

stream_confs = ConfigParser.ConfigParser()
stream_confs.read(sets.stream_conf_file)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


def threshold(im, display_type, pic):
    if display_type_confs.has_option(display_type, pic + '_thresh'):
        im_grey = im.convert('L')
        return im_grey.point(lambda x: 256 if x > int(display_type_confs.get(display_type, pic + '_thresh')) else 0)
    else:
        return im


def get_image(display_type, im, pic, mode):
    logger.debug("get_image for " + display_type + " image_area " + pic)
    resolution = im.size[1]
    l = int(display_type_confs.get(display_type, pic + '_l_' + str(resolution)))
    u = int(display_type_confs.get(display_type, pic + '_u_' + str(resolution)))
    r = int(display_type_confs.get(display_type, pic + '_r_' + str(resolution)))
    d = int(display_type_confs.get(display_type, pic + '_d_' + str(resolution)))
    temp = im.crop((l, u, r, d))
    temp = threshold(temp, display_type, pic)
    width, height = temp.size
    scale = 5
    temp = temp.resize((width * scale, height * scale),
                       resample=PIL.Image.BICUBIC)
    mkdir_p(image_temp_file + display_type)
    temp.save(image_temp_file + display_type + "/" + pic + '.jpeg')
    command = [sets.tesseract,
               image_temp_file + display_type + "/" + pic + '.jpeg',
               image_temp_file + display_type + "/" + pic,
               '-psm', '8']
    command.append(mode)
    subprocess.call(command, stdout=FNULL, stderr=subprocess.STDOUT)
    return open(image_temp_file + display_type + "/" + pic + '.txt').read().strip()


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

    im = Image.open(image_temp_file + section_name +
                    '/' + section_name + '-1.jpeg')
    return im


def get_data_from_image(im, display_type):
    my_data = {}
    resolution = im.size[1]
    logger.debug("resolution: " + str(resolution) +
                 " for section: " + display_type)

    texts = ['l_name', 'r_name']
    for name in texts:
        if display_type_confs.has_option(display_type, name + "_l_" + str(resolution)):
            my_data[name] = get_image(display_type, im, name, "name")

    supplies = ['l_supply', 'r_supply']
    for supply in supplies:
        if display_type_confs.has_option(display_type, supply + "_l_" + str(resolution)):
            my_data[supply] = get_image(display_type, im, supply, "supply")

    if display_type_confs.has_option(display_type, "time_l_" + str(resolution)):
        my_data['time'] = get_image(display_type, im, "time", "time")

    numbers = ['l_score', 'r_score', 'l_minerals', 'r_minerals', 'l_gas', 'r_gas',
               'l_workers', 'r_workers', 'l_army', 'r_army']
    for digits_only in numbers:
        if display_type_confs.has_option(display_type, digits_only + "_l_" + str(resolution)):
            data = get_image(display_type, im, digits_only, "digits_only")
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
        # It seems best isn't necessarily the best, twitch doesn't seem to consider 60
        # streams, so we should search for those first.
        if '1080p60' in streams:
            stream = streams['1080p60']
        elif '720p60' in streams:
            stream = streams['720p60']
        else:
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


def game_live(data):
    if get_score(data) >= 85:
        return True
    else:
        return False


def get_score(data):
    """
    Return a score out of 100 (float). 100 is we are are sure the 
    data is from a live game 0 is definitely not a live game
    """
    score = 0
    total_possible_points = 0
    num_valid_fields = 0

    for field in ['l_name', 'r_name']:
        worth = 3
        total_possible_points += worth
        if len(data[field]) >= 3:
            score += worth

    for field in ['l_supply', 'r_supply']:
        worth = 4
        total_possible_points += worth
        if re.search(r'\d+/\d+', data[field]):
            score += worth

    for field in ['l_minerals', 'r_minerals', 'l_gas', 'r_gas', 'l_score', 'r_score']:
        worth = 1
        total_possible_points += worth
        if data[field] >= 0:
            num_valid_fields += worth

    return ((score * 1.0) / (total_possible_points * 1.0)) * 100.0


def set_up_bracket(section_name, stream_obj):
    """
    Set up a bracket object for a stream, or delete it if there is no longer a link
    TODO: I shouldn't depend on there only being one bracket object for a stream
    """
    bracket = Bracket.objects.filter(stream=stream_obj)
    if stream_confs.has_option(section_name, 'bracket_link'):
        link = stream_confs.get(section_name, 'bracket_link')
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
            name = ''.join(random.choice(
                string.ascii_lowercase + string.digits) for _ in range(10))
            path = "/home/sc2ls/pics/" + section_name + "/" + category
            mkdir_p(path)
            copyfile(image_temp_file + section_name + "/" + prefix + category + '.jpeg',
                     path + "/" + name + ".jpeg")
    name = ''.join(random.choice(string.ascii_lowercase + string.digits)
                   for _ in range(10))
    path = "/home/sc2ls/pics/" + section_name + "/time"
    mkdir_p(path)
    copyfile(image_temp_file + section_name + "/time" + '.jpeg',
             path + "/" + name + ".jpeg")


def get_info_from_stream(section_name):
    tries = 0
    while True:
        if PRINT_MEMORY_INFO:
            if section_name == "iem":
                gc.collect()
                logger.debug("NEW GRAPH - " + time.strftime("%c"))
                graphOutput = StringIO()
                objgraph.show_most_common_types(file=graphOutput)
                logger.debug(graphOutput.getvalue())
        try:

            stream_url = stream_confs.get(section_name, 'stream_url')
            stream_obj = Stream.objects.filter(url=stream_url)
            if not stream_obj:
                stream_obj = Stream(url=stream_url, name=stream_confs.get(
                    section_name, 'stream_name'))
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
                logger.info(
                    "There doesn't seem to be any stream available for: " + stream_url)
                tries = 0
                stream_obj.up = False
                stream_obj.save()
                time.sleep(60)
                continue
            else:
                tries = 0

            headers = {'Client-ID': 'jy4zwuphqfdvh2nfygxkzb66z23wjz',
                       'Accept': 'application/vnd.twitchtv.v3+json'}
            res = requests.get(
                "https://api.twitch.tv/kraken/channels/" + stream_url, headers=headers)
            json_res = res.json()
            if json_res["game"] != "StarCraft II":
                logger.info(
                    "Current game is not SCII for stream: " + stream_url)
                stream_obj.up = False
                stream_obj.save()
                time.sleep(60)
                continue
            if any(x in json_res["status"].lower() for x in ["rerun", "rebroadcast"]):
                logger.info("Showing rerun in stream: " + stream_url)
                stream_obj.up = False
                stream_obj.save()
                time.sleep(60)
                continue

            # At this point we know we have a stream that is up and we need to
            # parse it

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

            display_type = stream_confs.get(section_name, "display_types")

            my_data = get_data_from_image(im, display_type)

            for key in my_data.keys():
                logger.debug(str(key) + ": " + str(my_data[key]))

            if 'l_name' not in my_data:
                logger.info("No correct conf for: " + stream_url)
                stream_obj.up = False
                stream_obj.save()
                time.sleep(60)
                continue

            if not game_live(my_data):
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

            players = get_players(stream_obj)
            p_l = players[0]
            p_r = players[1]

            categories = ['name', 'score', 'supply',
                          'minerals', 'gas', 'workers', 'army']
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
        except Exception as _:
            logger.error("Something went wrong for stream: " +
                         stream_url, exc_info=True)


if __name__ == "__main__":
    logger.debug("Starting the update_state script")
    logger.debug("Deleting old streams")
    sections = stream_confs.sections()
    stream_names = [stream_confs.get(section, "stream_name")
                    for section in sections]
    for stream in Stream.objects.all():
        if stream.name not in stream_names:
            stream.up = False
            stream.save()
    for section in sections:
        logger.debug("Starting thread for " + section)
        t = threading.Thread(
            name=section, target=get_info_from_stream, args=[section])
        t.setDaemon(True)
        t.start()
    # Wait for a keyboard interrupt and then finish the program
    try:
        while threading.active_count() > 0:
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
