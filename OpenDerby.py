#!/usr/bin/env python
# Author: Dan Radez
# URL: https://github.com/radez/openderby/
#
# OpenDerby is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# OpenDerby is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OpenDerby.  If not, see <http://www.gnu.org/licenses/>.

# Check needed software dependencies to nudge users to fix their setup
import sys
if sys.version_info < (2, 5):
    sys.exit("Sorry, requires Python 2.5, 2.6 or 2.7.")

#try:
#    import Cheetah
#    if Cheetah.Version[0] != '2':
#        raise ValueError
#except ValueError:
#    sys.exit("Sorry, requires Python module Cheetah 2.1.0 or newer.")
#except:
#    sys.exit("The Python module Cheetah is required")

import os
import cherrypy
import logging
import argparse

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage

from openderby.db import SAEnginePlugin
from openderby.db import SATool
from openderby import Derby

class WebSocketHandler(WebSocket):
    def received_message(self, m):
        cherrypy.engine.publish('websocket-broadcast', m)

    def closed(self, code, reason="A client left the room without a proper explanation."):
        cherrypy.engine.publish('websocket-broadcast', TextMessage(reason))

def main():
    from ws4py import configure_logger
    configure_logger(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='OpenDerby CherryPy Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9000, type=int)
    parser.add_argument('--ssl', action='store_true')
    args = parser.parse_args()
    
    cherrypy.config.update({'server.socket_host': args.host,
                            'server.socket_port': args.port,
                            'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))})
    
    if args.ssl:
        cherrypy.config.update({'server.ssl_certificate': './server.crt',
                                'server.ssl_private_key': './server.key'})
    
    # Setup WebSockets for the scoreboard
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()
        
    # Database setup
    SAEnginePlugin(cherrypy.engine).subscribe()
    cherrypy.tools.db = SATool()



    cherrypy.tree.mount(Derby(args.host, args.port, args.ssl), '', config={
    '/': {'tools.db.on': True},
    '/ws': {
        'tools.websocket.on': True,
        'tools.websocket.handler_cls': WebSocketHandler
        },
    '/js': {
          'tools.staticdir.on': True,
          'tools.staticdir.dir': 'js'
        }
    })
    
    # Use Flask for the Admin
    from openderby.registration import app
    from openderby import models
    cherrypy.tree.graft(app, '/registration')

    # Start up CherryPy
    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == "__main__":
    main()
