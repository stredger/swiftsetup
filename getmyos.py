""" 
Author: Stephen Tredger, 2013

Copyright (c) 2013 University of Victoria

See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
for the full license
"""

import platform

# A list of the os types we can expect. Don't actually use this as
#  I fairly certain this doesn't cover everything platform.system()
#  can return. more of just a reference 
# os_types = ['Linux', 'Darwin', 'Windows', 'Java']

os_t = platform.system()

if 'Linux' in os_t:
    dist = platform.linux_distribution()
    os_t = dist[0]

print os_t
