import numpy as np
import cv2
import sys

if len(sys.argv) != 3:
    print "Use create_config.py <image to test on> <resolution>"
    sys.exit()

im_path = sys.argv[1]
res = sys.argv[2]

boxes = []
box_name = raw_input()

def on_mouse(event, x, y, flags, params):
    global box_name
    if event == cv2.EVENT_LBUTTONDOWN:
        print box_name + "_l_" + res + "=" + str(x)
        print box_name + "_u_" + res + "=" + str(y)
    elif event == cv2.EVENT_LBUTTONUP:
        print box_name + "_r_" + res + "=" + str(x)
        print box_name + "_d_" + res + "=" + str(y)
        print ""
        box_name = raw_input()


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
