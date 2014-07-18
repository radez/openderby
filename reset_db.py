from openderby import db
from registration import Category, Car
print "Destroying database"
db.drop_all()
print "Recreating database"
db.create_all()
print "Seeding database"

# creating categories
kids = Category(name="Ranger Kids")
discovery = Category(name="Discovery Rangers")
adventure = Category(name="Adventure Rangers")
db.session.add(kids)
db.session.add(discovery)
db.session.add(adventure)

# creating cars
car1 = Car(name="Car 1", driver="Driver 1", category=kids)
car2 = Car(name="Car 2", driver="Driver 2", category=kids)
car3 = Car(name="Car 3", driver="Driver 3", category=kids)
car4 = Car(name="Car 4", driver="Driver 4", category=kids)
car5 = Car(name="Car 5", driver="Driver 5", category=kids)
car6 = Car(name="Car 6", driver="Driver 6", category=kids)
car7 = Car(name="Car 7", driver="Driver 7", category=kids)
car8 = Car(name="Car 8", driver="Driver 8", category=kids)
car9 = Car(name="Car 9", driver="Driver 9", category=kids)

db.session.add(car1)
db.session.add(car2)
db.session.add(car3)
db.session.add(car4)
db.session.add(car5)
db.session.add(car6)
db.session.add(car7)
db.session.add(car8)
db.session.add(car9)

db.session.commit()
print "Complete"
