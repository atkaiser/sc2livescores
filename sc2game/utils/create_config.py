import numpy as np
import cv2
import cv2.cv as cv

boxes = []
box_name = raw_input()

def on_mouse(event, x, y, flags, params):
    global box_name
    if event == cv.CV_EVENT_LBUTTONDOWN:
        print box_name + "_l=" + str(x)
        print box_name + "_u=" + str(y)

    elif event == cv.CV_EVENT_LBUTTONUP:
        print box_name + "_r=" + str(x)
        print box_name + "_d=" + str(y)
        box_name = raw_input()


count = 0

img = cv2.imread('wcs_a2_chal-1.jpeg',0)
cv2.namedWindow('real image')
cv.SetMouseCallback('real image', on_mouse, 0)
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
