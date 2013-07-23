
import socket as soc
import getpass

def getip(host):
    return soc.gethostbyname(host)


def promptForPassword():
    return getpass.getpass()


def generateRoles(machines):
    cluster = []
    worker = []
    proxy = []
    boss = None
    objexp = []
    loopbacks = []

    def genFabHoststring(machine):
        s = ""
        if machine.sshUser is not None: s += "%s@" % (machine.user)
        s += machine.hostname
        if machine.sshPort is not None: s += ":%s" % (machine.sshPort)
        return s

    for hostname, machine in machines.items():
        cluster.append(genFabHoststring(machine))
        if machine.worker: worker.append(genFabHoststring(machine))
        if machine.proxy: proxy.append(genFabHoststring(machine))
        if boss is None and machine.boss: boss = genFabHoststring(machine)
        if machine.objexp: objexp.append(genFabHoststring(machine))
        if machine.dev_setup: loopbacks.append(genFabHoststring(machine))

    return cluster, worker, proxy, [boss], objexp, loopbacks


class Machine():
    
    def __init__(self,
                 hostname, # the only required arg, hostname of the machine
                 pubip=None, # ip to use, if None will try to get the public ip
                 privip=None,
                 mtype='ubuntu', # string to say machine type
                 key="~/.ssh/id_rsa", # ssh keyfile to use #CURRENTLY IGNORED
                 password="", # ssh password to use
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
                 makeSwiftUser=True,
                 makeMemcachedUser=False,
                 sshPort=None, # if these are set then fabrics en.host_string will 
                 sshUser=None, #  return the ssh command like user@host:port (which we want)
                 repNum=3,
                 ):

        self.hostname = hostname
        self.pubip = pubip if pubip is not None else getip(hostname)
        self.privip = privip if privip is not None else self.pubip
        self.type = mtype
        self.key = key
        self.passwd = password
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
        self.makeSwiftUser = makeSwiftUser
        self.makeMemcachedUser = makeMemcachedUser
        self.sshPort = str(sshPort)
        self.sshUser = sshUser
        self.repNum = repNum
