
import socket as soc

def get_ip(host):
    return soc.gethostbyname(host)


def generate_roles(machines):
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


class Machine():
    
    def __init__(self,
                 hostname, # the only required arg, hostname of the machine
                 ip=None, # ip to use, if None will try to get the public ip
                 key="~/.ssh/id_rsa", # ssh keyfile to use #CURRENTLY IGNORED
                 password="", # ssh password to use #CURRENTLY IGNORED
                 worker=False, # if True we will be used to store stuff
                 proxy=False, # if True we will have a proxy server installed
                 boss=False, # if True we will be used to build the ring files (1 boss per cluster)
                 obj_exp=False, # if True we will handle deleting unused objects from the cluster
                 dev_setup=False, # if True we want to make a loopback file
                 dev='swiftdisk', # name of our loopback file
                 dev_path='/srv/', # path to where our loopback file will be
                 dev_size=50*100000, # size of our swift filesystem
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
        

