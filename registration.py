from openderby import db

from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(120))

    def __init__(self, name=None, description=''):
        self.name = name
        self.description = description

    def __repr__(self):
        return self.name

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    driver = db.Column(db.String(80))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category')
               #backref=db.backref('car', lazy='dynamic'))

    def __repr__(self):
        return self.name

class Heat(db.Model):    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer, db.ForeignKey('category.id'))
    lane = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    car = db.relationship('Car')
          #backref=db.backref('car', lazy='dynamic'))

class HeatGenView(BaseView):
    @expose('/')
    def index(self):
        heats = Heat.query.order_by('id', 'lane').all()
        cars = db.session.query(Car, db.func.count(Car.id).label('heats'))\
                         .group_by(Car.id).join(Heat).all()
        return self.render('index.html', heats=heats, cars=cars)

