#! /bin/bash

# this must be sourced as we need these vars in our current shell!!


export PROXYNODE="alpha.multiswift.vikelab.emulab.net"

export STORENODES="beta-0.multiswift.vikelab.emulab.net beta-1.multiswift.vikelab.emulab.net beta-2.multiswift.vikelab.emulab.net beta-3.multiswift.vikelab.emulab.net beta-4.multiswift.vikelab.emulab.net beta-5.multiswift.vikelab.emulab.net beta-6.multiswift.vikelab.emulab.net beta-7.multiswift.vikelab.emulab.net"


# should be nodes ip addr?? Dont know how to uniquely id that...
sip=`ifconfig | grep -e "inet addr:.*Bcast" | cut -f2 -d \: | cut -f1 -d \  | tr -d ' ' | head -n 1`
export STORAGE_LOCAL_NET_IP=$sip
echo "Local ip addr = $sip"

# this should be the ip of the proxy node
pip=`host ${PROXYNODE} | awk /[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/ | cut -f4 -d \  | tr -d ' '`
export PROXY_LOCAL_NET_IP=$pip
echo "Proxy ip addr = $pip"

if [ $sip == $pip ]; then
    export ISPROXY=1
fi

# for actual external device
#export DEVICE=sda4

# for local loopback
export DEVICE=swift-disk

# should be 1 for multinode setup, but must be a list
export ZONESPERNODE="1"

export scpuser=stredger