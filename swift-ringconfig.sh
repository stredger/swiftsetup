#! /usr/bin/env bash

# Create config files for each ring
#


cat > account-server.conf <<EOF
[DEFAULT]
bind_ip = 0.0.0.0
workers = 2
mount_check=True

[pipeline:main]
pipeline = account-server

[app:account-server]
use = egg:swift#account

[account-replicator]

[account-auditor]

[account-reaper]
EOF

cat > container-server.conf <<EOF
[DEFAULT]
bind_ip = 0.0.0.0
workers = 2
mount_check=True

[pipeline:main]
pipeline = container-server

[app:container-server]
use = egg:swift#container

[container-replicator]

[container-updater]

[container-auditor]

[container-sync]
EOF

cat > object-server.conf <<EOF
[DEFAULT]
bind_ip = 0.0.0.0
workers = 2
mount_check=True

[pipeline:main]
pipeline = object-server

[app:object-server]
use = egg:swift#object

[object-replicator]

[object-updater]

[object-auditor]
EOF