import tempfile
import os
from livestreamer import Livestreamer
from subprocess import call
import sys
from PIL import Image
import update_state
import sys
import ConfigParser
from sc2livescores import sets

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError:
        pass

if len(sys.argv) != 2:
    print "Use get_image_from_stream.py <stream_name>"
    print "<stream_name> should be like 'gsl' or 'basetradetv'"
    sys.exit()

stream_name = sys.argv[1]

FFMPEG_BIN = "/usr/local/bin/ffmpeg"
temp_dir = tempfile.gettempdir()
saved_images = '/Users/akaiser/Documents/workspace/sc2livescores/sc2game/images'
mkdir_p(saved_images)

stream = update_state.get_stream(stream_name)


# download enough data to make sure the first frame is there
fd = stream.open()
data = ''
data += fd.read(3000000)
fd.close() 
fname = temp_dir + '/vid.mp4'
open(fname, 'wb').write(data)
command = [ FFMPEG_BIN,
        '-i', fname,
        '-r', '1',
        '-t', '1',
        temp_dir + '/image-%d.jpeg']
call(command)
new_image_name = saved_images + '/' + stream_name + '.jpeg'
os.rename(temp_dir + '/image-1.jpeg', new_image_name)
os.remove(fname)

im = Image.open(new_image_name)
resolution = im.size[1]

# Test against current configs
for section_name in update_state.parser.sections():
    print "Trying section: " + section_name
    my_data = update_state.get_data_from_image(im, update_state.parser, section_name)
    if "l_name" in my_data:
        if update_state.game_live(im, my_data):
            print "Live game for: " + section_name


print("")
print("Image from stream is at: " + new_image_name)
print("To create config run: python create_config.py " + new_image_name + " " + str(resolution))