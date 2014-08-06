import update_state
import sys
from PIL import Image

if len(sys.argv) != 3:
    print "Use test_image.py <image to test on> <stream name>"
    sys.exit()
    
im = Image.open(sys.argv[1])
my_data = update_state.get_data_from_image(im, update_state.parser, sys.argv[2])

for key in my_data.keys():
    print str(key) + ": " + str(my_data[key])
    
print update_state.game_live(im, my_data)