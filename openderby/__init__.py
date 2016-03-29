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

import random
import cherrypy

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('templates'))

from models import *

class Derby(object):
    current_category = 0
    current_heat = 0

    def __init__(self, host, port, ssl=False):
        self.host = host
        self.port = port
        self.scheme = 'wss' if ssl else 'ws'

    @cherrypy.expose
    def index(self):
        tmpl = env.get_template('scoreboard.html')
        return tmpl.render(username="User%d" % random.randint(0, 100),
                           host=self.host, port=self.port, scheme=self.scheme)

    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))
        cherrypy.engine.publish('websocket-broadcast', 'test')

    @cherrypy.expose
    def status(self, cat=None, heat=None):
        if cat and heat:
            if heat != Derby.current_heat:
                for i in range(1,7):
                    json = '{ "element": "lane%stime", "val": "" }' % i
                    cherrypy.engine.publish('websocket-broadcast', json)

            # send the Category update to the scoreboard
            Derby.current_category = cat
            cat_name = Category.query.get(cat)
            json = '{ "element": "category", "val": "%s" }'  % cat_name
            cherrypy.engine.publish('websocket-broadcast', json)
            Derby.current_heat = heat
            json = '{ "element": "heat", "val": "%s" }'  % heat
            cherrypy.engine.publish('websocket-broadcast', json)

            # Send the lane assignments
            lane_assigns = Heat.query.filter_by(category_id=cat,id=heat)
            for lane in lane_assigns:
                json = '{ "element": "lane%sname", "val": "%s" }'  % (lane.lane, lane.car.name)
                cherrypy.engine.publish('websocket-broadcast', json)

        tmpl = env.get_template('status.html')
        return tmpl.render(category=Derby.current_category,
                           heat=Derby.current_heat)

    @cherrypy.expose
    def finish(self, lane, time):
        json = '{ "element": "lane%stime", "val": "%s" }'  % (lane, time)
        cherrypy.engine.publish('websocket-broadcast', json)

    @cherrypy.expose
    def publish(self):
        cherrypy.engine.publish('websocket-broadcast', '{ "element": "lane1name", "val": "A test Car\'s name" }')
        cherrypy.engine.publish('websocket-broadcast', '{ "element": "lane1time", "val": "00:00" }')

