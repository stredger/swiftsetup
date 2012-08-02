#! /bin/bash

# pretty much just following: 
# http://docs.openstack.org/developer/swift/howto_installmultinode.html

scriptdir=~/swift

source ${scriptdir}/swift-envars.sh

# run this as root!!!
if [ "`whoami`" != "root" ]; then
    echo "Must run with root permissions!"
    exit
fi

if [ -z $STORAGE_LOCAL_NET_IP ]; then
    echo "please set STORAGE_LOCAL_NET_IP!"
    echo "see swift-envars.sh for details"
    exit
fi

if [ -z $PROXY_LOCAL_NET_IP ]; then
    echo "please set PROXY_LOCAL_NET_IP!"
    echo "see swift-envars.sh for details"
    exit
fi

if [ -z $DEVICE ]; then
    echo "please set DEVICE!"
    echo "see swift-envars.sh for details"
    exit
fi


swift-housekeep()
{
    echo "======================= Start Setup ========================="

    # config stuff
    mkdir -p /etc/swift
    chown -R swift:swift /etc/swift/

    # make unique string key, should be same for all nodes
    # generates /etc/swift/swift.conf
    source ${scriptdir}/swift-keygen.sh
    
    echo "======================= Done Setup ========================="
}


proxy-setup() 
{
    echo "======================= Start Proxy ========================="

    partpower=18 # 2^(the value) that the partition will be sized to.
    replfactor=1 # replication factor for objects
    partmovetime=1 # number of hours to restrict moving a partition more than once
    
    numzones="1" # list of storage devs/node nums (should be 1 to n)

    cd /etc/swift
    openssl req -new -x509 -nodes -out cert.crt -keyout cert.key<<EOF
CA
British Columbia
.
UVic
.
.
.
EOF

    mv cert* /etc/swift

    #memfile="/etc/memcached.conf"
    #cp ${memfile} ${memfile}.back
    #cat ${memfile} | sed 's:127.0.0.1:${PROXY_LOCAL_NET_IP}:' > ${memfile}
    perl -pi -e "s/-l 127.0.0.1/-l $PROXY_LOCAL_NET_IP/" /etc/memcached.conf


    service memcached restart

    # Should generate /etc/swift/proxy-server.conf
    source ${scriptdir}/swift-pconfgen.sh

    cd /etc/swift
    swift-ring-builder account.builder create ${partpower} ${replfactor} ${partmovetime}
    swift-ring-builder container.builder create ${partpower} ${replfactor} ${partmovetime}
    swift-ring-builder object.builder create ${partpower} ${replfactor} ${partmovetime}

    dev=sdb1
    weight=100
    #for each storage device in each node, add entries to the ring
    for zone in ${numzones}; do
	swift-ring-builder account.builder add z${zone}-${STORAGE_LOCAL_NET_IP}:6002/${dev} ${weight}
	swift-ring-builder container.builder add z${zone}-${STORAGE_LOCAL_NET_IP}:6001/${dev} ${weight}
	swift-ring-builder object.builder add z${zone}-${STORAGE_LOCAL_NET_IP}:6000/${dev} ${weight}
    done

    # verify the rings
    swift-ring-builder account.builder
    swift-ring-builder container.builder
    swift-ring-builder object.builder

    # rebalance rings
    swift-ring-builder account.builder rebalance
    swift-ring-builder container.builder rebalance
    swift-ring-builder object.builder rebalance
    wait $!

    # move to config (should be in for every node in cluster)
    mv *.builder /etc/swift
    mv *.ring.gz /etc/swift
    
    chown -R swift:swift /etc/swift

    # start proxy server
    swift-init proxy start

    echo "======================= Done Proxy ========================="
}


swift-setup()
{
    echo "======================= Start Store ========================="

    # generate config file ans start rsync service
    source ${scriptdir}/swift-rsync.sh

    # generate config files for storage services
    source ${scriptdir}/swift-ringconfig.sh

    source ${scriptdir}/swift-objexpconfig.sh

    # one more time for good luck!
    chown -R swift:swift /etc/swift

    swift-init all start

    echo "======================= Done Store ========================="
}



device-setup()
{
    echo "======================= Start Dev ========================="

    dev=${DEVICE}
    mntpt=/srv/node/sdb1
    numzones="1"
    mkdir -p /srv

    if [ ${dev} == "sda4" ]; then

	devpath=/dev/${dev}
	fdisk /dev/sda<<EOF
t
4
83
w
EOF
	mkfs.xfs -i size=1024 ${devpath}
	echo "${devpath} $mntpt xfs noatime,nodiratime,nobarrier,logbufs=8 0 0" >> /etc/fstab

    elif [ ${dev} == "swift-disk" ]; then # loopback into file
	devpath=/srv/${dev}
	dd if=/dev/zero of=${devpath} bs=1024 count=0 seek=1000000
   
	mkfs.xfs -i size=1024 ${devpath}
	echo "${devpath} $mntpt xfs loop,noatime,nodiratime,nobarrier,logbufs=8 0 0" >> /etc/fstab

    else # dont really know what to do!
	echo "-----------Unkown disk type!!----------------"
	echo "-----------Failed to mount disk!!----------------"
	return
    fi

    mkdir -p $mntpt
    mount $mntpt

    # for zone in ${numzones}; do
    # 	mkdir ${mntpt}/${zone}
    # done

    chown -R swift:swift $mntpt
    # mkdir /srv

    # for zone in ${numzones}; do
    # 	ln -s ${mntpt}/${zone} /srv/${zone}
    # 	mkdir -p /srv/${zone}/node/sdb${zone}
    # done    

    # mkdir -p /etc/swift/object-server /etc/swift/container-server /etc/swift/account-server  /var/run/swift

    #chown -R swift:swift /etc/swift /srv/[${zone}-${numzones}]/ /var/run/swift

    # rcfile="/etc/rc.local"
    # # may have to replace exit 0???
    # # perl -pi -e "s/exit 0//" $rcfile
    # echo "mkdir /var/cache/swift /var/cache/swift2 /var/cache/swift3 /var/cache/swift4" >> $rcfile
    # echo "chown swift:swift /var/cache/swift*" >> $rcfile
    # echo "mkdir /var/run/swift" >> $rcfile
    # echo "chown swift:swift /var/run/swift" >> $rcfile

    echo "======================= Done Dev ========================="
}


install-deps() {
    source ./swift-depinstall.sh
}


all()
{
    install-deps
    device-setup
    swift-housekeep
    proxy-setup
    swift-setup
}


if [ -z ${1} ]; then
    all
fi

while [ $1 ]; do
    case "${1}" in

	"all")
	    all
	    ;;

	"all-d")
	    device-setup
	    swift-housekeep
	    proxy-setup
	    swift-setup
	    ;;

	"all-dd")
	    swift-housekeep
	    proxy-setup
	    swift-setup
	    ;;

	"deps")
	    install-deps
	    ;;

	"dev")
	    device-setup
	    ;;

	"init")
	    swift-housekeep
	    ;;

	"proxy")
	    proxy-setup
	    ;;
	
	"store")
	    swift-setup
	    ;;

	*)
	    echo "invalid option ${1}"
	    ;;
    esac
    shift
done