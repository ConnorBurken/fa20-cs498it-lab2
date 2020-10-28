import db_util

# db_util.insert_record('room_01', 'air_sensor', 125)

results = db_util.query_record('room_01', 1603822678180, 1603822985890)
print(results)
