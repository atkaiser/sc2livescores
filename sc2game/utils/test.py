'''
Created on Jul 16, 2014

@author: akaiser
'''

import threading
import time

def worker():
    print threading.currentThread().getName(), 'Starting'
    print 
    time.sleep(1)
    print threading.currentThread().getName(), 'Exiting'

if __name__ == '__main__':
    t = threading.Thread(name='worker', target=worker, args=["something"])
    t.start()