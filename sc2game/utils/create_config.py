import cv2
import sys
from PIL import Image

if len(sys.argv) != 2:
    print "Use create_config.py <image to test on>"
    sys.exit()

im_path = sys.argv[1]
# res = sys.argv[2]

im = Image.open(im_path)
res = str(im.size[1])

configs = ["l_name",
           "r_name",
           "l_score",
           "r_score",
           "l_supply",
           "r_supply",
           "l_minerals",
           "r_minerals",
           "l_gas",
           "r_gas",
           "l_army",
           "r_army",
           "l_workers",
           "r_workers",
           "map",
           "time"]

boxes = []
index = 0
box_name = configs[index]
print box_name

def on_mouse(event, x, y, flags, params):
    global box_name
    global index
    global configs
    if event == cv2.EVENT_LBUTTONDOWN:
        print box_name + "_l_" + res + "=" + str(x)
        print box_name + "_u_" + res + "=" + str(y)
    elif event == cv2.EVENT_LBUTTONUP:
        print box_name + "_r_" + res + "=" + str(x)
        print box_name + "_d_" + res + "=" + str(y)
        print ""
        index += 1
        if index >= len(configs):
            sys.exit(0)
        box_name = configs[index]
        print box_name


count = 0

img = cv2.imread(im_path, 0)
cv2.namedWindow('real image')
cv2.setMouseCallback('real image', on_mouse, 0)
cv2.imshow('real image', img)
while(True):
    count += 1

    if count < 50:
        if cv2.waitKey(33) == 27:
            cv2.destroyAllWindows()
            break
    elif count >= 50:
        if cv2.waitKey(0) == 27:
            cv2.destroyAllWindows()
            break
        count = 0
