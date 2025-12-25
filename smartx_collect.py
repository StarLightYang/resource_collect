# -*- coding:utf-8 -*-

import requests
import sys
import json
import re
import hashlib
import hmac
import logging

requests.packages.urllib3.disable_warnings()

# 格式化log
logging.basicConfig(level=logging.INFO, format="[%(levelname)s][%(asctime)s]\n%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

def user_request(url, method, params=None):
    headers = {'content-type': 'application/json'}
    # print (url)
    # print (headers)
    # print (params)
    # print (method)
    response = requests.request(method, url, headers=headers, json=params, verify=False)
    # print (response.text)
    try:
        response_json = response.json()
        if response.status_code == 200:
            if response_json.has_key("token"):
                return 0, response_json  # success
            else:
                return response_json['code'], response_json
        else:
            try:
                return response_json['code'], response_json
            except Exception as e:
                print ("http exception: ", e)
    except Exception as e:
        print (e)

def smartx_request(url, method, token, params=None):
    headers = {'accept': 'application/json', 'X-SmartX-Token': token}
    url = url
    # print (url)
    # print (headers)
    # print (params)
    # print (method)
    response = requests.request(method, url, headers=headers, json=params, verify=False)
    # print (response.text)
    try:
        response_json = response.json()
        if response_json.has_key('data'):
            return response_json
    except Exception as e:
        print (e)

def smartx_search_all(url, token):
    search_url = "https://X.X.X.X%s?count=%d&skip_page=%d" % (url, 100, 1)
    search_method = "GET"
    search_datas = smartx_request(search_url, search_method, token)

    total = search_datas["data"]["total_entities"]
    all_data = search_datas["data"]["entities"]

    if total > 100:
        pages = (total / 100) + (0 if (total % 100) == 0 else 1)

        for i in range(2, pages + 1):
            search_url = "https://X.X.X.X%s?count=%d&skip_page=%d" % (url, 100, i)
            search_datas = smartx_request(search_url, search_method, token)
            print (u"分页大小: 100, 当前页码: %d, 实例总数: %d" % (i, total))
            all_data += search_datas["data"]["entities"]
    return all_data

if __name__ == "__main__":
    logging.info(u'开始登陆SmartX!')
    user_url = "https://X.X.X.X/api/v3/sessions"
    user_method = "POST"
    user_params = {
        "username": "test-username",
        "password": "test-password"
    }
    user_code, user_info = user_request(user_url, user_method, user_params)
    logging.info(u'SmartX登陆完成!')
    print("\n")

    if user_code == 0:
        logging.info(u'开始采集SmartX 宿主机!')
        host_datas = smartx_request("https://X.X.X.X/api/v2/management/hosts", "GET", user_info["token"])
        host_contact = []
        for host_data in host_datas["data"]:
            host_dict = {}
            nic_contact = []
            host_dict["name"] = host_data["name"]
            host_dict["id"] = host_data["host_uuid"]
            host_dict["uuid"] = host_data["host_uuid"]
            host_dict["ip"] = host_data["management_ip"]
            host_dict["accessIP"] = host_data["ipmi_ip"]
            host_dict["mdl"] = host_data["model"]
            host_dict["cpuBMhz"] = host_data["cpu"]["hz_advertised"]
            host_dict["cpuBrand"] = host_data["cpu"]["brand"]
            host_dict["cpuCoreCount"] = host_data["cpu"]["num_cores"]
            host_dict["ipmiIP"] = host_data["ipmi_ip"]
            host_dict["dataIP"] = host_data["data_ip"]
            host_dict["rpcIP"] = host_data["rpc_ip"]
            host_dict["sn"] = host_data["sn"]
            host_dict["menSizeG"] = str(round(host_data["memory"]["total"] / 1024 / 1024 / 1024, 2)) + "GiB"
            for nic in host_data["nics"]:
                nic_dict = {}
                nic_dict["eth"] = nic["name"]
                nic_dict["mac"] = nic["hwaddr"]
                nic_contact.append(nic_dict)
            if len(nic_contact) > 0:
                host_dict["networkInfo"] = nic_contact
            host_contact.append(host_dict)

        logging.info(u'SmartX 宿主机采集完成!')
        print("host_contact:")
        print(json.dumps(host_contact, indent=2, ensure_ascii=False))
        print("\n")

        logging.info(u'开始采集SmartX 虚拟机/SmartX 虚拟网络/SmartX 网卡!')
        # 获取VM全量数据
        vm_datas = smartx_search_all("/api/v2/vms", user_info["token"])

        # 获取VM虚拟磁盘相关信息
        vmdisk_datas = smartx_search_all("/api/v2/volumes", user_info["token"])
        vmdisk_dicts = {}
        for vmdisk_data in vmdisk_datas:
            vmdisk_dict = {}
            if vmdisk_data.has_key("mounting_vm_list") and len(vmdisk_data["mounting_vm_list"]) > 0:
                if not vmdisk_dicts.has_key(vmdisk_data["mounting_vm_list"][0]["name"]) or len(
                        vmdisk_dicts[vmdisk_data["mounting_vm_list"][0]["name"]]) < 1:
                    vmdisk_dicts[vmdisk_data["mounting_vm_list"][0]["name"]] = []
                vmdisk_dict["name"] = vmdisk_data["name"]
                vmdisk_dict["resource_state"] = vmdisk_data["resource_state"]
                vmdisk_dict["type"] = vmdisk_data["type"]
                vmdisk_dict["path"] = vmdisk_data["path"]
                vmdisk_dicts[vmdisk_data["mounting_vm_list"][0]["name"]].append(vmdisk_dict)

        vm_contact = []
        vlan_contact = []
        for vm_data in vm_datas:
            vm_dict = {}
            vm_disk_contact = []
            vm_dict["uuid"] = vm_data["uuid"]
            vm_dict["description"] = vm_data["description"]
            vm_dict["firmware"] = vm_data["firmware"]
            vm_dict["status"] = vm_data["status"]
            vm_dict["type"] = vm_data["type"]
            vm_dict["vmName"] = vm_data["vm_name"]
            vm_dict["ha"] = vm_data["ha"]
            vm_dict["memory"] = vm_data["memory"] / 1024 / 1024 / 1024
            vm_dict["vcpu"] = vm_data["vcpu"]

            for nic in vm_data["nics"]:
                vlan_dict = {}
                # 获取SmartX 虚拟网络数据
                vlan_dict["id"] = nic["vlans"][0]["vlan_id"]
                vlan_dict["name"] = "VLAN" + str(nic["vlans"][0]["vlan_id"])
                vlan_dict["uuid"] = nic["vlan_uuid"]
                val = 0
                for vlans in vlan_contact:
                    if vlans["uuid"] == nic["vlan_uuid"]:
                        val = 1
                        break
                if val == 0:
                    vlan_contact.append(vlan_dict)

            for vm_disk in vm_data["disks"]:
                vm_disk_dict = {}
                vm_disk_dict["boot"] = vm_disk["boot"]
                vm_disk_dict["bus"] = vm_disk["bus"]
                vm_disk_dict["path"] = vm_disk["path"]
                if vmdisk_dicts.has_key(vm_data["vm_name"]):
                    for vmdisk in vmdisk_dicts[vm_data["vm_name"]]:
                        if vmdisk["path"] == vm_disk["path"]:
                            vm_disk_dict["name"] = vmdisk["name"]
                            vm_disk_dict["type"] = vmdisk["type"]

                            if vmdisk["resource_state"] == "in-use":
                                vm_disk_dict["disabled"] = True
                            else:
                                vm_disk_dict["disabled"] = False
                vm_disk_contact.append(vm_disk_dict)

            if len(vm_disk_contact) > 0:
                vm_dict["disks"] = vm_disk_contact
            vm_contact.append(vm_dict)

        logging.info(u'SmartX 虚拟机/SmartX 虚拟网络-采集完成!')
        print("vm_contact:")
        print(json.dumps(vm_contact, indent=2, ensure_ascii=False))
        print("vlan_contact:")
        print(json.dumps(vlan_contact, indent=2, ensure_ascii=False))
        print("\n")

        logging.info(u'开始采集SmartX 网卡!')
        nic_contact = []
        for vm_data in vm_datas:
            for nic in vm_data["nics"]:
                nic_dict = {}
                # 获取SmartX 网卡数据
                if nic.has_key("ip_address") and nic.has_key("mark"):
                    nic_dict["name"] = nic["mark"] + "_" + nic["ip_address"] + "_" + nic["mac_address"]
                elif nic.has_key("ip_address"):
                    nic_dict["name"] = nic["ip_address"] + "_" + nic["mac_address"]
                else:
                    nic_dict["name"] = nic["mac_address"]
                if nic.has_key("gateway"):
                    nic_dict["gateway"] = nic["gateway"]
                if nic.has_key("ip_address"):
                    nic_dict["ip"] = nic["ip_address"]
                if nic.has_key("mac_address"):
                    nic_dict["mac"] = nic["mac_address"]
                if nic.has_key("model"):
                    nic_dict["model"] = nic["model"]
                if nic.has_key("subnet_mask"):
                    nic_dict["netmask"] = nic["subnet_mask"]
                if nic.has_key("link") and nic["link"] == "up":
                    nic_dict["enabled"] = True
                else:
                    nic_dict["enabled"] = False
                nic_dict["vm"] = [{"uuid": vm_data["uuid"]}]
                nic_contact.append(nic_dict)

        logging.info(u'SmartX 网卡-采集完成!')
        print("nic_contact:")
        print(json.dumps(nic_contact, indent=2, ensure_ascii=False))


