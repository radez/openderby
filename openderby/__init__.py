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

from models import Category, Heat, Car
from registration import app

rankings_key = 'rankings_key'

class Derby(object):
    current_category = 0
    current_heat = 0
    scoreboard_category = 0
    scoreboard_heat = 0

    def __init__(self, host, port, ssl=False):
        self.host = host
        self.port = port
        self.scheme = 'wss' if ssl else 'ws'

    @cherrypy.expose
    def index(self, cat=None):
        return self.results()

    @cherrypy.expose
    def results(self, cat=None, refresh=None):
        results = Heat.query.order_by(Heat.category_id, Heat.id, Heat.lane)
        if refresh:
            cat=Derby.current_category
            anchor=Derby.current_heat
        else:
            anchor=0
        if cat:
            results = results.filter(Heat.category_id==cat)
        tmpl = env.get_template('results.html')
        return tmpl.render(results=results, selected=cat, anchor=anchor, refresh=refresh)

    @cherrypy.expose
    def scoreboard(self):
        cat = Derby.current_category
        heat = Derby.current_heat
        lanes = [{"name": "", "time": ""} for x in range(7)]
        if cat:
            cat_name = Category.query.get(cat)
            for lane in Heat.query.filter_by(category_id=cat,id=heat).all():
                lanes[lane.lane]["name"] = lane.car.name
                if lane.time:
                    lanes[lane.lane]["time"] = "{0:.2f}".format(lane.time)
        else:
            cat_name = "No Race in Progress"
        tmpl = env.get_template('scoreboard.html')
        return tmpl.render(username="User%d" % random.randint(0, 100),
                           host=self.host, port=self.port, scheme=self.scheme,
                           lanes=lanes, category=cat_name, heat=heat)

    @cherrypy.expose
    def ws(self):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))
        cherrypy.engine.publish('websocket-broadcast', 'test')

    @cherrypy.expose
    def status(self, cat=None, heat=None):
        cat = int(cat)
        heat = int(heat)
        if cat and heat:
            Derby.current_category = cat
            Derby.current_heat = heat
        tmpl = env.get_template('status.html')
        return tmpl.render(category=Derby.current_category,
                           heat=Derby.current_heat)

    @cherrypy.expose
    def scoreboard_update(self):
        heat = Derby.current_heat
        s_heat = Derby.scoreboard_heat
        cat = Derby.current_category
        s_cat = Derby.scoreboard_category
        if s_heat != heat or s_cat != cat:
            Derby.scoreboard_heat = heat
            Derby.scoreboard_category = cat

            # clean the lanes
            for i in range(1,7):
                json = '{ "element": "lane%sname", "val": "" }'  % i
                cherrypy.engine.publish('websocket-broadcast', json)
                json = '{ "element": "lane%stime", "val": "" }' % i
                cherrypy.engine.publish('websocket-broadcast', json)

            # send the Category update to the scoreboard
            if int(cat):
                cat_name = Category.query.get(cat)
            else:
                cat_name = "No Race in Progress"
            json = '{ "element": "category", "val": "%s" }'  % cat_name
            cherrypy.engine.publish('websocket-broadcast', json)
            json = '{ "element": "heat", "val": "%s" }'  % heat
            cherrypy.engine.publish('websocket-broadcast', json)

            # Send the lane assignments
            lane_assigns = Heat.query.filter_by(category_id=cat,id=heat)
            for lane in lane_assigns:
                json = '{ "element": "lane%sname", "val": "%s" }'  % (lane.lane, lane.car.name)
                cherrypy.engine.publish('websocket-broadcast', json)
        tmpl = env.get_template('scoreboard_update.html')
        return tmpl.render()

    @cherrypy.expose
    def finish(self, lane, time):
        json = '{ "element": "lane%stime", "val": "%s" }'  % (lane, "{0:.2f}".format(float(time)))
        cherrypy.engine.publish('websocket-broadcast', json)

    @cherrypy.expose
    def publish(self):
        cherrypy.engine.publish('websocket-broadcast', '{ "element": "lane1name", "val": "A test Car\'s name" }')
        cherrypy.engine.publish('websocket-broadcast', '{ "element": "lane1time", "val": "00:00" }')

    @cherrypy.expose
    def pit(self):
        app.db.session.expire_all()
        heats = Heat.query.filter_by(
                           category_id=Derby.current_category
                         ).filter(
                           Heat.id >= Derby.current_heat
                         ).order_by(Heat.id, Heat.lane)
        tmpl = env.get_template('pit.html')
        return tmpl.render(category=Derby.current_category,
                           heat=Derby.current_heat, heats=heats)

    @cherrypy.expose
    def rankings(self, key=None):
        results = []
        if key == rankings_key:
            app.db.session.expire_all()
            bests = app.db.session.query(Heat.car_id.label('car_id'), app.db.func.min(Heat.time).label('best_time')).group_by(Heat.car_id).subquery()
            results = app.db.session.query(Heat.id.label('heat_id'), Heat.category_id.label('category'), Category.name.label('cat_name'),\
                                       Heat.car_id.label('car_id'), Heat.lane, Heat.time, Car.name, Car.driver, bests.c.best_time)\
                                         .filter_by(time=bests.c.best_time)\
                                         .outerjoin(bests, Heat.car_id==bests.c.car_id).order_by('category').order_by('best_time')\
                                         .join(Category, Heat.category_id==Category.id).join(Car, Heat.car_id==Car.id)


            results = results.all()
        tmpl = env.get_template('rankings.html')
        return tmpl.render(results=results)
