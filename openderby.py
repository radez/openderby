from flask import Flask
from flask import render_template
from flask.ext.cache import Cache
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView

# stackoverflow.com/questions/16469456/application-scope-variables-in-flask
class OpenDerby(Flask):
    def __init__(self, *args, **kwargs):
        super(OpenDerby, self).__init__(*args, **kwargs)
        self.current_category = 0
        self.current_heat = 0

app = OpenDerby(__name__)

# https://pythonhosted.org/Flask-Cache/
cache = Cache(app,config={'CACHE_TYPE': 'simple'})

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/openderby'
db = SQLAlchemy(app)

from registration import Category, Car, Heat, HeatGenView

@app.route("/")
@cache.cached(timeout=5)
def results():
    results = Heat.query.filter(Heat.time != None).order_by(Heat.category_id, Heat.id, Heat.lane)
    return render_template("results.html", results=results)

class CarModelView(ModelView):
    column_display_pk=True
    def __init__(self, model, session, name=None, category=None, endpoint=None, url=None, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

        super(CarModelView, self).__init__(model, session, name=name, category=category, endpoint=endpoint, url=url)


# Setup Registration admin
adminReg = Admin(app, name="Registration", url='/registration')
adminReg.add_view(ModelView(Category, db.session))
adminReg.add_view(CarModelView(Car, db.session))
adminReg.add_view(HeatGenView(name="Heats"))

class MyView(BaseView):
    #def is_accessible(self):
    #    return login.current_user.is_authenticated()
    pass

@app.route("/pit")
@cache.cached(timeout=5)
def pit():
    heats = Heat.query.filter_by(
                       category_id=app.current_category
                     ).filter(
                       Heat.id >= app.current_heat
                     ).order_by(Heat.id, Heat.lane)
    return render_template("pit.html", category=app.current_category,
                                       heat=app.current_heat, heats=heats)

@app.route("/status")
@app.route("/status/<cat>/<heat>")
def status(cat=None, heat=None):
    if cat and heat:
        app.current_category = cat
        app.current_heat = heat
    return render_template("status.html",
                           category = app.current_category,
                           heat = app.current_heat)
