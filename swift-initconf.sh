#! /usr/bin/env bash


# Author: Stephen Tredger, 2013

# Copyright (c) 2013 University of Victoria

# See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
# for the full license


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