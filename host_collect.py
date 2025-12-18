# -*- coding: utf-8 -*-
import json
import os
import re
import time
import psutil
import chardet
import tempfile
import socket
import platform
import traceback
import subprocess

class HOSTCollectorLinux:
    """
    将其作为class来处理，是考虑到可能中间有变量要共享
    函数里面不需要为捕获异常，外层调用会负责捕获，并打印日志
    """

    def __init__(self, osType):
        self.osType = osType

    '''
    获取操作系统信息
    '''

    def get_os_info(self):
        data = dict()
        data['osSystem'] = platform.system()
        data['osArchitecture'] = platform.machine()
        data['osRelease'] = platform.release()
        return data

    '''
    获取主机名
    '''

    def get_hostname_info(self):
        hostname = socket.gethostname()
        return {'hostname': hostname}

    '''
    获取主机内存信息
    '''

    def get_memory_info(self):
        res = psutil.virtual_memory().total >> 10
        return {'memSize': res}

    '''
    获取主机网卡信息
    '''

    def get_eth_info(self):
        """
        需要解决：
        1. 网卡bond情况，bond0
        2. 虚拟网卡情况，eth0:1
        3. 多ip情况，eth0(1.1.1.1,2.2.2.2)
        4. todo bug: windows下speed，mask，broadcast，status都为空
        """
        data = []
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        for name, entries in addrs.items():
            eth = {
                'name': name,
                'mac': '00:00:00:00:00:00',
                'ip': '',
                'mask': '',
                'broadcast': '',
                'status': 'Unknown',
                'speed': 0
            }
            try:  # windows下中文
                eth['name'] = name.decode('gbk')
            except Exception:
                eth['name'] = name
            if name in stats:
                eth['status'] = 'Active' if int(stats[name].isup) else 'Inactive'
                eth['speed'] = stats[name].speed if stats[name].isup and stats[name].speed != 65535 else 0

            # 先获取这块网卡的mac地址(因为一个网卡可能有多个IP地址， 下面有deepcopy逻辑， 所以提前填写mac地址)
            for entry in entries:
                if entry.family == psutil.AF_LINK:
                    eth['mac'] = entry.address.upper()

            # 获取这块网卡的IP地址（可能有多个）
            for entry in entries:
                if entry.family == socket.AF_INET or entry.family == socket.AF_INET6:
                    if eth['ip']:  # 一个网卡多个ip，注意，这里不是虚拟网卡
                        data.append(eth)
                    address = entry.address
                    # psutil输出ipv6的格式是"ipv6地址%网卡名"，需要去掉"%网卡名"
                    if address.endswith('%' + eth['name']):
                        address = address[:len(address) - len(eth['name']) - 1]
                    eth['ip'] = address
                    eth['mask'] = entry.netmask
                    eth['broadcast'] = entry.broadcast
                else:  # 暂不采集IPV6
                    continue
            data.append(eth)
        # 如果虚拟网卡，则取其实际网卡的mac，避免都是00:00:00:00:00:00，常见虚拟网卡名称都带有":"
        for item in data:
            # 是否虚拟网卡
            if ':' not in item['name']:
                continue
            # 已经有mac，一般不会进入到这个逻辑，网卡名本身就带有":"的情况。
            if item['mac'] != '00:00:00:00:00:00':
                continue
            name = item['name'].rsplit(':', 1)[0]
            for iitem in data:
                if name == iitem['name']:
                    item['mac'] = iitem['mac']
                    break
        data.sort(key=lambda x: x['name'])
        return {'eth': data}

    '''
    获取主机文件系统分区信息
    '''

    def get_filesystem_info(self):
        data = {}
        # all=True获取所有分区，包含网络挂载的
        disks = psutil.disk_partitions(all=True)
        filter_type = {
            # 过滤光盘
            'hsf', 'iso9660', 'iso13490', 'udf',
            # 过滤系统使用的虚拟分区
            'configfs', 'devfs', 'debugfs', 'tracefs', 'kernfs', 'procfs',
            'specfs', 'sysfs', 'tmpfs', 'devtmpfs', 'winfs', 'bpf',
            'fusectl', 'hugetlbfs', 'mqueue', 'pstore',
            'securityfs', 'rpc_pipefs', 'autofs',
            'proc', 'binfmt_misc', 'devpts', 'squashfs',
            # 过滤容器相关技术
            'cgroup', 'lxcfs', 'nsfs', 'cgroup2', "overlay", "tmpfs",
            # 默认过滤网络挂载
            "nfs", "nfs4", "cifs"
        }

        for disk in disks:
            if not disk.device:
                continue
            if 'cdrom' in disk.opts.lower():
                continue
            if 'removable' in disk.opts.lower():
                continue
            # 过滤不需要的文件系统类型
            fs_type = disk.fstype.lower()
            if fs_type in filter_type:
                continue
            skip = False
            # 挂载路径过滤容器相关
            for path in ['/run/docker', '/var/lib/kubelet/pods', '/var/lib/docker']:
                if disk.mountpoint.startswith(path):
                    skip = True
                    break
            if skip:
                continue
            item = dict()
            item['filesystem'] = disk.device
            item['size'] = self.get_disk_size(disk.mountpoint)
            item['used'] = self.get_disk_use_persent(disk.mountpoint)
            item['available'] = self.get_disk_available(disk.mountpoint)
            item['usedPercent'] = self.get_disk_use_persent(disk.mountpoint)
            item['mountPoint'] = disk.mountpoint
            data[item["mountPoint"]] = item
        data = list(data.values())

        # 做排序是为了diff比较一致
        data.sort(key=lambda x: x['filesystem'])
        return {'filesystem': data}

    def get_disk_size(self, mountpoint):
        try:
            return psutil.disk_usage(mountpoint).total >> 10
        except Exception:
            return 0

    def get_disk_use_persent(self, mountpoint):
        try:
            return int(psutil.disk_usage(mountpoint).percent * 100)
        except Exception:
            return 0

    def get_disk_available(self, mountpoint):
        try:
            return psutil.disk_usage(mountpoint).free >> 10
        except Exception:
            return 0

    '''
    获取主机硬盘信息
    '''

    def get_hard_devices_info(self):
        cmd = 'lsblk -P -a -b -o NAME,MAJ:MIN,RM,SIZE,RO,TYPE,MOUNTPOINT'
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        rcode = res.wait()
        output = res.stdout.read().decode('utf-8')

        if rcode != 0:
            self.logger.warning('exec [%s] failed, would not collect hard devices' % cmd)
            return {}
        data = []
        for row in output.splitlines():
            block = row.split()
            if len(block) < 7:
                continue
            item = {}
            item['name'] = self.get_value(block[0])
            maj_min = self.get_value(block[1]).split(':')
            if len(maj_min) >= 2:
                item['major'] = int(maj_min[0])
                item['minor'] = int(maj_min[1])
            if self.get_value(block[3]):
                item['size'] = int(self.get_value(block[3])) >> 10
            item['readyOnly'] = self.get_value(block[4])
            item['type'] = self.get_value(block[5])
            item['mountPoints'] = self.get_value(block[6])
            data.append(item)
        return {'hardDevices': data}

    def get_value(self, key_value):
        return re.sub(r'^.+="(.*)"$', r'\1', key_value)

    '''
    获取主机服务信息
    '''

    def str2int(self, str):
        try:
            return int(str)
        except ValueError:
            return None

    def get_listen_connection_ss(self):
        ss_cmd = "ss -nlp |tail -n +2 |awk '{print $3, $5}' |awk -F',| ' '{print $1,$3}'"
        res = subprocess.Popen(ss_cmd, shell=True, stdout=subprocess.PIPE)
        rcode = res.wait()
        output = res.stdout.read().decode('utf-8')

        if rcode != 0:
            return None

        listen_conn = {}
        all_listen = output.strip().split('\n')
        for each_line in all_listen:
            if not each_line:
                continue
            each_conn = each_line.split()
            if len(each_conn) != 2:
                continue
            pid = int(each_conn[1])
            listen_info = listen_conn.setdefault(pid, [])
            address, port = each_conn[0].rsplit(':', 1)
            port = self.str2int(port)
            if port:
                listen_info.append({'ip': address, 'port': port})
        return listen_conn

    def _is_process_permanent(self, create_time):
        res = False
        current = time.time()
        boot_elapse = current - psutil.boot_time()
        run_time = current - create_time
        # 如果系统启动时间大于15分钟，则进程启动时间必须大于10分钟才判断为常驻进程，避免脉冲
        if boot_elapse > 60 * 15:
            if run_time >= 60 * 10:
                res = True
        # 否则，超过系统启动时间的一半则认为是常驻进程
        else:
            if run_time >= boot_elapse * .5:
                res = True
        return res

    def _is_system_process(self, exe):
        if not exe:
            return True
        return False

    def get_service_info(self):
        listen_connection = self.get_listen_connection_ss()
        if not listen_connection:
            print("not found ss command")
            listen_connection = self._get_listen_connection_psutil

        service_info = self._get_service_info(listen_connection)
        service_info.sort(key=lambda x: x['listening_port'])
        return {'service': service_info}

    @property
    def _get_listen_connection_psutil(self):
        connections = psutil.net_connections()
        conns = {}
        for conn in connections:
            if not conn.pid:
                continue
            if not conn.status == psutil.CONN_LISTEN:
                continue
            listening = conns.setdefault(conn.pid, [])
            ip, port = conn.laddr
            listening.append({'ip': ip, 'port': port})
        return conns

    def _get_service_info(self, conns):
        service_info = []
        # 获得监听端口的进程名
        for proc in psutil.process_iter():
            # 没有监听端口
            if not conns.get(proc.pid, []):
                continue
            # 启动时间是否符合判断
            if not self._is_process_permanent(proc.create_time()):
                continue
            # 是否有exe
            if self._is_system_process(proc.exe()):
                continue

            info = dict()
            info['exe'] = proc.exe()
            info['name'] = proc.name()
            info['pname'] = proc.name()
            info['cwd'] = proc.cwd()
            info['username'] = proc.username()
            for listenings in conns[proc.pid]:
                item = {}
                item.update(info)
                item['listening_ip'] = listenings['ip']
                try:
                    item['listening_port'] = int(listenings['port'])
                except ValueError:
                    item['listening_port'] = listenings['port']
                service_info.append(item)
        return service_info

    '''
    获取iptables信息
    '''

    def get_iptables_info(self):
        data = self.get_iptables() + self.get_iptables(ipv6=True)
        return {'iptables': data}

    def get_iptables(self, ipv6=False):
        data = []
        cmd = 'iptables -L -n'
        if ipv6:
            cmd = 'ip6tables -L -n'
        res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        rcode = res.wait()
        output = res.stdout.read().decode('utf-8')

        if rcode != 0:
            print('exec [%s] failed, would not collect iptables' % cmd)
            return data
        current_chain = ''
        for row in output.splitlines():
            rule = row.split()
            if not rule or rule[0] == 'target':
                continue
            if rule[0] == 'Chain':
                current_chain = rule[1]
                continue
            if len(rule) < 5:
                continue
            item = dict()
            item['isIPv6'] = ipv6
            item['chain'] = current_chain
            item['target'] = rule[0]
            item['protocol'] = rule[1]
            item['options'] = rule[2]
            item['source'] = rule[3]
            item['destination'] = rule[4]
            if len(rule) > 5:
                item['module'] = ' '.join(rule[5:])
            data.append(item)
        return data


class HOSTCollectorWindows:

    def __init__(self, osType):
        self.osType = osType

    '''
    获取操作系统信息
    '''

    def get_os_info(self):
        # 在具体方法引入是因为func_set_timeout的装饰下，wmi连接不在方法内会报AttributeError错误

        pythoncom.CoInitialize()
        wmi_inst = wmi.WMI()
        system_info = wmi_inst.Win32_OperatingSystem()
        data = dict()
        system_version_map = {('5', None): ["post2003"],
                              ('5', '0'): ['2000'],
                              ('5', '1'): ['XP'],
                              ('5', '2'): ['2003'],
                              ('5', '2', '3'): ['2003 R2'],
                              ('6', None): ["post8.1", "post2012ServerR2"],
                              ('6', '0'): ['Vista', 'Server 2008'],
                              ('6', '1'): ['7', 'Server 2008 R2'],
                              ('6', '2'): ['8', 'Server 2012'],
                              ('6', '3'): ['8.1', 'Server 2012 R2'],
                              ('10', '0'): ['10', 'Server 2016', 'Server 2019'],
                              ('10', None): ["post10"]}

        for information in system_info:
            ver_sequence = information.Version.split('.')
            if len(ver_sequence) > 1:
                maj, min = ver_sequence[0], ver_sequence[1]
            else:
                maj, min = ver_sequence[0], None
            system_list = system_version_map.get((maj, min), None)
            product_type = information.ProductType
            if product_type != 1 and len(system_list) > 1:
                data['osRelease'] = system_list[1]
                if 'Server 2019' in information.Caption and len(system_list) > 2:
                    data['osRelease'] = system_list[2]
            elif system_list:
                data['osRelease'] = system_list[0]
            else:
                data['osRelease'] = ""

            data['osSystem'] = 'Windows'
            data['osArchitecture'] = getattr(information, "OSArchitecture", "")
            data['osDistro'] = information.Caption

        return data

    '''
    获取主机磁盘信息
    '''

    def get_disk_info(self):
        data = []
        disk_keys = ["Name", "DeviceId", "FileSystem", "Size", "ProviderName"]
        # DriveType: 3, means local disk
        # 在具体方法引入是因为func_set_timeout的装饰下，wmi连接不在方法内会报AttributeError错误

        pythoncom.CoInitialize()
        wmi_inst = wmi.WMI()
        for disk in wmi_inst.Win32_LogicalDisk(disk_keys, DriveType=3):
            data.append({
                'name': disk.Name,
                'device': disk.DeviceId,
                'mountpoint': disk.DeviceId,
                'fstype': disk.FileSystem,
                'provider': disk.ProviderName,
                'size': int(disk.Size) >> 10 if disk.Size else 0
            })
        # DriveType: 4, means network disk
        for disk in wmi_inst.Win32_LogicalDisk(disk_keys, DriveType=4):
            data.append({
                'name': disk.Name,
                'device': disk.DeviceId,
                'mountpoint': disk.DeviceId,
                'fstype': disk.FileSystem,
                'provider': disk.ProviderName,
                'size': int(disk.Size) >> 10 if disk.Size else 0
            })
        data.sort(key=lambda x: x['device'])
        return {'disk': data}

    '''
    获取主机CPU信息
    '''

    def get_cpu_info(self):
        res = {}
        # 在具体方法引入是因为func_set_timeout的装饰下，wmi连接不在方法内会报AttributeError错误

        pythoncom.CoInitialize()
        wmi_inst = wmi.WMI()
        cpu = wmi_inst.Win32_Processor()

        cpu_type = cpu[0].Name
        res['Name'] = cpu_type
        res['brand'] = cpu_type
        res['architecture'] = platform.machine()
        cpu_speed = cpu[0].MaxClockSpeed

        if cpu_type == 'AMD Athlon(tm) Processor':
            cpu_hz = cpu_speed
        else:
            cpu_hz = '%.2f GHz' % (cpu_speed / 1000.0)
        res['hz'] = cpu_hz

        # core_keys = ["NumberOfProcessors", "NumberOfLogicalProcessors"]
        comp = wmi_inst.Win32_ComputerSystem()[0]
        res['cpu_pieces'] = comp.NumberOfProcessors
        res['logical_cores'] = getattr(comp, 'NumberOfLogicalProcessors', comp.NumberOfProcessors)
        res['physical_cores'] = 0

        for inst in cpu:
            res['physical_cores'] += getattr(inst, 'NumberOfCores', 0)

        if res['physical_cores'] == 0:
            res['physical_cores'] = res['cpu_pieces']
        return {'cpu': res}

    '''
    获取主机内存信息
    '''

    def get_memory_info(self):
        mem_keys = ["TotalPhysicalMemory"]
        # 在具体方法引入是因为func_set_timeout的装饰下，wmi连接不在方法内会报AttributeError错误

        pythoncom.CoInitialize()
        wmi_inst = wmi.WMI()
        comp = wmi_inst.Win32_ComputerSystem(mem_keys)[0]
        return {'memSize': int(comp.TotalPhysicalMemory) >> 10}

    '''
    获取网卡信息
    '''

    def get_eth_info(self):
        data = []
        eth_dict = {}
        eth_static_keys = ["MACAddress", "NetConnectionID", "Speed", "Status", "name", "NetEnabled"]
        # 在具体方法引入是因为func_set_timeout的装饰下，wmi连接不在方法内会报AttributeError错误

        pythoncom.CoInitialize()
        wmi_inst = wmi.WMI()
        # 先获得网卡的硬件信息
        for interface in wmi_inst.Win32_NetworkAdapter(eth_static_keys, NetConnectionStatus=2):
            if interface.NetEnabled and interface.NetConnectionID:
                eth_dict[interface.MACAddress] = {
                    'name': interface.NetConnectionID,
                    'mac': interface.MACAddress,
                    'ip': '',
                    'mask': '',
                    'status': interface.NetEnabled or 'Unknown',
                    'speed': int(interface.Speed) / 1000000 if interface.Speed else 0,
                }
        try:
            # 获得网卡的TCP/IP信息
            eth_config_keys = ["MACAddress", "IPAddress", "IPSubnet"]
            for interface in wmi_inst.Win32_NetworkAdapterConfiguration(eth_config_keys, IPEnabled=1):
                mac_address = interface.MACAddress
                if mac_address not in eth_dict:
                    continue

                if not interface.IPAddress:
                    data.append(eth_dict[mac_address])
                    continue

                for i, ip_address in enumerate(interface.IPAddress):
                    if not ip_address or '.' not in ip_address:
                        continue
                    eth = eth_dict[mac_address]
                    eth['ip'] = ip_address
                    # interface.DefaultIPGateway and interface.DefaultIPGateway[i]
                    eth['mask'] = interface.IPSubnet[i]
                    eth['status'] = 'Active'
                    data.append(eth)
        except Exception:
            print("get eth ip config error, %s", traceback.format_exc())
            if not data:
                data = list(eth_dict.values())
        data.sort(key=lambda x: x['mac'])
        return {'eth': data}

    '''
    获取主机服务信息
    '''

    def _is_system_process(self, exe):
        if not exe:
            return True
        return False

    def _is_process_permanent(self, create_time):
        res = False
        current = time.time()
        boot_elapse = current - psutil.boot_time()
        run_time = current - create_time
        # 如果系统启动时间大于15分钟，则进程启动时间必须大于10分钟才判断为常驻进程，避免脉冲
        if boot_elapse > 60 * 15:
            if run_time >= 60 * 10:
                res = True
        # 否则，超过系统启动时间的一半则认为是常驻进程
        else:
            if run_time >= boot_elapse * .5:
                res = True
        return res

    def _get_listen_connection_psutil(self):
        connections = psutil.net_connections()
        conns = {}
        for conn in connections:
            if not conn.pid:
                continue
            if not conn.status == psutil.CONN_LISTEN:
                continue
            listening = conns.setdefault(conn.pid, [])
            ip, port = conn.laddr
            listening.append({'ip': ip, 'port': port})
        return conns

    def get_service_info(self):
        conns = self._get_listen_connection_psutil()
        service_info = self._get_service_info(conns)
        service_info.sort(key=lambda x: x['listening_port'])

        return {'service': service_info}

    def _get_service_info(self, conns):
        service_keys = [
            "ProcessId",
            "ExecutablePath",
            "Name",
            "CommandLine",
        ]
        service_info = []
        # 在具体方法引入是因为func_set_timeout的装饰下，wmi连接不在方法内会报AttributeError错误

        pythoncom.CoInitialize()
        wmi_inst = wmi.WMI()
        for proc in wmi_inst.Win32_Process(service_keys):
            # 没有监听端口
            if not conns.get(proc.ProcessId, []):
                continue
            # 是否有exe
            if self._is_system_process(proc.ExecutablePath):
                continue
            # 启动时间是否符合判断
            try:
                if not self._is_process_permanent(psutil.Process(proc.ProcessId).create_time()):
                    continue
            except psutil.NoSuchProcess:
                continue

            info = dict()
            info['name'] = proc.Name
            info['cwd'] = proc.CommandLine

            try:
                info['username'] = psutil.Process(proc.ProcessId).username()
            except psutil.AccessDenied:
                pass

            parent_object = psutil.Process(proc.ProcessId).parent()
            if parent_object:
                info['pname'] = parent_object.name()
            else:
                info['pname'] = ''

            for listenings in conns[proc.ProcessId]:
                item = {}
                item.update(info)
                item['listening_ip'] = listenings['ip']
                item['listening_port'] = listenings['port']
                service_info.append(item)
        return service_info


if __name__ == '__main__':
    system = platform.system()

    hostInfo = {}
    if system == "Linux":
        linuxCollect = HOSTCollectorLinux("Linux")

        # 操作系统信息
        osData = linuxCollect.get_os_info()
        hostInfo.update(osData)

        # 主机名
        hostname = linuxCollect.get_hostname_info()
        hostInfo.update(hostname)

        # 网卡信息
        ethData = linuxCollect.get_eth_info()
        hostInfo.update(ethData)

        # 内存信息
        memData = linuxCollect.get_memory_info()
        hostInfo.update(memData)

        # 文件系统分区
        fileSystemData = linuxCollect.get_filesystem_info()
        hostInfo.update(fileSystemData)

        # 硬盘信息
        hardDeviceData = linuxCollect.get_hard_devices_info()
        hostInfo.update(hardDeviceData)

        # iptables信息
        iptablesData = linuxCollect.get_iptables_info()
        hostInfo.update(iptablesData)

        # 服务信息
        service = linuxCollect.get_service_info()
        hostInfo.update(service)


    else:
        import pythoncom
        import wmi

        winCollect = HOSTCollectorWindows("Windows")

        # 服务信息
        service = winCollect.get_service_info()
        hostInfo.update(service)

        # 操作系统信息
        osData = winCollect.get_os_info()
        hostInfo.update(osData)

        # 磁盘信息
        diskData = winCollect.get_disk_info()
        hostInfo.update(diskData)

        # CPU信息
        cpuData = winCollect.get_cpu_info()
        hostInfo.update(cpuData)

        # 内存信息
        memData = winCollect.get_memory_info()
        hostInfo.update(memData)

        # 网卡信息
        ethData = winCollect.get_eth_info()
        hostInfo.update(ethData)

    print("hostInfo:")
    print(json.dumps(hostInfo, indent=2, ensure_ascii=False))
