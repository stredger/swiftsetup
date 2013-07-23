#! /usr/bin/env bash

# generates a proxy server config file
#  expects $user, $passwd, and $authtype to be defined

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


[filter:healthcheck]
use = egg:swift#healthcheck

[filter:cache]
use = egg:swift#memcache
memcache_servers = 0.0.0.0:11211
EOF
