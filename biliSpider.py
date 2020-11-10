import requests
import bs4
import random
import time

from fakeUaPool import FakeUaPool
from db import DB

class BiliSpider:
    def __init__(self,begin,end,ua_freq):
        self.url_root="https://www.bilibili.com/video/av"
        self.uaPool=FakeUaPool(50)
        self.db=DB("bili","title1")

        if begin<1 or end>10**10 or ua_freq<=0:
            print("error:args out of range!")
            exit()
        self.begin=begin
        self.end=end
        self.ua_freq=ua_freq

    def run(self):
        start_time=time.time()
        user_agent=self.uaPool.get_random_ua()
        for i in range(self.begin,self.end):
            # time.sleep(0.5)
            url=self.url_root+str(i)
            if i%self.ua_freq==0:
                user_agent=self.uaPool.get_random_ua()
                print("change ua:"+user_agent)

            # headers={'user-agent':user_agent}
            headers={'user-agent ':"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15"}
            r=requests.get(url,headers=headers)
            # print(r.text)
            soup=bs4.BeautifulSoup(r.text,'lxml')
            title=soup.select('title')[0].text

            if "视频去哪了呢" not in title:
                if '_哔哩哔哩 (゜-゜)つロ 干杯~-bilibili' in title:
                    title=title.split('_哔哩哔哩 (゜-゜)つロ 干杯~-bilibili')[0]
                elif '哔哩哔哩 (゜-゜)つロ 干杯~-bilibili' in title:
                    title=title.split('哔哩哔哩 (゜-゜)つロ 干杯~-bilibili')[0]
                self.db.insert({"title":title})
                
                print(title)
                # f.write(soup.find("meta",itemprop="datePublished")['content'])
                # print(url,r.status_code)

        print("used time:"+str(time.time()-start_time))
        print("get "+str(self.db.count_all())+" entries")
            