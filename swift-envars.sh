#! /bin/bash

# this must be sourced as we need these vars in our current shell!!

ip=`ifconfig | grep -e "inet addr:.*Bcast" | cut -f2 -d \: | cut -f1 -d \ `

export STORAGE_LOCAL_NET_IP=$ip
export PROXY_LOCAL_NET_IP=$ip

# for actual external device
#export DEVICE=sda4

# for local loopback
export DEVICE=swift-disk

export NUMZONES="1"