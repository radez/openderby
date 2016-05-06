from random import randint
from openderby.models import Category, Car
from openderby.registration import app

print "Seeding database"

# creating categories
print "Creating Categories"
kids = Category(name="Ranger Kids")
discovery = Category(name="Discovery Rangers")
adventure = Category(name="Adventure Rangers")
app.db.session.add(kids)
app.db.session.add(discovery)
app.db.session.add(adventure)

# creating cars
print "Creating Cars"

car_ct = 1
for c in [kids, discovery, adventure]:
    for i in range(1, randint(7,13)):
        car = Car(name="Car %i" % car_ct, driver="Driver %i" % car_ct, category=c)
        app.db.session.add(car)
        car_ct += 1

print "Commiting"
app.db.session.commit()
print "Complete"
