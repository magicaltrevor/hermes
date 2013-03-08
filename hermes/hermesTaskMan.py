from celery import Celery
from hermes.lib import util as Util
conf = Util.load_conf()
import os
import sys
cmd_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if cmd_folder not in sys.path:
     sys.path.insert(-1, cmd_folder)
     sys.path.insert(-1, cmd_folder + "/engines")
     sys.path.insert(-1, cmd_folder + "/plugins")
     sys.path.insert(-1, cmd_folder + "/lib")
     sys.path.insert(-1, cmd_folder + "/services")
import engines
import services
import plugins
import lib

celery = Celery('hermes.hermesTaskMan',
                broker=conf['broker'],
                backend=conf['backend'],
                include=([conf['modules']]))