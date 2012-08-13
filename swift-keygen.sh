#! /bin/bash




if [ ${ISPROXY} ]; then
    echo -n "Generating /etc/swift/swift.conf... "

    cat >/etc/swift/swift.conf <<EOF
[swift-hash]
# random unique string that can never change (DO NOT LOSE)
swift_hash_path_suffix = `od -t x8 -N 8 -A n </dev/random`
EOF

    for node in ${STORENODES}; do
	scp /etc/swift/swift.conf ${scpuser}@${node}:~ # figure out how to copy these better
    done
else
    echo -n "Copying to /etc/swift/ swift.conf + *.rings.gz ..."
    # we are running as root! may want to set up a key!
    # or figure out a better way to get this to every node
    #scp $alphanode:/etc/swift/swift.conf /etc/swift
    #cp ~/swift-setup/swift.conf /etc/swift/
    #cp ~/*.ring.gz /etc/swift/
    cp ~/swift-setup/swiftage/* /etc/swift/
fi

echo "done!"
