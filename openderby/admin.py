import cherrypy

from formalchemy import FieldSet, Grid
from fa.jquery import renderers as jquery
FieldSet.default_renderers.update(jquery.default_renderers)

from formalchemy import config
from fa.jquery.utils import TemplateEngine
config.engine = TemplateEngine()

from openderby.model import Category

class Admin(object):
        
    @cherrypy.expose
    def index(self):
        return

    @cherrypy.expose
    def list(self, type):
        if type == 'category':
            type = Category
        else:
           return
        items = cherrypy.request.db.query(type).all()
        g = Grid(type, items)
        return g.render()

    @cherrypy.expose
    def edit(self, type):
        if type == 'category':
            type = Category
        else:
           return
        fs = FieldSet(type)
        return fs.render()
