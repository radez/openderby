from registration import app

from flask.ext.sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

from flask.ext.admin import Admin, BaseView, expose
from flask.ext.admin.contrib.sqla import ModelView


class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(120))

    def __init__(self, name=None, description=''):
        self.name = name
        self.description = description

    def __repr__(self):
        return self.name

class Car(db.Model):
    __tablename__ = 'car'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    driver = db.Column(db.String(80))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', foreign_keys=[category_id])
               #backref=db.backref('car', lazy='dynamic'))
    weight = db.Column(db.Float)

    def __repr__(self):
        return self.name

class Heat(db.Model):    
    __tablename__ = 'heat'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), primary_key=True)
    category = db.relationship('Category')
    lane = db.Column(db.Integer, primary_key=True)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    car = db.relationship('Car')
          #backref=db.backref('car', lazy='dynamic'))
    time = db.Column(db.Float)

class CarModelView(ModelView):
    column_display_pk=True
    def __init__(self, model, session, name=None, category=None, endpoint=None, url=None, **kwargs):
        for k, v in kwargs.iteritems():
            setattr(self, k, v)

        super(CarModelView, self).__init__(model, session, name=name, category=category, endpoint=endpoint, url=url)

class HeatGenView(BaseView):
    @expose('/')
    def index(self):
        heats = Heat.query.order_by('category_id', 'id', 'lane').all()
        cars = db.session.query(Car, db.func.count(Car.id).label('heats'))\
                         .group_by(Car.id).join(Heat).all()
        return self.render('index.html', heats=heats, cars=cars)

# Setup Registration admin
adminReg = Admin(app, name="Registration", url='/')
adminReg.add_view(ModelView(Category, db.session))
adminReg.add_view(CarModelView(Car, db.session))
adminReg.add_view(HeatGenView(name="Heats"))
