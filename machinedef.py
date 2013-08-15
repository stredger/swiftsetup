
import socket as soc
import getpass

def getip(host):
    return soc.gethostbyname(host)


def prompt_for_password():
    return getpass.getpass()


def generate_roles(machines):
    cluster = []
    worker = []
    proxy = []
    boss = None
    objexp = []
    loopbacks = []

    def gen_fab_hoststring(machine):
        s = ""
        if machine.sshuser is not None: s += "%s@" % (machine.sshuser)
        s += machine.hostname
        if machine.sshport is not None: s += ":%s" % (machine.sshport)
        return s

    for hostname, machine in machines.items():
        cluster.append(gen_fab_hoststring(machine))
        if machine.worker: worker.append(gen_fab_hoststring(machine))
        if machine.proxy: proxy.append(gen_fab_hoststring(machine))
        if boss is None and machine.boss: boss = gen_fab_hoststring(machine)
        if machine.objexp: objexp.append(gen_fab_hoststring(machine))
        if machine.dev_setup: loopbacks.append(gen_fab_hoststring(machine))

    return cluster, worker, proxy, [boss], objexp, loopbacks


class Machine():
    
    def __init__(self,
                 hostname, # the only required arg, hostname of the machine
                 pubip=None, # ip to use, if None will try to get the public ip
                 privip=None,
                 mtype='ubuntu', # string to say machine type
                 #key='~/.ssh/id_rsa', # ssh keyfile to use #CURRENTLY IGNORED
                 #password='', # ssh password to use
                 worker=False, # if True we will be used to store stuff
                 proxy=False, # if True we will have a proxy server installed
                 boss=False, # if True we will be used to build the ring files (1 boss per cluster)
                 objexp=False, # if True we will handle deleting unused objects from the cluster
                 dev_setup=False, # if True we want to make a loopback file
                 dev='swiftdisk', # name of our loopback file
                 dev_path='/srv/', # path to where our loopback file will be
                 dev_size=25*1024, # size of our swift filesystem in KB, 25MB is around the MIN size
                 mntpt='/srv/node/swiftfs', # where our swift filesystem will be
                 rsync_maxconn=6, # max connections for rsync to handle (used to move files)
                 make_swift_user=True,
                 make_memcached_user=False,
                 sshport=None, # if these are set then fabrics en.host_string will 
                 sshuser=None, #  return the ssh command like user@host:port (which we want)
                 uselocalfs=False
                 ):

        self.hostname = hostname
        self.pubip = pubip if pubip is not None else getip(hostname)
        self.privip = privip if privip is not None else self.pubip
        self.type = mtype
        #self.key = key
        #self.passwd = password
        self.worker = worker
        self.proxy = proxy
        self.boss = boss
        self.objexp = objexp
        self.dev_setup = dev_setup
        self.dev = dev
        self.dev_path = dev_path
        self.dev_size = dev_size # size in bytes
        self.mntpt = mntpt
        self.rsync_maxconn = rsync_maxconn
        self.makeSwiftUser = make_swift_user
        self.makeMemcachedUser = make_memcached_user
        self.sshport = str(sshport) if sshport is not None else None
        self.sshuser = sshuser
        self.uselocalfs = uselocalfs
