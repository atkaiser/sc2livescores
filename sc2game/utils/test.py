'''
Created on Jul 16, 2014

@author: akaiser
'''

import sys
import logging
from logging.handlers import TimedRotatingFileHandler

sys.path.append('/Users/akaiser/Documents/workspace/sc2livescores')

from sc2livescores import sets

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = TimedRotatingFileHandler('test.log',
                                                    when='midnight',
                                                    backupCount=5,
                                                    utc=True)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

logger.debug("log this")