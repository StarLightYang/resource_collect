import re
import json
import time
import random
import hashlib
import requests
import pandas as pd
from datetime import datetime

if __name__ == '__main__':

    url = "https://h5api.m.taobao.com/h5/mtop.relationrecommend.wirelessrecommend.recommend/2.0/"
    headers = {
        'referer': 'https://s.taobao.com/',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Cookie": "thw=cn; t=cc3dccd620b0a201447a77bd7952743643; wk_cookie2=18a9082474e62c470bf416ec498fbe18; wk_unb=UUwZ9PQNjXuY%2Bg%3D%3D; _hvn_lgc_=0; havana_lgc2_0=eyJoaWQiOjI0OTk1Mjg0NDYsInNnIjoiNzIwMDc1MDk2N2YyOTMzNjFhYzY5MTczMjQ1MjFjNjEiLCJzaXRlIjowLCJ0b2tlbiI6IjEweUdCcVdKV2pudkQtOW1TaEwyY2NBIn0; lgc=%5Cu661F%5Cu5149adc; cancelledSubSites=empty; dnk=%5Cu661F%5Cu5149adc; tracknick=%5Cu661F%5Cu5149adc; sn=; aui=2499528446; cna=e79eIC+W5QsCAXFZ6lwLaUSM; _tb_token_=5504f61e33e4e; _samesite_flag_=true; unb=2499528446; uc1=cookie15=URm48syIIVrSKA%3D%3D&existShop=false&pas=0&cookie21=VFC%2FuZ9aiKCaj7AzMHh1&cookie16=Vq8l%2BKCLySLZMFWHxqs8fwqnEw%3D%3D&cookie14=UoYbyGQojafZYA%3D%3D; uc3=lg2=URm48syIIVrSKA%3D%3D&vt3=F8dD2fntbzlVNoH8Oq0%3D&id2=UUwZ9PQNjXuY%2Bg%3D%3D&nk2=s0%2BKohE%2B9Q%3D%3D; csg=f820cfaf; cookie17=UUwZ9PQNjXuY%2Bg%3D%3D; skt=fad782554448d26a; cookie2=1a6305848c490bca85df23b5267670a3; existShop=MTc1Mzg1NjM0Ng%3D%3D; uc4=nk4=0%40sTB8t8nxvWY1a3P7H4m8xGOj&id4=0%40U27GhYUdpL13FrprCcCCzfPWdkig; _cc_=URm48syIZQ%3D%3D; _l_g_=Ug%3D%3D; sg=c6b; _nk_=%5Cu661F%5Cu5149adc; cookie1=U7T0f3Z5yjBSvPA8bEVANEaogzh2MAdn%2BDuG99UG8W0%3D; sgcookie=E100v2hS0vMpDIJjJNcdfeeyZEPT8NZaialBT7PPTqOz5X5CBV5E5Na21mfHMW5tqgOYtXM9oAmFgIoNQ4v5envGhTvFX3SQnpnKgqFHcakoyQZGw85jCe0O5SRs36L99ytx; havana_lgc_exp=1784960346535; sdkSilent=1753885146534; havana_sdkSilent=1753885146534; xlly_s=1; sca=6d78a824; mtop_partitioned_detect=1; _m_h5_tk=25923d057bf9eab72143e5778aad2dd2_1753870037413; _m_h5_tk_enc=140d86a55ffec129d11c93463accca0b; tfstk=goEnKxcjhyuQ0s1tWliCRypJ64_tdDiSi7K-w0hP7fl6J0QQeY4gh7cdFwiLSbVasX-ddJFiU727J9gROLvQjSxJv6_QU3m-4sCADieQp0iPM4W755cIFRlPB28YuSqn4sCAXFpZR6nzwRY65OYZhfkEUbuFIFko_v8zaXuw_xDj40Pr8FuZnxkrUH-zQODS_bor47oNIYGZaXoBPjVQMl5uVPI_CraYjv0ngRbX43qwD2c4LfxPglDhGjyEs3-riT5zFR2dtnwtAlFmHWIwxS2Uu7z4_Gxn5yygqqZWTOorzPUx-PfeqfEKEqorSL-zIDlsluoV0CD_7JUzAWvk4vZLD4cjST-SycrxurPHFtwZYYPSluCXAXyzhoaxmgxZx4SzzF8qEXtSQTEwPUgECAcxVkrkbb1MvwXGIEsZ8AMCjOXMPUgECAcAIOY272ksdGf..; isg=BNjYctClBDKXzCfoE8VoYzdSqQZqwTxLIG5-JBLJLJPErXiXutGc28OL5eWdvfQj"
    }

    # eM = eE(em.token + "&" + eT + "&" + eC + "&" + ep.data)
    em_token = "25923d057bf9eab7dd2143e5778aad2dd2"
    eC = "12574478"
    eT = int(time.time()) * 1000
    # ep_data = '{"appId":"34385","params":"{\\"device\\":\\"HMA-AL00\\",\\"isBeta\\":\\"false\\",\\"grayHair\\":\\"false\\",\\"from\\":\\"nt_history\\",\\"brand\\":\\"HUAWEI\\",\\"info\\":\\"wifi\\",\\"index\\":\\"4\\",\\"rainbow\\":\\"\\",\\"schemaType\\":\\"auction\\",\\"elderHome\\":\\"false\\",\\"isEnterSrpSearch\\":\\"true\\",\\"newSearch\\":\\"false\\",\\"network\\":\\"wifi\\",\\"subtype\\":\\"\\",\\"hasPreposeFilter\\":\\"false\\",\\"prepositionVersion\\":\\"v2\\",\\"client_os\\":\\"Android\\",\\"gpsEnabled\\":\\"false\\",\\"searchDoorFrom\\":\\"srp\\",\\"debug_rerankNewOpenCard\\":\\"false\\",\\"homePageVersion\\":\\"v7\\",\\"searchElderHomeOpen\\":\\"false\\",\\"search_action\\":\\"initiative\\",\\"sugg\\":\\"_4_1\\",\\"sversion\\":\\"13.6\\",\\"style\\":\\"list\\",\\"ttid\\":\\"600000@taobao_pc_10.7.0\\",\\"needTabs\\":\\"true\\",\\"areaCode\\":\\"CN\\",\\"vm\\":\\"nw\\",\\"countryNum\\":\\"156\\",\\"m\\":\\"pc\\",\\"page\\":2,\\"n\\":48,\\"q\\":\\"%E7%AC%94%E8%AE%B0%E6%9C%AC%E7%94%B5%E8%84%91\\",\\"qSource\\":\\"url\\",\\"pageSource\\":\\"a21bo.jianhua/a.search_history.d1\\",\\"channelSrp\\":\\"\\",\\"tab\\":\\"all\\",\\"pageSize\\":\\"48\\",\\"totalPage\\":\\"100\\",\\"totalResults\\":\\"21492\\",\\"sourceS\\":\\"0\\",\\"sort\\":\\"_coefp\\",\\"bcoffset\\":\\"-12\\",\\"ntoffset\\":\\"13\\",\\"filterTag\\":\\"\\",\\"service\\":\\"\\",\\"prop\\":\\"\\",\\"loc\\":\\"\\",\\"start_price\\":null,\\"end_price\\":null,\\"startPrice\\":null,\\"endPrice\\":null,\\"categoryp\\":\\"\\",\\"ha3Kvpairs\\":null,\\"myCNA\\":\\"e79eIC+W5QsCAXFZ6lwLaUSM\\",\\"screenResolution\\":\\"1707x1067\\",\\"userAgent\\":\\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36\\",\\"couponUnikey\\":\\"\\",\\"subTabId\\":\\"\\",\\"np\\":\\"\\"}"}'

    dataAllContact = []
    # 获取前2页数据
    for page in range(1, 3):

        print(f'正在采集第{page}页的数据内容!')

        ep_data_param = {"page":page,"device":"HMA-AL00","isBeta":"false","grayHair":"false","from":"nt_history","brand":"HUAWEI","info":"wifi","index":"4","rainbow":"","schemaType":"auction","elderHome":"false","isEnterSrpSearch":"true","newSearch":"false","network":"wifi","subtype":"","hasPreposeFilter":"false","prepositionVersion":"v2","client_os":"Android","gpsEnabled":"false","searchDoorFrom":"srp","debug_rerankNewOpenCard":"false","homePageVersion":"v7","searchElderHomeOpen":"false","search_action":"initiative","sugg":"_4_1","sversion":"13.6","style":"list","ttid":"600000@taobao_pc_10.7.0","needTabs":"true","areaCode":"CN","vm":"nw","countryNum":"156","m":"pc","n":48,"q":"%E7%9C%BC%E5%BD%B1%E7%9B%98","qSource":"url","pageSource":"a21bo.jianhua/a.search_paste.0","channelSrp":"","tab":"all","pageSize":48,"totalPage":100,"totalResults":4800,"sourceS":"0","sort":"_coefp","bcoffset":"","ntoffset":"","filterTag":"","service":"","prop":"","loc":"","start_price":None,"end_price":None,"startPrice":None,"endPrice":None,"itemIds":None,"p4pIds":None,"p4pS":None,"categoryp":"","ha3Kvpairs":None,"myCNA":"e79eIC+W5QsCAXFZ6lwLaUSM","screenResolution":"1707x1067","userAgent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36","couponUnikey":"","subTabId":"","np":""}

        ep_data_1 = {
            "appId":"34385",
            "params":json.dumps(ep_data_param)
        }
        ep_data = json.dumps(ep_data_1).replace(" ", "")
        signString = em_token + "&" + str(eT) + "&" + eC + "&" + ep_data
        sign = hashlib.md5(signString.encode("utf-8")).hexdigest()
        # print ("sign:")
        # print (sign)
        # exit()

        params = {
            'jsv': '2.7.4',
            'appKey': '12574478',
            't': eT,
            'sign': sign,
            'api': 'mtop.relationrecommend.wirelessrecommend.recommend',
            'v': '2.0',
            'timeout': '10000',
            'type': 'jsonp',
            'dataType': 'jsonp',
            'callback': 'mtopjsonp5',
            'data': ep_data,
            'bx-ua':  '231!FoR3b4mUsT0+jmeDd477jGBjUGg0uSOn+fYFmLQQwGng0wmHntUSK+2ttWIwYfiRlXeQ+thKJXIvfegh2cGUuRIvbZ9fhRfZbrcyCwJp1Tn/1O6FZpEGdNopwjVxT/gkc2+fG9NEGeFMxJZKFjttf2lq8JGP12qukMjMOVIw7I6onsL8PCXg2xr6zTLxETpXTlz4uIqOPy2NLsEa9JLvzhoqmpGrY5NQqno3V+Z5ZcibnzjahH6O3kmo0Q3oyE+jauHhUllP2+WGHkE+++3+qCS4+ItNZk6/GjtCo+nHNnIno8U4bYahZFS1dWvpqbwJpgane0l0j26FSV7xceTrXG4fI2kowkxuStGlvqAYLXU8szjTCezzXpkIEkMYuypKFh7I798t77wsFuGwC/wpcFKQo6AIAl8wXPJd7iK30zPzrOH8rQXylNgEUz09Of2UeZwz1KLcRhal4pabg3tNuda9Z3UItz/bnLpatMuS4mrzMDqRZwU/tZLnqbgtM70M46mq48XwD+ufUhwHQDdiPr+0Ej6YTIy36aIKdmKIkHIS8ra3iFSjFNa1d1c+SFsAdDsLDJwFVC5tOtHRE6aXcDaZwB56fBKdjA3AU8xjn4vT8d3bHH002LvX13nvKQTb6vPWowaieGzCtTcx4wZSA8vVCMadNYHpYCVp5qwU6ChmlnFB+WcL6H/RvbBwTJ0PM32IVTvQ/+Ksk1vMkcj41F7Iz/By2WPlD6sE6seBFPJC5l36FYUNicHPlkl2zMRfpYei9yNgFqqVBvD8cyeveibz8w2GkhZMEX+Azp41IrRCufUiY5O9/khy+jGd/QO1lxAAYTTjsF1CZgtx//4jiAuTAN/XwM8QyCD6A/Zb10CPyjWV7Ugaelump8AjWsHwVK3bfouppRQkxWpGXemy59LlfUpuDypuWyntLJuxwDF3IwH+U/lSz8dcu6efxqPoD93jeSFM5Oo9++fVv/MqroTDzGC/4Ig/YUW6pA6ciIjFOKUfIAZVAWFOja3PzhOyC+iu1UFuDUV3nmarMzAroaLDrXhiMqTayPklpNFJUDctXG8C8ZYiIkaYi69Co4v/dOJ5pMjcKEFjwQjvrAd/KcyQm2yjE8PanOJuV6t3KPz5FZHiHpjmbqSOaky61NbJBGZFLjp/C8flJqfBm1ysh0p77xzE55zF1NAaNY1FQtoPYle5c/yYrL1CCAf3HbXfV32fWsyR9zYxvb16xYaSnVQjbCmIeBGMPwvDdjlhjdLmMCC74icKMcKlb8XZ0W1VGlinvZtaJWnn7hKCL/LKDsIH4lr5kMVh9HNH5lbnTt8tfVm5n/87aVXDqAKTr6mi1FWLfLKTliht9dOjN8HxofG5+dknYFihwENUNgjgbx8GgvL236Ft42PMK+VrFii5fEgXv1NC/LO4Xu9Y0JkdtgpRIRUHdZn7Ao+Quce7FYcAzK8HX8CZp0NyMuxHdAZXQ/wBeDFRBJWHftbMvF2P7n5IwbDP',
            'bx-umidtoken': 'T2gAUOqWDJWn_6yf9VkQn6uyMetFBHgvIPJ4g42Bk598PUHGAqOYDTBXqSKkAe55LoA=',
            'bx_et': 'g3gqwC_G-ELVw_wYm4aNUeGzP8UY-PJBuVw_sfcgG-20hfVg7YD6M-GMHAuaEfnXMl9A_s3rLN_XHnhG7PaMdpTBRjhbWPvBjkQYH-FtZRA7mtl0ks4MdpTCV_qvhPD_GXexzgVLESVgslAzEWV_S5bmI8qutW60SADgqaV3g5XcoZ2uq8FgSRDgSQzue5agIX-xHABQtoA9-d2-EBNT0Jc0Uwl-zSqcDj2PSN0rmoyhP87GS4Pm_qM2ww-_KDebA8HkPZzZZ5kUTxWkUPcrk2rooLQZLYo3z7nJQGyEjjiKjuRDobz43ku7VsjaucDx7onV6BhuoYnLpoxJe7ujRlyL4TvmNby0YckXeN2jYbDzA465Rzcn4zSyjOFux5gt0Ojam7FzdQRzbLcCxu4IMFIOXuq3aJOYjGITm7FzdQRPXGEA-7yBMlf..'
        }

        response = requests.get(url=url, params=params, headers=headers)
        """获取数据"""
        # 获取响应的文本数据
        text = response.text
        # print(text)
        # exit()

        str_json = re.findall(r'mtopjsonp\d+\((.*)', text)[0].replace(")", "")
        json_data = json.loads(str_json)
        itemsArray = json_data["data"]["itemsArray"]
        # print (len(itemsArray))
        # print (json.dumps(itemsArray[0], indent=2, ensure_ascii=False))
        # exit()

        for item in itemsArray:
            if "item_id" in item:
                dataDict = {
                    "商品ID": item.get("item_id", ""),
                    "标题": item.get("title", "").replace("<span class=H>", "").replace("</span>", ""),
                    "当前价": item.get("price", ""),
                    "累计销量": item.get("realSales", ""),
                    "店铺名": item.get("nick", ""),
                    "所在地": item.get("procity", ""),
                    "商店标签": item.get("shopTag", ""),
                    "抓取时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                dataAllContact.append(dataDict)

        delay = random.uniform(3, 10)
        print(f'等待{delay:.2f}秒后继续=====\n')
        time.sleep(delay)

# print ("dataAllContact:")
# print (json.dumps(dataAllContact, indent=4, ensure_ascii=False))
# exit()

df=pd.DataFrame(dataAllContact,  columns=["商品ID", "标题", "当前价", "累计销量", "店铺名", "所在地", "商店标签", "抓取时间"])
df.to_csv('淘宝数据.csv', encoding='utf-8-sig', index=False)

