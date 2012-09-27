#! /bin/bash

echo -n "Generating /etc/rsyncd.conf... "

if [ -z $STORAGE_LOCAL_NET_IP ]; then
    echo "
STORAGE_LOCAL_NET_IP not set! using 127.0.0.1 as default"
    STORAGE_LOCAL_NET_IP=127.0.0.1
fi

# these should be changed based on the mount point and how many cons you want (should be in envars)
fspath=/srv/node/
numconns=6

# create rsyncd config file
cat >/etc/rsyncd.conf <<EOF
uid = swift
gid = swift
log file = /var/log/rsyncd.log
pid file = /var/run/rsyncd.pid
address = $STORAGE_LOCAL_NET_IP

[account]
max connections = $numconns
path = $fspath
read only = false
lock file = /var/lock/account.lock

[container]
max connections = $numconns
path = $fspath
read only = false
lock file = /var/lock/container.lock

[object]
max connections = $numconns
path = $fspath
read only = false
lock file = /var/lock/object.lock
EOF

echo "Done!!"

# enable rsync in rsync config file (not the one we just generated)
perl -pi -e 's/RSYNC_ENABLE=false/RSYNC_ENABLE=true/' /etc/default/rsync

# start the rsync service    
service rsync start
