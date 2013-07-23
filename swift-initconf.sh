#! /usr/bin/env bash

# Generates an init script to allow swift services 
#  to start when the machine boots

cat > swift-init.conf <<EOF

# swift
#
# Starts everything swift can find a .conf file for.

description     "swift services"
author          "Stephen Tredger"

start on runlevel [2345]
stop on runlevel [016]

pre-start exec /usr/bin/swift-init all start

post-stop exec /usr/bin/swift-init all stop

EOF