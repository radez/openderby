from openderby.models import db, Category, Car
print "Destroying database"
db.drop_all()
print "Recreating database"
db.create_all()

db.session.commit()
print "Complete"
