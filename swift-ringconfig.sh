#! /bin/bash


#STORAGE_LOCAL_NET_IP=155.98.39.50

if [ -z $STORAGE_LOCAL_NET_IP ]; then
    echo "
STORAGE_LOCAL_NET_IP not set! using 127.0.0.1 as default"
    STORAGE_LOCAL_NET_IP=127.0.0.1
fi

# Create config files for each ring
echo -n "Generating /etc/swift/account-server.conf... "
cat >/etc/swift/account-server.conf <<EOF
[DEFAULT]
bind_ip = $STORAGE_LOCAL_NET_IP
workers = 2

[pipeline:main]
pipeline = account-server

[app:account-server]
use = egg:swift#account

[account-replicator]

[account-auditor]

[account-reaper]
EOF
echo "Done!!"

echo -n "Generating /etc/swift/container-server.conf... "
cat >/etc/swift/container-server.conf <<EOF
[DEFAULT]
bind_ip = $STORAGE_LOCAL_NET_IP
workers = 2

[pipeline:main]
pipeline = container-server

[app:container-server]
use = egg:swift#container

[container-replicator]

[container-updater]

[container-auditor]

[container-sync]
EOF
echo "Done!!"

echo -n "Generating /etc/swift/object-server.conf... "
cat >/etc/swift/object-server.conf <<EOF
[DEFAULT]
bind_ip = $STORAGE_LOCAL_NET_IP
workers = 2

[pipeline:main]
pipeline = object-server

[app:object-server]
use = egg:swift#object

[object-replicator]

[object-updater]

[object-auditor]
EOF
echo "Done!!"