#! /usr/bin/env bash

# Author: Stephen Tredger, 2013

# Copyright (c) 2013 University of Victoria

# See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
# for the full license


# Create config files for each ring, worker nodes need these

cat > account-server.conf <<EOF
[DEFAULT]
bind_ip = 0.0.0.0
workers = 2
mount_check = true

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
mount_check = true

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
mount_check = true

[pipeline:main]
pipeline = object-server

[app:object-server]
use = egg:swift#object

[object-replicator]

[object-updater]

[object-auditor]
EOF