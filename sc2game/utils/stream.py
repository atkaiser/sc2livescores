import time, Image

import pdb
import numpy
import tempfile
import os
import time
from livestreamer import Livestreamer
from subprocess import call

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        pass

FFMPEG_BIN = "/usr/local/bin/ffmpeg"
temp_dir = tempfile.gettempdir()
stream_dir = '/Users/akaiser/Documents/workspace/sc2livescores/sc2game/tmp-images/nation_wars/'
mkdir_p(stream_dir)

# change to a stream that is actually online
livestreamer = Livestreamer()
plugin = livestreamer.resolve_url("http://www.dailymotion.com/video/xmpb7j_ogamingtv-inter_videogames?start=341")
streams = plugin.get_streams()
stream = streams['720p']

# download enough data to make sure the first frame is there
i = 81
while True:
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
    os.rename(temp_dir + '/image-1.jpeg', stream_dir + 'frame' + str(i) + '.jpeg')
    os.remove(fname)
    time.sleep(3)
    i += 1

# fd = stream.open()
# data = ''
# data += fd.read(3000000)
# fd.close() 
# fname = temp_dir + '/vid.mp4'
# open(fname, 'wb').write(data)
# command = [ FFMPEG_BIN,
#         '-i', fname,
#         '-r', '1',
#         '-t', '1',
#         temp_dir + '/image-%d.jpeg']
# call(command)
# os.rename(temp_dir + '/image-1.jpeg', '/Users/akaiser/Documents/workspace/random/pics/alpha.jpeg')
# os.remove(fname)

# fd = streamb.open()
# data = ''
# data += fd.read(3000000)
# fd.close()
# fname = temp_dir + '/vid.mp4'
# open(fname, 'wb').write(data)
# command = [ FFMPEG_BIN,
#         '-i', fname,
#         '-r', '1',
#         '-t', '1',
#         temp_dir + '/image-%d.jpeg']
# call(command)
# os.rename(temp_dir + '/image-1.jpeg', '/Users/akaiser/Documents/workspace/random/pics/bravo.jpeg')
# os.remove(fname)
