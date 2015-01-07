from flask import Flask
from flask import render_template
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/openderby'
db = SQLAlchemy(app)

from registration import Category, Car, HeatGenView
@app.route("/")
def menu():
    
    return "use /registration or /pit"

# Setup Registration admin
adminReg = Admin(app, name="Registration", url='/registration')
adminReg.add_view(ModelView(Category, db.session))
adminReg.add_view(ModelView(Car, db.session))
adminReg.add_view(HeatGenView(name="Heats"))

class MyView(BaseView):
    #def is_accessible(self):
    #    return login.current_user.is_authenticated()

    pass


@app.route("/pit")
def pit():
    return render_template("pit.html")
