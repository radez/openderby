from flask import Flask
from flask import render_template
#from flask.ext.cache import Cache
from flask_sqlalchemy import SQLAlchemy

# stackoverflow.com/questions/16469456/application-scope-variables-in-flask
class OpenDerby(Flask):
    def __init__(self, *args, **kwargs):
        super(OpenDerby, self).__init__(*args, **kwargs)
        #self.current_category = 0
        #self.current_heat = 0
        self.db = SQLAlchemy(self)

app = OpenDerby(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/openderby'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'super secret key'
rankings_key = 'rankings_key'

# https://pythonhosted.org/Flask-Cache/
#cache = Cache(app,config={'CACHE_TYPE': 'simple'})
