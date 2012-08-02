#! /bin/bash

echo -n "Generating /etc/swift/swift.conf... "

cat >/etc/swift/swift.conf <<EOF
[swift-hash]
# random unique string that can never change (DO NOT LOSE)
swift_hash_path_suffix = `od -t x8 -N 8 -A n </dev/random`
EOF

echo "done!"