import redis

rc = redis.Redis()
for item in ['room_*']:
    for key in rc.keys(item):
        print 'deleting %s'%key
        rc.delete(key)
