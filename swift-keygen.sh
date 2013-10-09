#! /usr/bin/env bash

# Author: Stephen Tredger, 2013

# Copyright (c) 2013 University of Victoria

# See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
# for the full license


# generates a key for a swift cluster to use.
#  This key must be in the file /etc/swift/swift.conf
#  and must be presenton and identical to
#  all nodes in the same swift cluster.

cat > swift.conf <<EOF
[swift-hash]
# random unique string that can never change (DO NOT LOSE)
swift_hash_path_suffix = `od -t x8 -N 8 -A n </dev/random`
EOF
