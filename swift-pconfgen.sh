#! /bin/bash

echo -n "Generating /etc/swift/proxy-server.conf... "

if [ -z $PROXY_LOCAL_NET_IP ]; then
    echo "
PROXY_LOCAL_NET_IP not set! using 127.0.0.1 as default"
    PROXY_LOCAL_NET_IP=127.0.0.1
fi

cat >/etc/swift/proxy-server.conf <<EOF
[DEFAULT]
#cert_file = /etc/swift/cert.crt
#key_file = /etc/swift/cert.key
bind_port = 8080
workers = 8
user = swift

[pipeline:main]
pipeline = healthcheck cache tempauth proxy-server

[app:proxy-server]
use = egg:swift#proxy
allow_account_management = true
account_autocreate = true

[filter:tempauth]
use = egg:swift#tempauth
user_system_root = testpass .admin http://$PROXY_LOCAL_NET_IP:8080/v1/AUTH_system

[filter:healthcheck]
use = egg:swift#healthcheck

[filter:cache]
use = egg:swift#memcache
memcache_servers = $PROXY_LOCAL_NET_IP:11211
EOF

echo "Done!!"