
import sys, os
from fabric.api import *
from config import *

"""
Before you run:
 make sure all the machines are defined correctly in config.py !!

 Be sure to check the filesystem size, mountpoint and such!
 The mountpoint is used in the rsyncd.config file as well as setting up the 
 loopback device


Usefull stuff!

To run a full install: fab swift_install

To distribute rings: fab distribute_rings

To restart all swift processes: fab swift_restart
"""

# TODO: get key and pass for each machine somehow..

# These are the roles machines play in the cluster
#  They should be lists of hostnames we can ssh into
env.roledefs = {
    'swift-cluster':swift_cluster,
    'swift-workers':swift_workers,
    'swift-proxies':swift_proxies,
    'swift-object-expirer':swift_object_exp,
    'boss':boss,
    'loopback-machines':loopback_machines
}

if keyfile: env.key_filename = keyfile
env.password = passwd or ''




def get_script_path(f):
    """ returns the full path for the script file f """
    return os.path.join(swift_script_dir, f)




def cluster_rings():
    """ Creates and distributes the ring files which are the heart (brain?) of the swift repo
      as they are the mapping to where a file gets placed! (basically imagine all
      the possible hash values as a ring. Then map sections of that ring to machines)
    """
    execute(create_rings)
    execute(get_rings)
    execute(distribute_rings)


@runs_once
@roles('boss')
def create_rings():
    """ Creates the ring files for the swift repo. Rings control the mapping from
     files to location and must be present on every machine in the cluster.  If a 
     new machine is added to the cluster the rings must be rebuit and redistributed.
     The actual ring files are created from builder files, which can be manipulated
     with the swift-ring-builder command.
    """

    partpower = 18 # how large each partition is, 2^this_num
    movetime = 1 # min hours between partition move
    region=1
    weight = 100
    builders = ['account.builder', 'container.builder', 'object.builder']
    ports = ['6002', '6001', '6000']

    if len(swift_workers) < repfactor:
        print "we are tring to have %d replications on %d swift workers!" % (repfactor, len(swift_worker))
        sys.exit()

    worker_machines = [machines[m] for m in swift_workers]

    sudo('chmod +wr %s' % bossworkingdir)
    with cd(bossworkingdir):
        for b in builders:
            sudo('swift-ring-builder %s create %s %s %s' 
                % (b, partpower, repfactor, movetime))

        zone = 0 # should be unique for each ip
        for m in worker_machines:
            ip = m.privip
            dev = os.path.split(m.mntpt)[1]
            
            # make an entry for machine m in each builder b at port p 
            for b, p in [(builders[n],ports[n]) for n in xrange(len(builders))]:
                sudo('swift-ring-builder %s add r%sz%s-%s:%s/%s %s' 
                    % (b, region, zone, ip, p, dev, weight))
            zone += 1
                    
        # distribute the partitions evenly across the nodes
        for b in builders:
            sudo('swift-ring-builder %s rebalance' % b)

    # place the builders in /etc/swift so we have them somewhere safe
    if os.path.normpath(bossworkingdir) != '/etc/swift':
        builders = os.path.join(bossworkingdir, '*.builder')
        rings = os.path.join(bossworkingdir, '*.ring.gz')
        sudo('mv %s /etc/swift/' % builders)
        sudo('mv %s /etc/swift/' % rings)
        

@runs_once
@roles('boss')
def get_rings():
    """ Downloads the ring and builder files from boss to local """
    rings = os.path.join('/etc/swift', '*.ring.gz')
    builders = os.path.join('/etc/swift', '*.builder')

    get(rings, localworkingdir)
    get(builders, localworkingdir)


@parallel
@roles('swift-cluster')
def distribute_rings():
    """ Distributes the ring files from the local machine to each remote machine """
    sudo('mkdir -p /etc/swift')
    sudo('chmod a+w /etc/swift')

    rings = '*ring.gz'
    put(os.path.join(localworkingdir, rings), '/etc/swift/', use_sudo=True)
    sudo('chown -R swift:swift /etc/swift')


@parallel
@roles('swift-cluster')
def clean_rings():
    """ Removes all ring files on all remote machines """
    sudo('rm -f /etc/swift/*.ring.gz')




def proxy_config():
    """ Configures the swift proxies
     generates proxy-server.conf config file and distributes it to all the proxies
     Also sets up the memcached daemon
    """
    execute(local_proxy)
    execute(cluster_proxy)


@runs_once
def local_proxy():
    """ locally generates proxy-server.conf file """
    script = get_script_path('swift-pconfgen.sh')
    local('cd %s && export user=%s && export passwd=%s && export authtype=%s && %s' 
          % (localworkingdir, swift_user, swift_passwd, authtype, script))


@parallel
@roles('swift-proxies')
def cluster_proxy():
    """ Configures swift proxies by moving proxy-server.conf and setting
     machine specific parameters. Also sets up the memcached service.  
    """
    sudo('mkdir -p /etc/swift')
    sudo('chmod a+w /etc/swift')
    put(os.path.join(localworkingdir, 'proxy-server.conf'), 
        '/etc/swift/', use_sudo=True)

    machine = machines[env.host_string]

    # set the public ip for swauth to use
    sudo('perl -pi -e "s/PUBIP/%s/" /etc/swift/proxy-server.conf' % (machine.pubip))

    # configure memcached
    if machine.type.lower() == 'ubuntu':
        sudo('perl -pi -e "s/-l 127.0.0.1/-l 0.0.0.0/" /etc/memcached.conf')
        #sudo('service memcached start')
    elif machine.type.lower() == 'fedora':
        sudo('perl -pi -e "s/OPTIONS=\"/OPTIONS=\"-l 0.0.0.0 /" /etc/sysconfig/memcached')
        #sudo('systemctl enable memcached.service && systemctl start memcached.service')

    sudo('service memcached start')
    sudo('chown -R swift:swift /etc/swift')
    sudo('swift-init proxy start')




def storage_config():
    """ Configures storage nodes, and the object-expirer.
     Generates config files for swift, and rsyncd to use
     and places them on the remote machines.
    """
    execute(storage_config_gen)
    execute(rsync_config)
    execute(cluster_object_exp)
    execute(cluster_storage)


@runs_once
def storage_config_gen():
    """ Creates base config files required for swift workers """

    # the with cd() command doesnt work for the local function
    #  so just append the 'cd <dir> &&' manually
    local('cd %s && %s' 
          % (localworkingdir, get_script_path('swift-ringconfig.sh')))
    local('cd %s && %s' 
          % (localworkingdir, get_script_path('swift-objexpconfig.sh')))
    local('cd %s && %s' 
          % (localworkingdir, get_script_path('swift-rsync.sh')))


@parallel
@roles('swift-workers')
def rsync_config():
    """ Moves the rsync config file from the local machine to remote machines
     and sets some machine specific parameters, on the remote machines
    """
    machine = machines[env.host_string]
    fspath = os.path.dirname(machine.mntpt)
    ip = machine.privip

    put(os.path.join(localworkingdir, 'rsyncd.conf'), '/etc/', use_sudo=True)
    sudo('perl -pi -e "s/MAXCONN/%s/" /etc/rsyncd.conf' % (machine.rsync_maxconn))
    # use : instead of / as fspath is a path with /'s in it!
    sudo('perl -pi -e "s:SWIFTFSPATH:%s:" /etc/rsyncd.conf' % (fspath)) 
    sudo('perl -pi -e "s/0.0.0.0/%s/" /etc/rsyncd.conf' % (ip))

    if machine.type.lower() == 'ubuntu':
        sudo('perl -pi -e "s/RSYNC_ENABLE=false/RSYNC_ENABLE=true/" /etc/default/rsync')
        sudo('service rsync start')
    elif machine.type.lower() == 'fedora':
        sudo('perl -pi -e "s/disable\s+= yes/disable = no/" /etc/xinetd.d/rsync')
        sudo('/usr/bin/env rsync --daemon')    


@parallel
@roles('swift-object-expirer')
def cluster_object_exp():
    """ Moves the object-expirer config file to a remote machine """
    put(os.path.join(localworkingdir, 'object-expirer.conf'), 
        '/etc/swift', use_sudo=True)
    sudo('chown -R swift:swift /etc/swift')
    sudo('swift-init object-expirer start')


@parallel
@roles('swift-workers')
def cluster_storage():
    """ Moves the storage machine config files to the storage machines 
     Also sets machine specific parameters
    """
    machine = machines[env.host_string]
    swiftfs_path = machine.mntpt
    ip = machine.privip

    sudo('rm -rf /etc/swift/account-server.conf /etc/swift/container-server.conf /etc/swift/object-server.conf')

    # set up ring config files
    sudo('mkdir -p /etc/swift')
    sudo('chmod a+w /etc/swift')
    put(os.path.join(localworkingdir, 'account-server.conf'), 
        '/etc/swift/', use_sudo=True)
    put(os.path.join(localworkingdir, 'container-server.conf'), 
        '/etc/swift/', use_sudo=True)
    put(os.path.join(localworkingdir, 'object-server.conf'), 
        '/etc/swift/', use_sudo=True)

    sudo('perl -pi -e "s/0.0.0.0/%s/" /etc/swift/*-server.conf' % (ip))

    if machine.uselocalfs:
        sudo('perl -pi -e "s/mount_check=True/mount_check=False/" /etc/swift/*-server.conf')

    sudo('chown swift:swift %s' % swiftfs_path)
    sudo('chown -R swift:swift /etc/swift')
    sudo('swift-init all start') # starts every swift process that has a config file





def cluster_keygen():
    """ Creates a swift cluster key, and distributes it to each node
     this key must be present on all nodes in the cluster!!
    """
    execute(local_keygen)
    execute(distribute_key)


@runs_once
def local_keygen():
    """ Generates a the key (swift.conf) to be used for a swift cluster """
    # we probably want to back up the file this generates somewhere!
    local('cd %s && %s' % (localworkingdir, get_script_path('swift-keygen.sh')))


@parallel
@roles('swift-cluster')
def distribute_key():
    """ Moves the key (swift.conf) to each machine in the cluster """
    sudo('mkdir -p /etc/swift')
    sudo('chmod a+w /etc/swift')
    put(os.path.join(localworkingdir, 'swift.conf'), '/etc/swift/swift.conf')
    sudo('chown -R swift:swift /etc/swift')
    



@parallel
@roles('loopback-machines')
def setup_loop_device():
    """ Sets up a 'machine.dev_size' size loopback filesystem at 'machine.mntpt'
     Makes the actual loopback file in 'machine.dev_path' called 'machine.dev'
    """
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
    """ Sets up logging for the cluster with rsyslog """
    execute(log_config_gen)
    execute(cluster_logging)


@runs_once
def log_config_gen():
    """ Generates rsyslog and logrotate config files on the local machine """
    local('cd %s && %s' % (localworkingdir, get_script_path('swift-logging.sh')))


@parallel
@roles('swift-cluster')
def cluster_logging():
    """ Moves the log config files to the remote machines, and restarts rsyslog """
    put(os.path.join(localworkingdir, 'swiftlog.conf'), 
        '/etc/rsyslog.d/swift.conf', use_sudo=True)
    put(os.path.join(localworkingdir, 'swiftrotate.conf'), 
        '/etc/logrotate.d/swift', use_sudo=True)
    sudo('chown root:root /etc/rsyslog.d/swift.conf')
    sudo('chown root:root /etc/logrotate.d/swift')
    # fedora machines the same? Also might want to reload not restart
    sudo('service rsyslog restart')


@parallel
@roles('swift-cluster')
def clean_logs():
    """ removes swift log files """
    with settings(warn_only=True):
        sudo('rm /etc/swift/swift.log*')
        sudo('service rsyslog reload')





@parallel
@roles('swift-cluster')
def install_dependencies():
    """ Installs dependencies using the appropreate package manager """
    machine = machines[env.host_string]
    if machine.type == 'ubuntu':
        with settings(warn_only=True):
            sudo('apt-get update')
        sudo('apt-get -y --force-yes install libffi6 libffi-dev memcached git-core xfsprogs rsync python-configobj python-coverage python-nose python-setuptools python-simplejson python-xattr python-webob python-eventlet python-greenlet python-netifaces') # python-pastedeploy
    elif machine.type == 'fedora':
        sudo('yum -y install git gcc libffi libffi-devel memcached xinetd rsync xfsprogs python-netifaces python-nose python-mock python-dns python-setuptools python-simplejson')

    if machine.uselocalfs:
        install_xattr_hack()


@parallel
@roles('swift-cluster')
def install_swift_from_git():
   """ get swift from git, checkout v1.9.0 and install it """
   machine = machines[env.host_string]

   with cd('/tmp'):
       with settings(warn_only=True):
           run('git clone https://github.com/openstack/swift.git')
       with cd('swift'):
           with settings(warn_only=True):
               run('git checkout 1.9.0 -b v1.9.0')

               # for some reason we fail to install dependencies
               #  the first time. Instead of figuring out the problem,
               #  we are just going to try the install twice (which works)
               sudo('python setup.py install')

           sudo('python setup.py install')


@parallel
@roles('swift-cluster')
def install_swauth_from_git():
    """ get swauth from git, checkout v1.0.8 and install it """
    with cd('/tmp'):
        with settings(warn_only=True):
            run('git clone https://github.com/gholt/swauth.git')
        with cd('swauth'):
            with settings(warn_only=True):
                run('git checkout 1.0.8 -b 1.0.8')
            sudo('python setup.py install')


@parallel
@roles('swift-workers')
def install_xattr_hack():
    """ installs our xattr swift hack from github """
    with cd('/tmp'):
       with settings(warn_only=True):
           run('git clone https://github.com/stredger/fake-xattr.git')
       with cd('fake-xattr'):
           sudo('python setup.py install')


@runs_once
@roles('swift-proxies')
def swauth_setup():
    """ Runs swauth initialization on proxies """
    run('swauth-prep -K %s' % (swift_passwd))


@parallel
@roles('swift-cluster')
def create_directories():
    """ Creates directories required by installation """
    sudo('mkdir -p /etc/swift')
    sudo('chown swift:swift /etc/swift')

    sudo('mkdir -p /var/cache/swift')
    sudo('chown swift:swift /var/cache/swift')

    sudo('mkdir -p /srv/node/swiftfs')
    sudo('chown swift:swift /srv/node/swiftfs')

    machine = machines[env.host_string]
    # used to store fake xattrs
    if machine.uselocalfs:
        sudo('mkdir -p /etc/swift/xattrs')
        sudo('chown swift:swift /etc/swift/xattrs')


def create_users(memcached=False):
    """ This will create the required users. memcache is usually 
     created when memcached is installed so we dont create it 
     by default  
    """
    execute(create_swift_user)
    if memcached:
        execute(create_memcached_user)


@parallel
@roles('swift-cluster')
def create_swift_user():
    """ Creates a swift user, on machines that want it """
    machine = machines[env.host_string]
    if machine.makeSwiftUser:
        sudo('useradd -r -s /sbin/nologin -c "Swift Daemon" swift')


@parallel
@roles('swift-cluster')
def create_memcached_user():
    """ Creates a memcached worker, on machines that want it """
    machine = machines[env.host_string]
    if machine.makeMemcachedUser:
        sudo('useradd -r -s /sbin/nologin -c "Memcached Daemon" memcached')


@roles('swift-cluster')
def change_shell(shell='/bin/bash'):
    """ Change the shell on the remote hosts """
    sudo('chsh -s %s %s' % (shell, env.user))


@parallel
@roles('swift-cluster')
def check_login_shell(change=True):
    """ Check that the login shell on the remote hosts is bash,
     if not change the shell to bash
    """
    sh = run('echo $SHELL')
    if "bash" not in sh:
        if change: change_shell()
        else: abort("The installation will not work unless bash is our default shell!!")
    



@parallel
@roles('swift-cluster')
def swift_restart():
    """ For all machines in the cluster, restart all the processes
     we can find config files for in /etc/swift
    """
    sudo('swift-init all restart')


@parallel
@roles('swift-cluster')
def swift_stop():
    """ Stop all swift processes on all machines """
    sudo('swift-init all stop')


@roles('boss')
def test_proxies():
    """ Test that we can correctly connect to all swift proxies """
    for proxy in swift_proxies:
        p = machines[env.host_string].pubip
        run('swift -A http://%s:8080/auth/v1.0 -U system:%s -K %s stat' % (p, swift_user, swift_passwd))


@roles('swift-cluster')
def test_ips():
    """ get the public ips for all machines in the cluster """
    put(get_script_path('getmyip.py'), '/tmp/')
    run('python /tmp/getmyip.py')
    

@roles('swift-proxies')
def test_memcached():
    """ test that memcached is working on all proxy machines """
    put(get_script_path('getmyip.py'), '/tmp/')
    put(get_script_path('memcachedtest.py'), '/tmp/')
    run('python /tmp/memcachedtest.py')


@parallel
@roles('swift-cluster')
def clean_files(files="proxy-server.conf"):
    """ Remove files on all machines in the cluster """
    sudo('rm -rf '+files)


@parallel
@roles('swift-cluster')
def fix_pastedeploy_install():
    """ reinstall paste deploy to fix bugged installs """
    with settings(warn_only=True):
        sudo('easy_install pip')
        sudo('pip uninstall -y PasteDeploy ')
        sudo('pip install PasteDeploy')


@parallel
@roles('swift-cluster')
def increase_networking_capabilities():
    """ Inrease the maximum number of tcp connections """
    sudo("sed '$ a\\nnet.ipv4.tcp_tw_recycle=1\nnet.ipv4.tcp_tw_reuse=1\nnet.ipv4.netfilter.ip_conntrack_max = 262144' /etc/sysctl.conf")
    sudo('sysctl -p')


@parallel
@roles('swift-cluster')
def fix_yum_fc15():
    """ Fix the yum install on bugged fc15 machines """
    for repo in ['fedora', 'fedora-updates']:
        sudo("perl -pi -e 's/#baseurl/baseurl/' /etc/yum.repos.d/%s.repo" %(repo))
        sudo("perl -pi -e 's/mirrorlist/#mirrorlist/' /etc/yum.repos.d/%s.repo" % (repo))


@roles('boss')
def init_swauth_web_admin():
    """ initialize the swauth web admin interface """
    with cd('/tmp'):
        with settings(warn_only=True):        
            run('git clone https://github.com/gholt/swauth.git')    
        with cd('swauth/webadmin'):
            authip = machines[swift_proxies[0]].privip
            authurl = "http://%s:8080/auth/v1.0" % (authip)
            run("swift -A %s -U .super_admin:.super_admin -K %s upload .webadmin ." 
                % (authurl, swift_passwd))


@roles('swift-cluster')
def ifconfig():
    """ run ifconfig on all machines """
    sudo('ifconfig')


@roles('swift-cluster')
def df():
    """ run df on all machines """
    sudo('df -h')


@parallel
@roles('swift-cluster')
def restart_rsyslog():
    """ restart rsyslog on all machines """
    sudo('service rsyslog restart')


@roles('boss')
def swauth_add_user(user='savant', group='savant', key='savant'):
    """ add a user to a swift install with swauth """
    proxyip = machines[swift_proxies[0]].pubip
    run('swauth-add-user -A http://%s:8080/auth -K %s -a %s %s %s' 
        % (proxyip, swift_passwd, group, user, key))





def swift_install():
    """ this is the main install function, run this to do a full install.
     It can be run multiple times (without messing up the installation) but the 
     device setup should only be run once (and only if we want to use a loopback device)
    """
    
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
    execute(proxy_config)
    execute(storage_config)
    execute(setup_logging)
    execute(swauth_setup)

    print "\n\n\t Finished swift installation!"
    print "make sure to back up the *.builder files! \n\n"
