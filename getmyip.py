""" 
Author: Stephen Tredger, 2013

Copyright (c) 2013 University of Victoria

See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
for the full license
"""

import socket
import sys


def getmyip(host="www.google.com"):
    """ Will get the ip of the current machine, 
    by connecting to a remote host"""

    conn = socket.create_connection((host, 80))
    ip = conn.getsockname()[0]
    conn.close()
    
    print ip
    return ip


def test_validip(host="www.google.com"):
    """ Checks if the IP of the current machine is a well formed
    IPv4 address, or IPv6 address """

    ip = getmyip(host)
    assert len(ip.split('.')) == 4 or len(ip.split(':')) == 8, "not a valid ip: "+ str(ip) 
    assert "localhost" not in ip, "ip is localhost"


if __name__ == "__main__":

    if (len(sys.argv) > 1):
        getmyip(sys.argv[1])
    else:
        getmyip()
