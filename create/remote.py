# -*- coding: utf8 -*-
import uuid
import time
from fabric import Connection

class ServerConn:
    def __init__(self,**kwargs):
        self.ip=kwargs.get('ip')
        self.port=kwargs.get('port')
        self.user=kwargs.get('user')
     
        self.memorysize=kwargs.get('memorysize')
        self.cpusize=kwargs.get('cpusize')
        self.maxvcpus=kwargs.get('maxvcpus')
        self.disksize=kwargs.get('disksize')
        self.version=kwargs.get('version')
        self.uuid=str(uuid.uuid4())
        self.os=kwargs.get('os')
        self.vmip=kwargs.get('vmip')
        self.vmnetmask=kwargs.get('vmnetmask')
        self.vmgateway=kwargs.get('vmgateway')
 
        arch=kwargs.get('arch')
        if arch =='64':
            self.arch='x86_64'
        else:
            self.arch='i386'

        self.vmname=self.os+self.version+'-'+self.arch+'-'+self.vmip

        self.c = Connection(
            host='%s' % self.ip,
            user='%s' % self.user,
            port = self.port,
            connect_timeout=30,
            connect_kwargs={"password": ")GTN1ZM_PZ<[_"})

    
    def install_vm(self):
        '''
        创建虚机 以及 磁盘
        '''
        self.c.run('virt-install --connect qemu:///system --name=%s \
            --uuid=%s --ram=%s --vcpus %s,maxvcpus=%s\
            --disk path=/export/kvm_images/volume-%s.qcow2,bus=virtio,size=30,format=qcow2 \
            --accelerate --location=http://10.52.8.251/cobbler/ks_mirror/%s-%s-%s/ \
            --extra-args "ks=http://10.52.8.251/cblr/svc/op/ks/profile/%s-%s-%s" \
            --graphics vnc --network bridge=br0,model=virtio --force \
            --autostart --noautoconsole \
       ' %(self.vmname,self.uuid,self.memorysize,self.cpusize,self.maxvcpus,self.uuid,self.os,self.version,self.arch,self.os,self.version,self.arch))
        if (len(self.disksize) >= 2):
            self.c.run('qemu-img create /export/kvm_images/volume-%s-1.qcow2 -f qcow2 %sG' % (self.uuid,self.disksize))
            self.c.run('sed -i "/<\/disk>/a\  <disk type=\'file\' device=\'disk\'><driver name=\'qemu\' type=\'qcow2\' cache=\'none\'\/><source file=\'\/export\/kvm_images\/volume-%s-1.qcow2\'\/><target dev=\'vdb\' bus=\'virtio\'\/><\/disk>" /etc/libvirt/qemu/%s.xml' % (self.uuid,self.vmname))
        msg='虚机开始创建'
        return msg

    def init_vm(self):
        ''' 初始化虚拟机配置 '''
        xes_status=self.c.run("virsh list --all |grep %s |awk '{print $NF}'" %(self.vmname))
        if xes_status != 'running':
            self.c.run('sed -i "/<boot dev=\'hd\'\/>/a\  <smbios mode=\'sysinfo\'\/>" /etc/libvirt/qemu/%s.xml' % (self.vmname))
            self.c.run('sed -i "/<\/vcpu>/a\  <sysinfo type=\'smbios\'><bios><entry name=\'vendor\'>Fenghua</entry></bios><system><entry name=\'manufacturer\'>XCloud</entry><entry name=\'product\'>XCloud ECS</entry><entry name=\'version\'>pc-i440fx-2.1</entry><entry name=\'serial\'>Not Specified</entry><entry name=\'family\'>Not Specified</entry></system></sysinfo>" /etc/libvirt/qemu/%s.xml' % (self.vmname))
            self.c.run('sed -i "s/clock offset=\'utc\'/clock offset=\'localtime\'/" /etc/libvirt/qemu/%s.xml' % (self.vmname))
            self.c.run('sed -i "/<\/features>/a\  <cpu mode=\'host-passthrough\'>" /etc/libvirt/qemu/%s.xml' %(self.vmname))
            self.c.run('sed -i "/<cpu mode=\'host-passthrough\'>/a\  </cpu>" /etc/libvirt/qemu/%s.xml' %(self.vmname))
        else:
            msg = '初始化失败，请稍后再试'
            return msg


    def template_vm(self):
        '''
        创建模板
        '''
        ipconfig='''
        DEVICE="eth0"
        BOOTPROTO="static"
        ONBOOT="yes"
        TYPE="Ethernet"
        IPADDR={ip}
        NETMASK={netmask}
        GATEWAY={gateway}
        '''.format(ip=self.vmip,netmask=self.vmnetmask,gateway=self.vmgateway)
        self.c.run('mkdir -p /opt/kvm_install/config/%s/' % self.vmip)
        self.c.run('echo "%s" >/opt/kvm_install/config/%s/ifcfg-eth0' %(ipconfig.replace(' ','').lstrip(),self.vmip))

        rc_local='''\
#!/bin/sh
#
# This script will be executed *after* all the other init scripts.
# You can put your own initialization stuff in here if you don't
# want to do the full Sys V style init stuff.

touch /var/lock/subsys/local
curl http://10.52.8.252/chushihua.sh |bash
'''
        self.c.run('echo "%s" >/opt/kvm_install/config/rc.local'%(rc_local.strip()))

    def setting_vm(self):
        ''' 设置虚机参数 '''
        #virt_check= self.c.run('which virt-copy-in')
        #print virt_check
        #if virt_check != 0:
        self.c.run('yum install -y libguestfs-tools-c')
        self.c.run('virt-copy-in -d %s /opt/kvm_install/config/%s/ifcfg-eth0 /etc/sysconfig/network-scripts/' %(self.vmname,self.vmip))
        self.c.run('chmod 755 /opt/kvm_install/config/rc.local && virt-copy-in -d %s /opt/kvm_install/config/rc.local /etc/rc.d/' % (self.vmname))
        self.c.run('cp /etc/libvirt/qemu/%s.xml /opt/kvm_install/%s.xml' % (self.vmname,self.vmname))
        self.c.run('virsh undefine %s' %(self.vmname))
        self.c.run('virsh define /opt/kvm_install/%s.xml' %(self.vmname))
        self.c.run('mv /opt/kvm_install/%s.xml /opt/kvm_install/config/%s/%s.xml' %(self.vmname,self.vmip,self.vmname))

    def start_vm(self):
        ''' 启动虚机 '''
        status=self.c.run("virsh list --all |grep %s |awk '{print $NF}'" %(self.vmname))
        if status != 'running':
            self.c.run('virsh start %s' % (self.vmname))
        else:
            msg='虚机已启动'
            return msg
