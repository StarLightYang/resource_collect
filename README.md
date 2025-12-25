# 汇总各类资源采集工具

## host_collect.py

支持采集 Linux、Windows 的主机信息。

具体采集信息包括：

Linux：操作系统信息、主机名、网卡信息、内存信息、文件系统分区、硬盘信息、iptables信息、服务信息；

Windows：服务信息、操作系统信息、磁盘信息、CPU信息、内存信息、网卡信息。



## taobao_product_collect.py

淘宝商品爬虫工具。

按需修改参数：Cookie、em_token、eC、ep_data_param，

通过逆向淘宝API的方式获取数据。 

具体采集信息包括：商品ID、标题、当前价、累计销量、店铺名、所在地、商店标签、抓取时间。



## taobao_comment_collect.py

淘宝评论爬虫工具。

按需修改参数：Cookie、em_token、eC、ep_data_param，

通过逆向淘宝API的方式获取数据。 

具体采集信息包括：商品ID、商品名称、用户名、日期、购买规格、评论内容、点赞数、图片链接。



#smartx_collect.py

采集SmartX平台数据，需确认SmartX平台版本是否适用工具中的API接口。

具体采集信息包括：SmartX 宿主机、虚拟机、虚拟网络、网卡。