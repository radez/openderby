from openderby.models import app, Category, Car
print "Destroying database"
app.db.drop_all()
print "Recreating database"
app.db.create_all()

app.db.session.commit()
print "Complete"
