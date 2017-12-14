import ConfigParser
import sys

from PIL import Image

# from sc2livescores import sets
import update_state


if len(sys.argv) < 2:
    print "Use test_image.py <display_type> <image to test on>"
    sys.exit()

section_name = sys.argv[1]

if len(sys.argv) == 3:
    im = Image.open(sys.argv[2])
# else:
    # TODO this needs to be redone
#     parser = ConfigParser.ConfigParser()
#     parser.read(sets.conf_file)
#     stream_url = parser.get(section_name, 'stream_url')
#     stream = update_state.get_stream(stream_url)
#     im = update_state.get_screenshot(stream, section_name)

resolution = im.size[1]
print "resolution: " + str(resolution) + " for section: " + section_name
my_data = update_state.get_data_from_image(im, section_name)

for key in my_data.keys():
    print str(key) + ": " + str(my_data[key])

print update_state.game_live(my_data)
print update_state.get_score(my_data)
