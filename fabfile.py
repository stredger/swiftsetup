
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

try:
    if keyfile: env.key_filename = keyfile
    if passwd: env.password = passwd
except NameError:
    pass


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
    region=1
    weight = 100
    builders = ['account.builder', 'container.builder', 'object.builder']
    ports = ['6002', '6001', '6000']

    if len(swift_workers) < repfactor:
        print "we are tring to have %d replications on %d swift workers!" % (repfactor, len(swift_worker))
        sys.exit()

    worker_machines = [machines[m] for m in swift_workers]

    sudo('chmod +wr %s', bossworkingdir)
    with cd(bossworkingdir):
        for b in builders:
            run('swift-ring-builder %s create %s %s %s' 
                % (b, partpower, repfactor, movetime))

            zone = 0 # should be unique for each ip
            for m in worker_machines:
                ip = m.privip
                dev = os.path.split(m.mntpt)[1]
            
            # make an entry for machine m in each builder b at port p 
            for b, p in [(builders[n],ports[n]) for n in xrange(len(builders))]:
                run('swift-ring-builder %s add r%sz%s-%s:%s/%s %s' 
                    % (b, region, zone, ip, p, dev, weight))
                zone += 1
                    
        # distribute the partitions evenly across the nodes
        for b in builders:
            run('swift-ring-builder %s rebalance' % b)

    # place the builders in /etc/swift so we have them somewhere safe
    if bossworkingdir != '/etc/swift':
        files = os.path.join(bossworkingdir, '*.builders')
        rings = os.path.join(bossworkingdir, '*.ring.gz')
        sudo('mv %s /etc/swift/' % builders)
        sudo('mv %s /etc/swift/' % rings)
        


@runs_once
@roles('boss')
def get_rings():
    rings = os.path.join('/etc/swift', '*.ring.gz')
    builders = os.path.join('/etc/swift', '*.builder')

    get(rings, localworkingdir)
    get(builders, localworkingdir)


@parallel
@roles('swift-cluster')
def distribute_rings():
    
    rings = '*ring.gz' #["account.ring.gz", "container.ring.gz", "object.ring.gz"]

    sudo('mkdir -p /etc/swift')
    sudo('chmod a+w /etc/swift')
    #for ring in rings:
    put(os.path.join(localworkingdir, rings), '/etc/swift/', use_sudo=True)
    sudo('chown -R swift:swift /etc/swift')


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
    with cd(localworkingdir):
        local('export user=%s && export passwd=%s && export authtype=%s && %s' 
              % (swift_user, swift_passwd, authtype, script))


@parallel
@roles('swift-proxies')
def cluster_proxy():

    sudo('mkdir -p /etc/swift')
    sudo('chmod a+w /etc/swift')
    put(os.path.join(localworkingdir, 'proxy-server.conf'), '/etc/swift/')

    # configure memcached
    if machine.type.lower() == 'ubuntu':
        sudo('perl -pi -e "s/-l 127.0.0.1/-l 0.0.0.0/" /etc/memcached.conf')
        sudo('service memcached start')
    elif machine.type.lower() == 'fedora':
        sudo('perl -pi -e "s/OPTIONS=\"/OPTIONS=\"-l 0.0.0.0 /" /etc/sysconfig/memcached')
        sudo('systemctl enable memcached.service && systemctl start memcached.service')

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
    ip = machine.privip

    put(get_script_path('swift-rsync.sh'), '/tmp')
    sudo('chmod +x /tmp/swift-rsync.sh')
    run('export fspath=%s; export maxconn=%s; /tmp/swift-rsync.sh' % (fs_path, machine.rsync_maxconn))
    sudo('mv /tmp/rsyncd.conf /etc/')
    # enable the rsync daemon
    sudo('perl -pi -e "s/0.0.0.0/%s/" /etc/rsyncd.conf' % (ip))
    if machine.type.lower() == 'ubuntu':
        sudo('perl -pi -e "s/RSYNC_ENABLE=false/RSYNC_ENABLE=true/" /etc/default/rsync')
        sudo('service rsync start')
    elif machine.type.lower() == 'fedora':
        sudo('perl -pi -e "s/disable\s+= yes/disable = no/" /etc/xinetd.d/rsync')
        sudo('/usr/bin/env rsync --daemon')


@runs_once
def storage_config_gen():

    with cd(localworkingdir):
        local(get_script_path('swift-ringconfig.sh'))
        local(get_script_path('swift-objexpconfig.sh'))



@parallel
@roles('swift-workers')
def cluster_storage():

    machine = machines[env.host_string]
    swiftfs_path = machine.mntpt
    ip = machine.privip

    sudo('rm -rf /etc/swift/account-server.conf /etc/swift/container-server.conf /etc/swift/object-server.conf')

    # set up ring config files
    sudo('mkdir -p /etc/swift')
    sudo('chmod a+w /etc/swift')
    put(os.path.join(localworkingdir, 'account-server.conf'), '/etc/swift/')
    put(os.path.join(localworkingdir, 'container-server.conf'), '/etc/swift/')
    put(os.path.join(localworkingdir, 'object-server.conf'), '/etc/swift/')

    sudo('perl -pi -e "s/0.0.0.0/%s/" /etc/swift/*-server.conf' % (ip))

    sudo('chown swift:swift %s' % swiftfs_path)
    sudo('chown -R swift:swift /etc/swift')
    sudo('swift-init all start') # starts every swift process that has a config file



@parallel
@roles('swift-object-expirer')
def cluster_object_exp():

    put(os.path.join(localworkingdir, 'object-expirer.conf'), '/etc/swift')
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
    with cd(localworkingdir):
        local(get_script_path('swift-keygen.sh'))


@parallel
@roles('swift-cluster')
def distribute_key():

    sudo('mkdir -p /etc/swift')
    sudo('chmod a+w /etc/swift')
    put(os.path.join(localworkingdir, 'swift.conf'), '/etc/swift/swift.conf')
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
    with cd(localworkingdir):
        local(get_script_path('swift-logging.sh'))


@parallel
@roles('swift-cluster')
def cluster_logging():
    put(os.path.join(localworkingdir, 'swiftlog.conf'), 
        '/etc/rsyslog.d/swift.conf', use_sudo=True)
    put(os.path.join(localworkingdir, 'swiftrotate.conf'), 
        '/etc/logrotate.d/swift', use_sudo=True)
    sudo('chown root:root /etc/rsyslog.d/swift.conf')
    sudo('chown root:root /etc/logrotate.d/swift')
    sudo('service rsyslog restart')


@parallel
@roles('swift-cluster')
def clean_logs():
    with settings(warn_only=True):
        sudo('rm /etc/swift/swift.log*')
        sudo('service rsyslog reload')


# installs our swift deployment
@parallel
@roles('swift-cluster')
def install_dependencies():

    machine = machines[env.host_string]
    if machine.type == 'ubuntu':
        with settings(warn_only=True):
            sudo('apt-get update')
        sudo('apt-get -y --force-yes install memcached git-core xfsprogs rsync python-configobj python-coverage python-nose python-setuptools python-simplejson python-xattr python-webob python-eventlet python-greenlet python-netifaces') # python-pastedeploy
    elif machine.type == 'fedora':
        sudo('yum -y install git memcached xinetd rsync xfsprogs python-netifaces python-nose python-mock python-dns python-setuptools python-simplejson')


@parallel
@roles('swift-cluster')
def install_swift_from_git():
    # get the swift code, checkout v1.9.0 and install it
    with cd('/tmp'):
        run('git clone https://github.com/openstack/swift.git')
        with cd('swift'):
            run('git checkout 1.9.0 -b v1.9.0')
            sudo('python setup.py install')

@parallel
@roles('swift-cluster')
def install_swauth_from_git():
    # get the swauth code, checkout v1.0.8 and install it
    with cd('/tmp'):
        run('git clone https://github.com/gholt/swauth.git')
        with cd('swauth'):
            run('git checkout 1.0.8 -b 1.0.8')
            sudo('python setup.py install')



@parallel
@roles('swift-cluster')
def create_directories():
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
    machine = machines[env.host_string]
    if machine.makeSwiftUser:
        sudo('useradd -r -s /sbin/nologin -c "Swift Daemon" swift')


@parallel
@roles('swift-cluster')
def create_memcached_user():
    machine = machines[env.host_string]
    if machine.makeMemcachedUser:
        sudo('useradd -r -s /sbin/nologin -c "Memcached Daemon" memcached')


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
        p = machines[env.host_string].pubip
        run('swift -A http://%s:8080/auth/v1.0 -U system:%s -K %s stat' % (p, swift_user, swift_passwd))


@roles('swift-cluster')
def test_ips():
    put(get_script_path('getmyip.py'), '/tmp/')
    run('python /tmp/getmyip.py')
    

@roles('swift-proxies')
def test_memcached():
    put(get_script_path('getmyip.py'), '/tmp/')
    put(get_script_path('memcachedtest.py'), '/tmp/')
    run('python /tmp/memcachedtest.py')


@parallel
@roles('swift-cluster')
def clean_files(files="proxy-server.conf"):
    sudo('rm -rf '+files)


@parallel
@roles('swift-cluster')
def fix_pastedeploy_install():
    with settings(warn_only=True):
        sudo('easy_install pip')
        sudo('pip uninstall -y PasteDeploy ')
        sudo('pip install PasteDeploy')


@parallel
@roles('swift-cluster')
def increase_networking_capabilities():
    sudo("sed '$ a\\nnet.ipv4.tcp_tw_recycle=1\nnet.ipv4.tcp_tw_reuse=1\nnet.ipv4.netfilter.ip_conntrack_max = 262144' /etc/sysctl.conf")
    sudo('sysctl -p')


@roles('swift-cluster')
def change_shell(shell='/bin/bash'):
    sudo('chsh -s %s %s' % (shell, env.user))



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
    execute(install_dependencies)
    execute(install_swift_from_git)
    execute(install_swauth_from_git)
    execute(create_users)
    execute(create_directories)
    if len(loopback_machines):
        execute(setup_loop_device)
    execute(cluster_keygen)
    execute(cluster_rings)
    if len(swift_proxies):
        execute(proxy_config)
    if len(swift_workers):
        execute(storage_config)
    execute(setup_logging)

    print "\n\n\t Finished swift installation!"
    print "make sure to back up the *.builder files! \n\n"
