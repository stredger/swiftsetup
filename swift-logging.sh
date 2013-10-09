#! /usr/bin/env bash

# Author: Stephen Tredger, 2013

# Copyright (c) 2013 University of Victoria

# See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
# for the full license


# Generates config files for rsyslog and logrotate. These will
#  cause swift to log to /etc/swift/swift.log, compressing old logs daily
#  and keeping only one compressed copy 

cat > swiftlog.conf <<EOF
# Swift stuff
#
local0.*			/etc/swift/swift.log
EOF

cat > swiftrotate.conf <<EOF
/etc/swift/swift.log 
{
    rotate 1
    daily
    missingok
    compress
    sharedscripts
    postrotate
        invoke-rc.d rsyslog reload >/dev/null 2>&1 || true
    endscript
}
EOF