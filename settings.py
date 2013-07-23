

import machinedef


#==================== Machines, Keys, Passwords ========================#


keyfile = "~/.ssh/st_rsa"
passwd = None
authtype = 'swauth' # should be swauth or tempauth

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
# sshPort=None, # if these are set then fabrics en.host_string will 
# sshUser=None  #  return the ssh command like user@host:port (which we want)


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
utahInsta = {
    msuffix+":32570" : machinedef.Machine(msuffix,
                                          sshPort=32570,
                                          #key=k,
                                          privip='10.10.1.3',
                                          proxy=True,
                                          boss=True,
                                          ),
    msuffix+":32571" : machinedef.Machine(msuffix,
                                          sshPort=32571,
                                          #key=k,
                                          privip='10.10.1.2',
                                          worker=True,
                                          objexp=True,
                                          dev_setup=True,
                                          dev_size=2*1024*1024
                                          ),
    msuffix+":32572" : machinedef.Machine(msuffix,
                                          sshPort=32572,
                                          #key=k,
                                          privip='10.10.1.1',
                                          worker=True,
                                          dev_setup=True,
                                          dev_size=2*1024*1024
                                          ),
    msuffix+":32573" : machinedef.Machine(msuffix,
                                          sshPort=32573,
                                          #key=k,
                                          privip='10.10.1.4',
                                          worker=True,
                                          dev_setup=True,
                                          dev_size=2*1024*1024
                                          ),
    }


# ubuntu
msuffix = "pc508.emulab.net"
utahEmu = {
    msuffix+":31290" : machinedef.Machine(msuffix,
                                          sshPort=31290,
                                          #key=k
                                          ),
    msuffix+":31291" : machinedef.Machine(msuffix,
                                          sshPort=31291,
                                          #key=k
                                          ),
    msuffix+":31292" : machinedef.Machine(msuffix,
                                          sshPort=31292,
                                          #key=k
                                          ),
    msuffix+":31293" : machinedef.Machine(msuffix,
                                          sshPort=31293,
                                          #key=k
                                          ),
    }


# fedora
msuffix = "pc1.instageni.gpolab.bbn.com"
gpo = {
    msuffix+":33338" : machinedef.Machine(msuffix,
                                          sshPort=33338,
                                          #key=k,
                                          mtype='fedora',),
    msuffix+":33339" : machinedef.Machine(msuffix,
                                          sshPort=33339,
                                          #key=k,
                                          mtype='fedora',),
    msuffix+":33340" : machinedef.Machine(msuffix,
                                          sshPort=33340,
                                          #key=k,
                                          mtype='fedora',),
    msuffix+":33341" : machinedef.Machine(msuffix,
                                          sshPort=33341,
                                          #key=k,
                                          mtype='fedora',)
}


# ubuntu
msuffix = ".uvic.trans-cloud.net"
uvic = {
    "grack01" + msuffix : machinedef.Machine("grack01" + msuffix,
                                             #key=k,
                                             proxy=True,
                                             boss=True),
    "grack02" + msuffix : machinedef.Machine("grack02" + msuffix,
                                             #key=k,
                                             worker=True,
                                             proxy=True),
    "grack03" + msuffix : machinedef.Machine("grack03" + msuffix,
                                             #key=k,
                                             worker=True),
    "grack04" + msuffix : machinedef.Machine("grack04" + msuffix,
                                             #key=k,
                                             worker=True),
    "grack06" + msuffix : machinedef.Machine("grack06" + msuffix,
                                             #key=k,
                                             worker=True,
                                             objexp=True)
    }

# get savi machines in on this?



machines = utahInsta
#machines.update(utahInsta)

#==================== Script Variables ========================#

# This is where all our helper scripts should be!
swift_script_dir = "./"

# Should we check the shell of each machine is bash?
check_shell = True

# superuser for swift
swift_user = 'megauser' # 'gis'

# password for swift
swift_passwd = 'stepheniscool' # 'uvicgis'

# this host will be connected to so a host
#  can get its own ip
host_to_check_ip = "www.google.com"



# Auto generate hostname lists for the fabric roles
swift_cluster,swift_workers,swift_proxies,boss, \
    swift_object_exp,loopback_machines = machinedef.generateRoles(machines)
