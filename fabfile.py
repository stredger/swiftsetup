
import sys, os
from fabric.api import *
from settings import *

# Before you run:
#  make sure all the machines are in the correct lists and the ip's 
#  of the workers are in the correst list as well.
#
#  Most of the config files and the rings are built on the local
#  machine. make sure swift is installed there!
#
#  Swift requires an xfs partition to use. If asked this will set up 500GB
#  a loopback device and mount it at /srv/node/swiftfs. 
#  (note this will NOT fail if you have less than 500GB available!!)
#
#  Be sure to check the filesystem size, mountpoint and such!
#  The mountpoint is used in the rsyncd.config file as well as setting up the 
#  loopback device


# Usefull stuff!
#
# To run a default full install: fab swift_install
#
# To distribute rings: fab distribute_rings
#
# To restart all swift processes: fab swift_restart


# TODO:
#  auto back up swift.config and builders! (place into swift repo?)
#  have boss .builder dir?
#  have temp script dir other than /tmp/?
#  make some vars global??
#  make scripts output to local dir so we can define where all this gets done

env.roledefs = {
    'swift-cluster':swift_cluster,
    'swift-workers':swift_workers,
    'swift-proxies':swift_proxies,
    'swift-object-expirer':swift_object_exp,
    'boss':boss,
    'loopback-machines':loopback_machines
}

env.key_filename = keyfile
env.password = passwd



def get_script_path(f):
    return os.path.join(swift_script_dir, f)



# Creates the ring files which are the heart (brain?) of the swift repo
#  as they are the mapping of where files are to be placed!
# The ring files: "account.ring.gz", "container.ring.gz", "object.ring.gz"
#  must be present in all machines in /etc/swift/ with the user swift having
#  all premissions on them
def cluster_rings():
    execute(create_rings)
    execute(get_rings)
    execute(distribute_rings)


@runs_once
@roles('boss')
def create_rings():

    partpower = 18 # how large each partition is, 2^this_num
    repfactor = 3 # replication factor
    movetime = 1 # min hours between partition move
    weight = 100
    builders = ['account.builder', 'container.builder', 'object.builder']
    ports = ['6002', '6001', '6000']

    if len(swift_workers) < repfactor:
        print "we are tring to have %d replications on %d swift workers!" % (repfactor, len(swift_worker))
        sys.exit()

    worker_machines = [machines[m] for m in swift_workers]

    # maybe have a place to cd to and build these files?
    for b in builders:
        run('swift-ring-builder %s create %s %s %s' % (b, partpower, repfactor, movetime))

    zone = 0 # should be unique for each ip
    for m in worker_machines:
        ip = m.ip
        dev = os.path.split(m.mntpt)[1]
        # make an entry for machine m in each builder b at port p 
        for b, p in [(builders[n],ports[n]) for n in xrange(len(builders))]:
            run('swift-ring-builder %s add z%s-%s:%s/%s %s' % (b, zone, ip, p, dev, weight))
        zone += 1

    # verify the rings
    for b in builders:
        run('swift-ring-builder %s' % b)

    # distribute the partitions evenly across the nodes
    for b in builders:
        run('swift-ring-builder %s rebalance' % b)


@runs_once
@roles('boss')
def get_rings():
    ring_suff = '*.ring.gz'
    builder_suff = '*.builder'

    get(ring_suff, '/tmp/')
    get(builder_suff, '/tmp/')


@parallel
@roles('swift-cluster')
def distribute_rings():
    
    rings = ["account.ring.gz", "container.ring.gz", "object.ring.gz"]

    sudo('mkdir -p /etc/swift')
    sudo('chmod a+w /etc/swift')
    for ring in rings:
        put(os.path.join('/tmp/',ring), os.path.join('/etc/swift/',ring), use_sudo=True)
    sudo('chown -R swift:swift /etc/swift')


@parallel
@roles('boss')
def distribute_builders():
    pass



@parallel
@roles('swift-cluster')
def clean_rings():
   
    sudo('rm -f /etc/swift/*.ring.gz')




# Configures the swift proxy
#  generates proxy-server.conf config file and distributes it to all the proxies
#  Also sets up the memcached daemon
def proxy_config():
    execute(local_proxy)
    execute(cluster_proxy)


@runs_once
def local_proxy():
    script = get_script_path('swift-pconfgen.sh')
    local('export user=%s && export passwd=%s && %s' % (swift_user, swift_passwd, script))


@parallel
@roles('swift-proxies')
def cluster_proxy():

    machine = machines[env.host_string]
    ip = machine.ip

    sudo('mkdir -p /etc/swift')
    sudo('chmod a+w /etc/swift')
    put('/tmp/proxy-server.conf', '/etc/swift/proxy-server.conf')
   
    # get desired ip and put into config file 
    sudo('perl -pi -e "s/0.0.0.0/%s/" /etc/swift/proxy-server.conf' % (ip))
    sudo('perl -pi -e "s/-l 127.0.0.1/-l 0.0.0.0/" /etc/memcached.conf')
    sudo('service memcached restart')
    sudo('chown -R swift:swift /etc/swift')
    sudo('swift-init proxy start')



def storage_config():
    execute(storage_config_gen)
    execute(rsync_config_gen)
    execute(cluster_object_exp)
    execute(cluster_storage)


@parallel
@roles('swift-workers')
def rsync_config_gen():

    machine = machines[env.host_string]
    fs_path = os.path.dirname(machine.mntpt)
    ip = machine.ip

    put(get_script_path('swift-rsync.sh'), '/tmp')
    sudo('chmod +x /tmp/swift-rsync.sh')
    run('export fspath=%s; export maxconn=%s; /tmp/swift-rsync.sh' % (fs_path, machine.rsync_maxconn))
    sudo('mv /tmp/rsyncd.conf /etc/')
    # enable the rsync daemon
    sudo('perl -pi -e "s/RSYNC_ENABLE=false/RSYNC_ENABLE=true/" /etc/default/rsync')
    sudo('perl -pi -e "s/0.0.0.0/%s/" /etc/rsyncd.conf' % (ip))
    sudo('service rsync start')


@runs_once
def storage_config_gen():

    local(get_script_path('swift-ringconfig.sh'))
    local(get_script_path('swift-objexpconfig.sh'))



@parallel
@roles('swift-workers')
def cluster_storage():

    machine = machines[env.host_string]
    swiftfs_path = machine.mntpt
    ip = machine.ip

    sudo('rm -rf /etc/swift/account-server.conf /etc/swift/container-server.conf /etc/swift/object-server.conf')

    # set up ring config files
    sudo('mkdir -p /etc/swift')
    sudo('chmod a+w /etc/swift')
    put('/tmp/account-server.conf', '/etc/swift/')
    put('/tmp/container-server.conf', '/etc/swift/')
    put('/tmp/object-server.conf', '/etc/swift/')

    sudo('perl -pi -e "s/0.0.0.0/%s/" /etc/swift/*-server.conf' % (ip))

    sudo('chown swift:swift %s' % swiftfs_path)
    sudo('chown -R swift:swift /etc/swift')
    sudo('swift-init all start') # starts every swift process that has a config file



@parallel
@roles('swift-object-expirer')
def cluster_object_exp():

    machine = machines[env.host_string]
    swiftfs_path = machine.mntpt

    put('/tmp/object-expirer.conf', '/etc/swift')

    sudo('chown -R swift:swift /etc/swift')
    sudo('swift-init object-expirer start')




# Creates a swift cluster key, and distributes it to each node
#  this key must be present on all nodes in the cluster!!
def cluster_keygen():

    execute(local_keygen)
    execute(distribute_key)


@runs_once
def local_keygen():

    # we probably want to back up the file this generates somewhere!
    local(get_script_path('swift-keygen.sh'))


@parallel
@roles('swift-cluster')
def distribute_key():

    sudo('mkdir -p /etc/swift')
    sudo('chmod a+w /etc/swift')
    put('/tmp/swift.conf', '/etc/swift/swift.conf')
    sudo('chown -R swift:swift /etc/swift')
    



# Sets up a 'machine.dev_size' size loopback filesystem at 'machine.mntpt'
#  Makes the actual loopback file in 'machine.dev_path' called 'machine.dev'
#  The mountpoint and disksize can be changed, but 
@parallel
@roles('loopback-machines')
def setup_loop_device():

    machine = machines[env.host_string]
    devpath = os.path.join(machine.dev_path, machine.dev)
    disksize = machine.dev_size
    mntpt = machine.mntpt

    sudo('mkdir -p %s' % (machine.dev_path))
    sudo('dd if=/dev/zero of=%s bs=1024 count=0 seek=%s' % (devpath, disksize))
    sudo('mkfs.xfs -i size=1024 %s' % (devpath))
    sudo('echo "%s %s xfs loop,noatime,nodiratime,nobarrier,logbufs=8 0 0" >> /etc/fstab' % (devpath, mntpt))

    sudo('mkdir -p %s' % (mntpt))
    sudo('mount %s' % (mntpt))
    sudo('chown -R swift:swift %s' % (mntpt))



def setup_logging():
    execute(log_config_gen)
    execute(cluster_logging)


@runs_once
def log_config_gen():
    local(get_script_path('swift-logging.sh'))


@parallel
@roles('swift-cluster')
def cluster_logging():
    put('/tmp/swiftlog.conf', '/etc/rsyslog.d/swift.conf', use_sudo=True)
    put('/tmp/swiftrotate.conf', '/etc/logrotate.d/swift', use_sudo=True)
    sudo('chown root:root /etc/rsyslog.d/swift.conf')
    sudo('chown root:root /etc/logrotate.d/swift')
    sudo('service rsyslog restart')



# installs dependencies for our swift deployment
@parallel
@roles('swift-cluster')
def install_swift_deps():

    with settings(warn_only=True):
        sudo('apt-get update')
    sudo('apt-get -y --force-yes install swift openssh-server swift-proxy memcached swift-account swift-container swift-object curl gcc git-core python-configobj python-coverage python-dev python-nose python-setuptools python-simplejson python-xattr sqlite3 xfsprogs python-webob python-eventlet python-greenlet python-pastedeploy python-netifaces')

    sudo('mkdir -p /etc/swift')
    sudo('chown swift:swift /etc/swift')

    sudo('mkdir -p /var/cache/swift')
    sudo('chown swift:swift /var/cache/swift')



# This will create the users swift and memcache, 
#  these users should be created when swift and memcached
#  are installed. I recommend you reinstall swift and memcached
#  if the users are not present before running this function
def create_users():
    execute(create_swift_user)
    execute(create_memcached_user)

@parallel
@roles('swift-cluster')
def create_swift_user():
    sudo('useradd -r -s /bin/false swift')

@parallel
@roles('swift-cluster')
def create_memcached_user():
    sudo('useradd -r -s /bin/false memcache ')



@parallel
@roles('swift-cluster')
def clean_files(files="proxy-server.conf"):
    sudo('rm -rf '+files)





@parallel
@roles('swift-cluster')
def check_login_shell():
    sh = run('echo $SHELL')
    if "bash" not in sh:
        abort("The installation will not work unless bash is our default shell!!")
    


# restart all swift processes that have a config file
#  in /etc/swift
@parallel
@roles('swift-cluster')
def swift_restart():
    sudo('swift-init all restart')


@parallel
@roles('swift-cluster')
def swift_stop():
    sudo('swift-init all stop')


def get_os_type():

    put(get_script_path('getmyos.py'), '/tmp/getmyos.py')


@roles('boss')
def test_proxies():
    for proxy in swift_proxies:
        run('swift -A http://%s:8080/auth/v1.0 -U system:%s -K %s stat' % (proxy, swift_user, swift_passwd))


@roles('swift-cluster')
def test_ips():
    put(get_script_path('getmyip.py'), '/tmp/')
    run('python /tmp/getmyip.py')
    

@roles('swift-proxies')
def test_memcached():
    put(get_script_path('getmyip.py'), '/tmp/')
    put(get_script_path('memcachedtest.py'), '/tmp/')
    run('python /tmp/memcachedtest.py')





# this is the main install function, it can be run multiple times
#  but the device setup should only be run once (and only if we 
#  want to use a loopback device).
def swift_install():
    
    print "\n\n==========Beginning swift installation==========="
    print "machines in cluster:", swift_cluster
    print "proxy machines:", swift_proxies
    print "worker machines:", swift_workers
    print "setup loopback file system on:", loopback_machines
    print "\n\n"

    if (check_shell):
        execute(check_login_shell)
    execute(install_swift_deps)
    execute(setup_loop_device)
    execute(cluster_keygen)
    execute(cluster_rings)
    execute(proxy_config)
    execute(storage_config)

    print "\n\n\t Finished swift installation!"
    print "make sure to back up the *.builder files! \n\n"
