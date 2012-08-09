import swift.common.memcached as memc

m = memc.MemcacheRing(['127.0.0.1:11211'])
token = m.get('AUTH_/user/system:root')

print "XAuthToken:", token
print "", m.get("AUTH_/token/" + str(token))

