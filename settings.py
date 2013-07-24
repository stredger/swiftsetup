

import machinedef
import os


# TODO: Checks so these variables cant screw us?


#==================== Script Variables ========================#

# This is where all our helper scripts should be!
swift_script_dir = os.getcwd()

# Should we check the shell of each machine is bash?
check_shell = True

# superuser for swift
swift_user = 'megauser' # 'gis'

# password for swift
swift_passwd = 'stepheniscool' # 'uvicgis'

# this host will be connected to so a host
#  can get its own ip
host_to_check_ip = 'www.google.com'

# should be swauth or tempauth
authtype = 'swauth'

# where we will generate rings and builders and such on the boss machine
bossworkingdir = '/etc/swift'

# where we will generate temp files and such on the local machine
localworkingdir = '/tmp'

# the replication factor in the cluster
repfactor = 3


#==================== Machines, Keys, Passwords ========================#


keyfile = '~/.ssh/st_rsa'
passwd = None



# ## The Machine() object is defined as follows: ##
#
# hostname, # the only required arg, hostname of the machine
# ip=None, # ip to use, if None will try to get the public ip
# mtype='ubuntu', # string to say machine type
# key="~/.ssh/id_rsa", # ssh keyfile to use #CURRENTLY IGNORED
# password="", # ssh password to use #CURRENTLY IGNORED
# worker=False, # if True we will be used to store stuff
# proxy=False, # if True we will have a proxy server installed
# boss=False, # if True we will be used to build the ring files (1 boss per cluster)
# obj_exp=False, # if True we will handle deleting unused objects from the cluster
# dev_setup=False, # if True we want to make a loopback file
# dev='swiftdisk', # name of our loopback file
# dev_path='/srv/', # path to where our loopback file will be
# dev_size=25*1024, # size of our swift filesystem in KB, 25MB is around the MIN size
# mntpt='/srv/node/swiftfs', # where our swift filesystem will be
# rsync_maxconn=6, # max connections for rsync to handle (used to move files)
# makeSwiftUser=True,
# makeMemcachedUser=False,
# sshport=None, # if these are set then fabrics en.host_string will 
# sshuser=None  #  return the ssh command like user@host:port (which we want)


# msuffix1 = ".hdoop.vikelab.emulab.net"
# # dictionary of hostname:Machine
# machines = {
#     "alpha" + msuffix1 : machinedef.Machine("alpha" + msuffix1,
#                                             ip="",
#                                             worker=True,
#                                             proxy=True,
#                                             boss=True,
#                                             dev_setup=True,
#                                             key=keyfile,
#                                             password=passwd),
#     "beta-0" + msuffix1 : machinedef.Machine("beta-0" + msuffix1,
#                                              ip="",
#                                              worker=True,
#                                              dev_setup=True,
#                                              key=keyfile,
#                                              password=passwd),
#     "beta-1" + msuffix1 : machinedef.Machine("beta-1" + msuffix1,
#                                              ip="",
#                                              worker=True,
#                                              objexp=True,
#                                              dev_setup=True,
#                                              key=keyfile,
#                                              password=passwd),
#     }

#k = "~./ssh/st_rsa"
#passwd = machinedef.prompt_for_password()

# ubuntu
msuffix = "pc3.utah.geniracks.net"
utahinsta = {
    msuffix+":32570" : machinedef.Machine(msuffix,
                                          sshport=32570,
                                          privip='10.10.1.3',
                                          proxy=True,
                                          boss=True,
                                          ),
    msuffix+":32571" : machinedef.Machine(msuffix,
                                          sshport=32571,
                                          privip='10.10.1.2',
                                          worker=True,
                                          objexp=True,
                                          dev_setup=True,
                                          dev_size=2*1024*1024
                                          ),
    msuffix+":32572" : machinedef.Machine(msuffix,
                                          sshport=32572,
                                          privip='10.10.1.1',
                                          worker=True,
                                          dev_setup=True,
                                          dev_size=2*1024*1024
                                          ),
    msuffix+":32573" : machinedef.Machine(msuffix,
                                          sshport=32573,
                                          privip='10.10.1.4',
                                          worker=True,
                                          dev_setup=True,
                                          dev_size=2*1024*1024
                                          ),
    }


# ubuntu
msuffix = "pc508.emulab.net"
utahemu = {
    msuffix+":31290" : machinedef.Machine(msuffix,
                                          sshport=31290,
                                          privip='10.10.1.1',
                                          proxy=True,
                                          boss=True
                                          ),
    msuffix+":31291" : machinedef.Machine(msuffix,
                                          sshport=31291,
                                          privip='10.10.1.2',
                                          worker=True,
                                          objexp=True,
                                          dev_setup=True,
                                          dev_size=2*1024*1024
                                          ),
    msuffix+":31292" : machinedef.Machine(msuffix,
                                          sshport=31292,
                                          privip='10.10.1.3',
                                          worker=True,
                                          dev_setup=True,
                                          dev_size=2*1024*1024
                                          ),
    msuffix+":31293" : machinedef.Machine(msuffix,
                                          sshport=31293,
                                          privip='10.10.1.4',
                                          worker=True,
                                          dev_setup=True,
                                          dev_size=2*1024*1024
                                          ),
    }


# fedora
msuffix = "pc1.instageni.gpolab.bbn.com"
gpo = {
    msuffix+":33338" : machinedef.Machine(msuffix,
                                          sshport=33338,
                                          mtype='fedora',),
    msuffix+":33339" : machinedef.Machine(msuffix,
                                          sshport=33339,
                                          mtype='fedora',),
    msuffix+":33340" : machinedef.Machine(msuffix,
                                          sshport=33340,
                                          mtype='fedora',),
    msuffix+":33341" : machinedef.Machine(msuffix,
                                          sshport=33341,
                                          mtype='fedora',)
}


# ubuntu
msuffix = ".uvic.trans-cloud.net"
uvic = {
    "grack01" + msuffix : machinedef.Machine("grack01" + msuffix,
                                             proxy=True,
                                             boss=True),
    "grack02" + msuffix : machinedef.Machine("grack02" + msuffix,
                                             worker=True,
                                             proxy=True),
    "grack03" + msuffix : machinedef.Machine("grack03" + msuffix,
                                             worker=True),
    "grack04" + msuffix : machinedef.Machine("grack04" + msuffix,
                                             worker=True),
    "grack06" + msuffix : machinedef.Machine("grack06" + msuffix,
                                             worker=True,
                                             objexp=True)
    }

# get savi machines in on this?



machines = utahemu
#machines.update(utahInsta)



# Auto generate hostname lists for the fabric roles
swift_cluster,swift_workers,swift_proxies,boss, \
    swift_object_exp,loopback_machines = machinedef.generate_roles(machines)
