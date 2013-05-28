
# import like this to avoid namespace collisions as we
#  probably want to say: from settings import *
import socket as soc


def get_ip(host):
    return soc.gethostbyname(host)


def generate_roles():
    cluster = []
    worker = []
    proxy = []
    boss = None
    obj_exp = []
    loopbacks = []

    for hostname, machine in machines.items():
        cluster.append(machine.hostname)
        if machine.worker:
            worker.append(machine.hostname)
        if machine.proxy:
            proxy.append(machine.hostname)
        if boss is None and machine.boss: # only want one boss
            boss = machine.hostname
        if machine.obj_exp:
            obj_exp.append(machine.hostname)
        if machine.dev_setup:
            loopbacks.append(machine.hostname)

    return cluster, worker, proxy, [boss], obj_exp, loopbacks



keyfile = "~/.ssh/st_rsa"
passwd = "STE!@#!!"

class Machine():
    
    def __init__(self,
                 hostname, # the only required arg, hostname of the machine
                 ip=None, # ip to use, if None will try to get the public ip
                 key=keyfile, # ssh keyfile to use #CURRENTLY IGNORED
                 password=passwd, # ssh password to use #CURRENTLY IGNORED
                 worker=False, # if True we will be used to store stuff
                 proxy=False, # if True we will have a proxy server installed
                 boss=False, # if True we will be used to build the ring files (1 boss per cluster)
                 obj_exp=False, # if True we will handle deleting unused objects from the cluster
                 dev_setup=False, # if True we want to make a loopback file
                 dev='swiftdisk', # name of our loopback file
                 dev_path='/srv/', # path to where our loopback file will be
                 dev_size=50*100000, # size of out swift filesystem
                 mntpt='/srv/node/swiftfs', # where our swift filesystem will be
                 rsync_maxconn=6 # max connections for rsync to handle (used to move files)
                 ):

        self.hostname = hostname
        if ip is None:
            self.ip = get_ip(hostname)
        else:
            self.ip = ip
        self.key=key
        self.passwd = password
        self.worker = worker
        self.proxy = proxy
        self.boss = boss
        self.obj_exp = obj_exp
        self.dev_setup = dev_setup
        self.dev = dev
        self.dev_path = dev_path
        self.dev_size = dev_size # size in bytes
        self.mntpt = mntpt
        self.rsync_maxconn = rsync_maxconn
        




msuffix1 = ".hdoop.vikelab.emulab.net"


#==================== Machines, Keys, Passwords ========================#

# dictionary of hostname:Machines
machines = {
    "alpha" + msuffix1:Machine("alpha" + msuffix1, worker=True, proxy=True, boss=True, dev_setup=True),
    "beta-0" + msuffix1:Machine("beta-0" + msuffix1, worker=True, dev_setup=True),
    "beta-1" + msuffix1:Machine("beta-1" + msuffix1, worker=True, obj_exp=True, dev_setup=True),
    #"pantera.cs.uvic.ca":Machine("pantera.cs.uvic.ca", worker=True, proxy=True, boss=True, obj_exp=True)
    }

# Auto generate hostname lists for the fabric roles
swift_cluster,swift_workers,swift_proxies,boss, \
    swift_object_exp,loopback_machines = generate_roles()


#==================== Script Variables ========================#

# This is where all our helper scripts should be!
swift_script_dir = "./"

# Should we check the shell of each machine is bash?
check_shell = True

# user for swift
swift_user = 'gis'

# password for swift
swift_passwd = 'uvicgis'

# this host will be connected to so a host
#  can get its own ip
host_to_check_ip = "www.google.com"

# machine = machines[swift_cluster[0]]
# print machine.ip
# print machine.mntpt
# print machine.mntpt[0:machine.mntpt.rfind('/')+1]
