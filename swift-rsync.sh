#! /usr/bin/env bash

# Author: Stephen Tredger, 2013

# Copyright (c) 2013 University of Victoria

# See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
# for the full license


# create rsyncd config file

cat > rsyncd.conf <<EOF
uid = swift
gid = swift
log file = /var/log/rsyncd.log
pid file = /var/run/rsyncd.pid
address = 0.0.0.0

[account]
max connections = MAXCONN
path = SWIFTFSPATH
read only = false
lock file = /var/lock/account.lock

[container]
max connections = MAXCONN
path = SWIFTFSPATH
read only = false
lock file = /var/lock/container.lock

[object]
max connections = MAXCONN
path = SWIFTFSPATH
read only = false
lock file = /var/lock/object.lock
EOF