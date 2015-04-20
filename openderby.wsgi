import logging, sys
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/openderby/')
from openderby import app as application

