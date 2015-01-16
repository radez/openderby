from random import randint
from openderby import db
from registration import Category, Car

print "Seeding database"

# creating categories
print "Creating Categories"
kids = Category(name="Ranger Kids")
discovery = Category(name="Discovery Rangers")
adventure = Category(name="Adventure Rangers")
db.session.add(kids)
db.session.add(discovery)
db.session.add(adventure)

# creating cars
print "Creating Cars"

car_ct = 1
for c in [kids, discovery, adventure]:
    for i in range(1, randint(7,13)):
        car = Car(name="Car %i" % car_ct, driver="Driver %i" % car_ct, category=c)
        db.session.add(car)
        car_ct += 1

print "Commiting"
db.session.commit()
print "Complete"