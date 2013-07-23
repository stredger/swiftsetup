#! /usr/bin/env bash

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