""" 
Author: Stephen Tredger, 2013

Copyright (c) 2013 University of Victoria

See LICENSE.txt or visit www.geni.net/wp-content/uploads/2009/02/genipublic.pdf 
for the full license
"""

"""
Define parameters for a cluster where Swift is to be installed,

Script Variables are global parameters, the only one that should
definately be changed is the swift_passwd. This is the password
to the admin account for the swift cluster.

Machines are lists of Machine objects, define as follows:

hostname, # the only required arg, hostname of the machine
ip=None, # ip to use, if None will try to get the public ip
mtype='ubuntu', # string to say machine type, should be 'ubuntu' or 'fedora'
key="~/.ssh/id_rsa", # ssh keyfile to use #CURRENTLY IGNORED
password="", # ssh password to use #CURRENTLY IGNORED
worker=False, # if True we will be used to store stuff
proxy=False, # if True we will have a proxy server installed
boss=False, # if True we will be used to build the ring files (1 boss per cluster)
obj_exp=False, # if True we will handle deleting unused objects from the cluster
dev_setup=False, # if True we want to make a loopback file
dev='swiftdisk', # name of our loopback file
dev_path='/srv/', # path to where our loopback file will be
dev_size=2*1024*1024, # (default=2GB) size of our swift filesystem in KB, 25MB is around the MIN size
mntpt='/srv/node/swiftfs', # where our swift filesystem will be
rsync_maxconn=6, # max connections for rsync to handle (used to move files)
makeSwiftUser=True,
makeMemcachedUser=False,
sshport=None, # if these are set then fabrics en.host_string will 
sshuser=None,  #  return the ssh command like user@host:port (which we want)
uselocalfs=False # dont use a separate partition for storage
"""

import machinedef
import os

# TODO: Checks so these variables cant mess up mid installation


#==================== Script Variables ========================#

# This is where all our helper scripts should be!
swift_script_dir = os.getcwd()

# Should we check the shell of each machine is bash?
check_shell = True

# superuser for swift
swift_user = '.super_admin'

# password for swift
swift_passwd = 'stepheniscool'

# this remote host will be connected to so a local host
#  can get its own ip
host_to_check_ip = 'www.google.com'

# should be swauth or tempauth
authtype = 'swauth'

# where we will generate rings and builders and such on the boss machine
bossworkingdir = '/etc/swift'

# where we will generate temp files and such on the local machine
localworkingdir = '/tmp'

# where we will download git repos and such to one the remote machine
remoteworkingdir = '.'

# the replication factor in the cluster
repfactor = 1

# this will put actual ips in swift and rsync config files, if false will use the wildcard 0.0.0.0
use_actual_ip_in_config_files = False

#==================== Machines, Keys, Passwords ========================#

usr = None
keyfile = '~/.ssh/st_rsa'
passwd = None # machinedef.prompt_for_password()




# msuffix = '.uvic.trans-cloud.net'
# uvic = {
#   'grack01' + msuffix : machinedef.Machine( 'grack01' + msuffix,
#                                             proxy=True,
#                                             boss=True),
#   'grack02' + msuffix : machinedef.Machine( 'grack02' + msuffix,
#                                             worker=True,
#                                             proxy=True),
#   'grack03' + msuffix : machinedef.Machine( 'grack03' + msuffix,
#                                             worker=True),
#   'grack04' + msuffix : machinedef.Machine( 'grack04' + msuffix,
#                                             worker=True),
#   'grack06' + msuffix : machinedef.Machine( 'grack06' + msuffix,
#                                             worker=True,
#                                             objexp=True)
#   }



# vicci = {
#   # 'node24.washington.vicci.org' is syndicate MS
#   'node40.washington.vicci.org': machinedef.Machine('node40.washington.vicci.org',
#                                   privip='10.129.39.40',
#                                   proxy=True,
#                                   boss=True,
#                                   mtype='fedora'
#                                 ),
#   'node6.washington.vicci.org': machinedef.Machine('node6.washington.vicci.org',
#                                   privip='10.129.39.6',    
#                                   worker=True,
#                                   objexp=True,
#                                   uselocalfs=True,
#                                   mtype='fedora'
#                                 ),
#   'node60.washington.vicci.org': machinedef.Machine('node60.washington.vicci.org',
#                                   privip='10.129.39.60',
#                                   worker=True,
#                                   uselocalfs=True,
#                                   mtype='fedora'
#                                 ),
#   'node61.washington.vicci.org': machinedef.Machine('node61.washington.vicci.org',
#                                   privip='10.129.39.61',
#                                   worker=True,
#                                   uselocalfs=True,
#                                   mtype='fedora'
#                                 )
# }


savi_vic = {
  '142.104.17.135' : machinedef.Machine('142.104.17.135',
                    privip='10.6.9.13',
                    proxy=True,
                    boss=True,
                    worker=True,
                    objexp=True,
                    # dev_setup=True,
                    # dev_size=2*1024*1024,
                    )
  }

savi_tor = {
  '142.150.208.220' : machinedef.Machine('142.150.208.220',
                    privip='10.12.9.5',
                    proxy=True,
                    boss=True,
                    ),
  '142.150.208.222' : machinedef.Machine('142.150.208.222',
                    privip='10.12.9.4',
                    worker=True,
                    objexp=True,
                    dev_setup=True,
                    dev_size=2*1024*1024,
                    )
  }

savi_carl = {
  '134.117.57.138' : machinedef.Machine('134.117.57.138',
                    privip='10.8.9.5',
                    proxy=True,
                    boss=True,
                    ),
  '134.117.57.137' : machinedef.Machine('134.117.57.137',
                    privip='10.8.9.4',
                    worker=True,
                    objexp=True,
                    dev_setup=True,
                    dev_size=2*1024*1024,
                    )
  }

# bench = {
#   'a.microbe.vikelab.emulab.net' :  
#     machinedef.Machine(
#       'a.microbe.vikelab.emulab.net',
#       proxy=True,
#       boss=True,
#       objexp=True
#     ),
#   'b.microbe.vikelab.emulab.net' :  
#     machinedef.Machine(
#       'b.microbe.vikelab.emulab.net',
#       worker=True,
#       objexp=True,
#       dev_setup=True,
#       dev_size=2*1024*1024
#     )    
# }

# bench2 = {
#   'node0.syn.vikelab.emulab.net' :  
#     machinedef.Machine(
#       'node0.syn.vikelab.emulab.net',
#       proxy=True,
#       boss=True,
#       objexp=True
#     ),
#   'node1.syn.vikelab.emulab.net' :  
#     machinedef.Machine(
#       'node1.syn.vikelab.emulab.net',
#       worker=True,
#       objexp=True,
#       # dev_setup=True,
#       # dev_size=2*1024*1024
#     )    
# }

machines = savi_vic
#machines.update(utah)


# Auto generate hostname lists for the fabric roles
swift_cluster,swift_workers,swift_proxies,boss, \
  swift_object_exp,loopback_machines = machinedef.generate_roles(machines)

