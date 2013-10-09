""" 
Author: Stephen Tredger, 2013

Copyright (c) 2013 University of Victoria

See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
for the full license
"""


import swift.common.memcached as memc
from getmyip import *


def test_memcached():
	""" Checks if memcached is running and can store,
	and retreve tokens """

    ip = getmyip()

    m = memc.MemcacheRing([ip+':11211'])
    token = m.get('AUTH_/user/system:gis')

    print "XAuthToken:", token
    print "", m.get("AUTH_/token/" + str(token))


if __name__ == "__main__":
    test_memcached()
