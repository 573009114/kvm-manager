import remote
kwargs={
    'ip':'10.20.52.180',
    'port':22,
    'user':'root',
    'vmip':'10.20.55.167',
    'vmnetmask':'255.255.252.0',
    'vmgateway':'10.20.52.1',
    'memorysize':1024,
    'disksize':'50',
    'cpusize':1,
    'maxvcpus':2,
    'os':'CentOS',
    'version':'6.9',
    'arch':'64',
}

remote.ServerConn(**kwargs).install_vm()
