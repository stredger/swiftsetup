

import machinedef


#==================== Machines, Keys, Passwords ========================#


keyfile = "~/.ssh/st_rsa"
passwd = "STE!@#!!"



# ## The Machine() object is defined as follows: ##
#
# hostname, # the only required arg, hostname of the machine
# ip=None, # ip to use, if None will try to get the public ip
# key="~/.ssh/id_rsa", # ssh keyfile to use #CURRENTLY IGNORED
# password="", # ssh password to use #CURRENTLY IGNORED
# worker=False, # if True we will be used to store stuff
# proxy=False, # if True we will have a proxy server installed
# boss=False, # if True we will be used to build the ring files (1 boss per cluster)
# obj_exp=False, # if True we will handle deleting unused objects from the cluster
# dev_setup=False, # if True we want to make a loopback file
# dev='swiftdisk', # name of our loopback file
# dev_path='/srv/', # path to where our loopback file will be
# dev_size=50*100000, # size of our swift filesystem
# mntpt='/srv/node/swiftfs', # where our swift filesystem will be
# rsync_maxconn=6 # max connections for rsync to handle (used to move files)

msuffix1 = ".hdoop.vikelab.emulab.net"
# dictionary of hostname:Machine
machines = {
    "alpha" + msuffix1 : machinedef.Machine("alpha" + msuffix1,
                                            ip="",
                                            worker=True,
                                            proxy=True,
                                            boss=True,
                                            dev_setup=True,
                                            key=keyfile,
                                            password=passwd),
    "beta-0" + msuffix1 : machinedef.Machine("beta-0" + msuffix1,
                                             ip="",
                                             worker=True,
                                             dev_setup=True,
                                             key=keyfile,
                                             password=passwd),
    "beta-1" + msuffix1 : machinedef.Machine("beta-1" + msuffix1,
                                             ip="",
                                             worker=True,
                                             obj_exp=True,
                                             dev_setup=True,
                                             key=keyfile,
                                             password=passwd),
    }

msuffix = ".uvic.trans-cloud.net"
k = "~./ssh/st_rsa"
passwd = machinedef.prompt_for_password()
machines = {
    "grack01" + msuffix : machinedef.Machine("grack01" + msuffix,
                                             key=k,
                                             proxy=True,
                                             boss=True),
    "grack02" + msuffix : machinedef.Machine("grack02" + msuffix,
                                             key=k,
                                             worker=True,
                                             proxy=True),
    "grack03" + msuffix : machinedef.Machine("grack03" + msuffix,
                                             key=k,
                                             worker=True),
    "grack04" + msuffix : machinedef.Machine("grack04" + msuffix,
                                             key=k,
                                             worker=True),
    "grack06" + msuffix : machinedef.Machine("grack06" + msuffix,
                                             key=k,
                                             worker=True,
                                             obj_exp=True)
 
    }

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



# Auto generate hostname lists for the fabric roles
swift_cluster,swift_workers,swift_proxies,boss, \
    swift_object_exp,loopback_machines = machinedef.generate_roles(machines)
