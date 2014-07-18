from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/openderby'
db = SQLAlchemy(app)

from registration import Category, Car, HeatGenView
@app.route("/")
def hello():
    
    return "Hello World!"

admin = Admin(app, name="Registration", url='/registration')
admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Car, db.session))
admin.add_view(HeatGenView(name="Heats"))
#admin.add_view(ModelView(Heat, db.session))
