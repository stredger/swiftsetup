#! /bin/bash

echo -n "Generating /etc/rsyncd.conf... "

if [ -z $STORAGE_LOCAL_NET_IP ]; then
    echo "
STORAGE_LOCAL_NET_IP not set! using 127.0.0.1 as default"
    STORAGE_LOCAL_NET_IP=127.0.0.1
fi

# this should be changed based on the mount point and stuff (maybe put in envars?)
fspath=/srv/node/sdb1/

# note: using external ip addr causes the rsync daemon to break!!

# create rsyncd config file
cat >/etc/rsyncd.conf <<EOF
uid = swift
gid = swift
log file = /var/log/rsyncd.log
pid file = /var/run/rsyncd.pid
#address = $STORAGE_LOCAL_NET_IP
address = 127.0.0.1

[account]
max connections = 2
path = $fspath
read only = false
lock file = /var/lock/account.lock

[container]
max connections = 2
path = $fspath
read only = false
lock file = /var/lock/container.lock

[object]
max connections = 2
path = $fspath
read only = false
lock file = /var/lock/object.lock
EOF

echo "Done!!"

# enable rsync in rsync config file (not the one we just generated)
perl -pi -e 's/RSYNC_ENABLE=false/RSYNC_ENABLE=true/' /etc/default/rsync

# start the rsync service    
service rsync start
