# -*- coding: utf8 -*-
from fabric import Connection

class ServerConn:
    def __init__(self,**kwargs):
        self.ip=kwargs.get('ip')
        self.port=kwargs.get('port')
        self.user=kwargs.get('user')
        self.c = Connection(
            host='%s' % self.ip,
            user='%s' % self.user,
            port = self.port,
            connect_timeout=30,
            connect_kwargs={"password": "woLIj55)GTN1ZM_PZ<[_"})

    
    def server_info(self):
        '''
        查看磁盘、内存、CPU
        '''
        root_disk=self.c.run("df -h|grep -E '/$'|awk '{print $5}'",hide=True).stdout.strip()
        export_disk=self.c.run("df -h|grep -E '/export$'|awk '{print $5}'",hide=True).stdout.strip()
        info={
            'root_disk':root_disk,
            'export_disk':export_disk,
        }

        return info

#if __name__ == '__main__':
#    kwargs = {
#        'ip':'10.20.52.178',
#        'port':22,
#        'user':'root',
#    }
#    host_disk=(ServerConn(**kwargs).server_info())
#    print host_disk['root_disk']
#
