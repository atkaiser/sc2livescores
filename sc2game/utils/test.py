'''
Created on Jul 16, 2014

@author: akaiser
'''

import sys
import cv2

if __name__ == '__main__':
    im_path = sys.argv[1]
    img = cv2.imread(im_path, 0)
    mser = cv2.MSER_create()
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    vis = img.copy()

    regions = mser.detectRegions(img, None)
    hulls = [cv2.convexHull(p.reshape(-1, 1, 2)) for p in regions]
    cv2.polylines(vis, hulls, 1, (0, 255, 0))

    cv2.imshow('img', vis)
    count = 0
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