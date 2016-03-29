from math import ceil
from random import randrange
from openderby import db, Category, Car, Heat

lanes = 6
warning = '  *** HEAT LANE MISMATCH ***'

# Do all Categories
for category in Category.query.all():
    cat_car_cnt = Car.query.filter_by(category=category).count()
    heat_cnt = int(ceil(float(cat_car_cnt) / float(lanes))) * lanes
    print "Starting Category: %s - %i cars - %i heats" % (category, cat_car_cnt, heat_cnt)
    for heat_id in range(1, heat_cnt+1):
        print "Generating Heat %i" % heat_id
        used_lanes = Heat.query.filter_by(id=heat_id, category=category).all()
        used_lanes = map(lambda x: x.lane, used_lanes)
#        print used_lanes
        for lane in range(1, lanes+1):
            if lane in used_lanes:
                break
            cars_q = Car.query.filter_by(category=category)\
                              .outerjoin(Heat, db.and_(Heat.car_id==Car.id, db.or_(Heat.id == heat_id, Heat.lane == lane))).filter(Heat.id.is_(None)).filter(Heat.lane.is_(None))
            #print str(cars_q)
            cars = cars_q.all()
            car_cnt = len(cars)
            if car_cnt:
                car_index = randrange(0, car_cnt)
                heat = Heat(id=heat_id, category=category, lane=lane, car=cars[car_index])
                db.session.add(heat) 
                db.session.commit()
    print "\nVerifying Cars"
    cars = db.session.query(Car, db.func.count(Car.id).label('heats'))\
                         .filter_by(category=category).group_by(Car.id).join(Heat).all()
    for car in cars:
        warn = ''
        if car[1] != lanes:
            warn = warning
        print "%s: %s Heats%s" % (car[0], car[1], warn)
    print "\n"
print "Complete"
