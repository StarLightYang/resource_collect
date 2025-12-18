import requests
import re
import json
import pandas as pd
import time
import hashlib
import random

info=[]

headers= {
    'referer': 'https://s.taobao.com/',
    'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'Cookie': "thw=cn; aui=2499528446; cna=otP/IKrFsDwCAXFascDe7ey1PW; xlly_s=1; t=ac10fad4fac0db16d928aaa652f03c9d; _tb_token_=e1e03e7d81356; sca=b7f44b6c; _samesite_flag_=true; cookie2=1eaa008f5e308743678bfa843fa94231; 3PcFlag=1764830099999; wk_cookie2=11f5e4afcb12a12a957e4a5d72b15a1f; wk_unb=UUwZ9PQNjXuY%2Bg%3D%3D; sgcookie=E100ftvUMrId4fhEX%2FSrL35eaOoOYOIr7040a8Pse6UaZ%2F75z9ymmnhqmSBKQAPzc%2FHeKVYeLHpIboENskUoTHAulfuMo5Ws%2FzmlJU9uS%2FPBHRw%2FGkC6fG4rTVWtKloq5xpQ; unb=2499528446; csg=9afa9b19; lgc=%5Cu661F%5Cu5149adc; cancelledSubSites=empty; cookie17=UUwZ9PQNjXuY%2Bg%3D%3D; dnk=%5Cu661F%5Cu5149adc; skt=b986b9ea4dd30e7d; tracknick=%5Cu661F%5Cu5149adc; _l_g_=Ug%3D%3D; sg=c6b; _nk_=%5Cu661F%5Cu5149adc; cookie1=U7T0f3Z5yjBSvPA8bEVANEaogzh2MAdn%2BDuG99UG8W0%3D; sn=; uc3=id2=UUwZ9PQNjXuY%2Bg%3D%3D&nk2=s0%2BKohE%2B9Q%3D%3D&lg2=Vq8l%2BKCLz3%2F65A%3D%3D&vt3=F8dD2kgpa13msRo%2BU4E%3D; existShop=MTc2NDgzMDEwNQ%3D%3D; uc4=nk4=0%40sTB8t8nxvWY1a3Dc8X%2FcC4ut&id4=0%40U27GhYUdpL13FrprCcNMeVL%2FJRTJ; _cc_=WqG3DMC9EA%3D%3D; _hvn_lgc_=0; havana_lgc2_0=eyJoaWQiOjI0OTk1Mjg0NDYsInNnIjoiYzc2NzhiYTEzNjM5YjQzMjcwYzBjZjFkYjMxODZhZTAiLCJzaXRlIjowLCJ0b2tlbiI6IjExMmpnallPbUpUdF9oOVZiYlNLN2xnIn0; havana_lgc_exp=1795934107874; sdkSilent=1764858907873; havana_sdkSilent=1764858907873; uc1=cookie14=UoYY50mvXfYQdQ%3D%3D&cookie16=W5iHLLyFPlMGbLDwA%2BdvAGZqLg%3D%3D&existShop=false&pas=0&cookie15=UtASsssmOIJ0bQ%3D%3D&cookie21=VFC%2FuZ9aiKCaj7AzMHh1; mtop_partitioned_detect=1; _m_h5_tk=76f59b272e128957a06a7dc74b8791ea_1764851740944; _m_h5_tk_enc=daba197f0f8c81b25ff737ee65c47b8c; tfstk=gl0ZIN_crFLaWp6B5vUVaY_JEkzT-rJW7qwbijc01R2gCjV0uvDX6RGDBxu4Kjn66o9Og13EUZ_6BhhcuraDFLTWPfh_krvSKQD8GRFxt-AQjOlgW14DFLT5A6q9Crc_ssIUxMV8K5VcjRAUK7V4oNVinJq3Z76gorDDTWVbiZjcSofhxSw3nr4mnXAUGJVgorDmtBPxGzHtHTNujBtcaz25bBq_Ef2Foa58_lVyyJ7co2PZT8cM2Zbm85ri-rbinYrsmbE-5fTVJPGrxyVZnUvg-bmENluwUNwY02kZ0AOfDWoqi4UTzsYiTPyaqVrOMNHoTjm7Y2OkyPzgImatG_JsTVks62lfiM4a5Drr7zYRI-iIaqPqkKLEUfmonmSz3tFH-Luxbtj4jWFUFBREsHgBLf9IkdSADkquT8OTmiIYjWFUFBRFDiEOrWyW6of..; isg=BGZm3CmLM8DyYuYtZd_ZsdnCt9zoR6oB67aI91APEQlk0wbtuNVAEAmlK8_f-6IZ"
}
url='https://h5api.m.tmall.com/h5/mtop.taobao.rate.detaillist.get/6.0/'

eT = int(time.time()) * 1000
em_token = "76f59b272e12s8957a06aa7dc74b8791ea"
eC = "12574478"

for page in range(1, 4):

    print(f'正在采集第{page}页的数据内容!')

    ep_data_param = {
        "pageNo":page,
        "showTrueCount":False,
        "auctionNumId":"720936823983",   # 需按实际修改
        "pageSize":20,
        "rateType":"",
        "searchImpr":"-8",
        "orderType":"",
        "expression":"",
        "rateSrc":"pc_rate_list"
    }

    ep_data = json.dumps(ep_data_param)

    signString = em_token + "&" + str(eT) + "&" + eC + "&" + ep_data
    sign = hashlib.md5(signString.encode("utf-8")).hexdigest()

    data = {
        'jsv': '2.7.5',
        'appKey': '12574478',
        't': eT,
        'sign': sign,
        'api': 'mtop.taobao.rate.detaillist.get',
        'v': '6.0',
        'isSec': '0',
        'ecode': '1',
        'timeout': '20000',
        'type': 'jsonp',
        'dataType': 'jsonp',
        'valueType': 'string',
        'callback': 'mtopjsonp16',
        'data': ep_data
    }
    response=requests.get(url=url,headers=headers,params=data).text
    # print(response)
    # exit()
    # # 正则表达式
    str_json=re.findall(r'mtopjsonp\d+\((.*)',response)[0][:-1]
    # print(str_json)
    #把字符串数据转换成字典
    json_data=json.loads(str_json)
    # print("json_data:")
    # print(json.dumps(json_data, indent=2, ensure_ascii=False))
    # exit()

    comments_list=json_data['data']['rateList']
    # print("comments_list:")
    # print(json.dumps(comments_list, indent=2, ensure_ascii=False))
    # exit()

    # for循环遍历，提取列表里面的元素
    for index in comments_list:
        img_urls = [img for img in index["feedPicPathList"]] if "feedPicPathList" in index  else []

        dit = {
            "商品ID": index["auctionNumId"],
            "商品名称": index["auctionTitle"],
            "用户名": index['reduceUserNick'],
            "日期": index['feedbackDate'],
            "购买规格": index["skuValueStr"],
            "评论内容": index['feedback'],
            "点赞数": index['interactInfo']['likeCount'],
            "图片链接": '\n'.join(img_urls)
        }
        info.append(dit)
        # print(dit)
        # exit()

    delay = random.uniform(3, 10)
    print(f'等待{delay:.2f}秒后继续=====\n')
    time.sleep(delay)

csv_file = f"淘宝评论_{dit["商品ID"]}.csv"
df=pd.DataFrame(info,  columns=["商品ID", "商品名称", "用户名", "日期", "购买规格", "评论内容", "点赞数", "图片链接"])
df.to_csv(csv_file, encoding='utf-8-sig', index=False)