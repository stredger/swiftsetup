#! /usr/bin/env bash

# Author: Stephen Tredger, 2013

# Copyright (c) 2013 University of Victoria

# See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
# for the full license


# generates a proxy server config file
#  expects $user, $passwd, and $authtype to be defined
#  in the current shell environment

#TODO: check that the vars are acutally set!

cat > proxy-server.conf <<EOF
[DEFAULT]
bind_port = 8080
workers = 8
user = swift

[pipeline:main]
pipeline = healthcheck cache ${authtype} proxy-server

[app:proxy-server]
use = egg:swift#proxy
allow_account_management = true
account_autocreate = true

# only one of tempauth or swauth should be used 
[filter:tempauth]
use = egg:swift#tempauth
user_system_${user} = ${passwd} .admin

[filter:swauth]
use = egg:swauth#swauth
set log_name = swauth
super_admin_key = ${passwd}
default_swift_cluster = local#http://PUBIP:8080/v1#http://127.0.0.1:8080/v1

[filter:healthcheck]
use = egg:swift#healthcheck

[filter:cache]
use = egg:swift#memcache
memcache_servers = 0.0.0.0:11211
EOF
