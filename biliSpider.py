import requests
import bs4
import time
import json
import sys
import csv
import traceback
from DecryptLogin import login
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

from fakeUaPool import FakeUaPool
from db import DB
from config import *

# TODO: 1.get fake cookie to speed up spider

class BiliSpider:
    def __init__(self):
        self.data_url_root=data_url_root
        self.title_url_root=title_url_root 
        self.reply_url_root=reply_url_root

        self.uaPool=FakeUaPool(ua_pool)
        self.db=DB("bilibili","data")

        self.ua_freq=ua_freq
        self.login_freq=login_freq
        self.max_task=max_task

        self.config_file_path=config_file_path
        self.txt_file_path=txt_file_path
        self.csv_file_path=csv_file_path

        self.execute=True

    def bili_login(self):
        lg = login.Login()
        infos_return, session = lg.bilibili("19921308726", "syc991112")
        return session

    def get_html(self,av,headers):
        url=self.title_url_root.format(str(av))

        r=requests.get(url,headers=headers)
        # print(r.text)
        soup=bs4.BeautifulSoup(r.text,'lxml')

        # get video title
        title=soup.select('title')[0].text

        try:
            if "视频去哪了呢" not in title and "出错啦" not in title and "bilibili.com" not in title:
                if '_哔哩哔哩 (゜-゜)つロ 干杯~-bilibili' in title:
                    title=title.split('_哔哩哔哩 (゜-゜)つロ 干杯~-bilibili')[0]
                elif '哔哩哔哩 (゜-゜)つロ 干杯~-bilibili' in title:
                    title=title.split('哔哩哔哩 (゜-゜)つロ 干杯~-bilibili')[0]

                # get published date
                av_time=soup.find("meta",itemprop="datePublished")['content']

                # get video tags
                tags=soup.find_all('a',class_='tag-link')
                tags=[tag.text.strip() for tag in tags]

                # get video discreption
                disc=soup.find('div',class_="info open").text

                # get relative video titles
                rel_titles=soup.find_all('a',class_="title")
                rel_titles=[rel_title.text.strip() for rel_title in rel_titles]

                return title,av_time,tags,disc,rel_titles

            elif "出错啦" in title or "bilibili.com" in title:
                print("\033[1;31manti spider.\033[0m")
                print(title)
                return -1
            else:
                return None
        except:
            print(title)
            traceback.print_exc()
            return -1

    def get_data(self,av,headers):
        url=self.data_url_root.format(str(av))

        data=requests.get(url,headers=headers).json()
        try:
            if data['code']==0:
                return data['data']
            else:
                return None
        except:
            print(data)
            traceback.print_exc()
            return -1

    def get_reply(self,av,headers):
        url=self.reply_url_root.format(str(av))

        r=requests.get(url,headers=headers)
        reply=r.json()
        re_list=[]
        # print(reply)

        try:
            if reply!=None and 'code' in reply and reply['code']==0 and \
                        'data' in reply and 'replies' in reply['data'] and reply['data']['replies']:
                n=min(len(reply['data']['replies']),5)
                for i in range(n):
                    r=reply['data']['replies'][i]["content"]["message"]
                    re_list.append(r)

            elif 'code' in reply and '请求被拦截' in reply['message']:
                print("\033[1;31manti spider.\033[0m")
                print(reply)
                return -1

            if len(re_list)!=0:
                return re_list
            else:
                return None
        except:
            print(reply)
            traceback.print_exc()
            return -1

    def get_task(self):
        config_data=[]
        for i in range(max_task):
            with open(self.config_file_path+'config{}.json'.format(str(i)),"r") as f:
                data=json.load(f)
                config_data.append((i,data['begin'],data['end']))
        
        return config_data

    def write_config(self,task_index,av,end):
        with open(self.config_file_path+"config{}.json".format(str(task_index)),'w') as f:
            json.dump({"begin":av,"end":end},f)

    def write_txt(self,task_index,title,reply):
        with open(self.txt_file_path+"txt_result{}.txt".format(str(task_index)),'a+',encoding='utf-8') as f:
            result='{}\n'.format(title)
            for each in reply:
                result+='{}\n'.format(each)
            result+=(1024-len(result))*" "
            f.write(result+"\n")

    def write_csv(self,task_index,html,reply,data):
        try:
            with open(self.csv_file_path+"csv_result{}.csv".format(str(task_index)),'a+',encoding='utf-8') as f:
                writer=csv.writer(f)
                entry=html+[
                    data['aid'],
                    data['view'],
                    data['danmaku'],
                    data['reply'],
                    data['favorite'],
                    data['coin'],
                    data['share'],
                    data['like']
                ]
                if reply:
                    entry.append(reply)
                writer.writerow(entry)
        except:
            traceback.print_exc()

    def insert_db(self,html,reply,data):
        self.db.insert({
            "title":html[0],
            "time":html[1],
            "tag":html[2],
            "discreption":html[3],
            "rel_title":html[4],
            'aid':data['aid'],
            'view':data['view'],
            'danmaku':data['danmaku'],
            'reply':data['reply'],
            'favorite':data['favorite'],
            'coin':data['coin'],
            'share':data['share'],
            'like':data['like'],
            'reply':reply
        })

    def sub_task(self,task_index,begin,end):
        print("begin task{}".format(task_index))
        av=begin
        end=end
        user_agent=self.uaPool.get_random_ua()

        html=None
        reply=None
        data=None

        try:
            while av<end and self.execute:
                # time.sleep(0.5)
                if av%self.ua_freq==0:
                    user_agent=self.uaPool.get_random_ua()
                    print("\033[1;33mchange ua : {}\033[0m".format(user_agent))

                # if av%self.login_freq==0:
                #     self.bili_login()

                headers={'user-agent':user_agent}
                # headers={'user-agent ':"Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.15 (KHTML, like Gecko) Chrome/24.0.1295.0 Safari/537.15"}

                html=self.get_html(av,headers)
                data=self.get_data(av,headers)
                reply=self.get_reply(av,headers)

                spider_result=[html,data,reply]

                if -1 not in spider_result:
                    if not all(spider_result)==None and html:
                        print("\033[1;32mav{}\033[0m {}".format(str(av),html[0]))
                        # print(html)
                        # print(data)
                        # print(reply)
                        # self.write_csv(task_index,html,reply,data)
                        self.insert_db(html,reply,data)
                else:
                    break

                av+=1
                time.sleep(0.5)
            # print("get "+str(self.db.count_all())+" entries")
            self.write_config(task_index,av,end)

        except Exception:
            self.write_config(task_index,av,end)

            traceback.print_exc()
            print(html)
            print(reply)
            print(data)
            print("exit")
            sys.exit()
    
    def run(self):
        thread_task_list=[]
        config_data=self.get_task()
        # print(config_data)

        try:
            p=ThreadPoolExecutor(max_workers=self.max_task)
            for task_index,begin,end in config_data:
                if begin<1 or end>10**10 or self.ua_freq<=0:
                    print("error:args out of range!")
                    exit()
                task=p.submit(self.sub_task,task_index,begin,end)
                thread_task_list.append(task)

            while not all([task.done() for task in thread_task_list]):
                time.sleep(10)
            
        # catch KeyboardInterrupt
        except: 
            self.execute=False

            wait(thread_task_list,return_when=ALL_COMPLETED)