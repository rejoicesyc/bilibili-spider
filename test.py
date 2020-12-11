from DecryptLogin import login
import pandas as pd 

df=pd.read_csv('./csv_result/csv_result0.csv')
print(df.info())
exit()

lg = login.Login()
infos_return, session = lg.bilibili("19921308726", "syc991112")

# print()

# _uuid=CBE61FE6-F32D-56C4-C70D-C2F91AB7EE3598522infoc; buvid3=D6DC6466-4597-42B9-932A-CAB65C3A9AFE138392infoc; sid=kzgxb9kz; DedeUserID=396830642; DedeUserID__ckMd5=68437832dbd8c4c4; SESSDATA=0bfd764a%2C1614240180%2Ccc23b*81; bili_jct=2f68193ad9de2362060d4ae3351d5861; blackside_state=1; rpdid=|(u))YYRlJ)R0J'ulm)Y))k||; LIVE_BUVID=AUTO2115987087840830; CURRENT_FNVAL=80; CURRENT_QUALITY=80; bp_video_offset_396830642=466763366264044240; PVID=2; bp_t_offset_396830642=466808957337994347; bfe_id=1e33d9ad1cb29251013800c68af42315


import requests
import bs4
import json
import fakeUaPool

ua=fakeUaPool.FakeUaPool(10)
agent=ua.get_random_ua()

headers={'user-agent ':agent}

r=requests.session().get("https://www.bilibili.com/video/BV1bA41147EQ",headers=headers)
# print(r.text)
# with open('./sample.html','w',encoding='utf-8') as f:
#     f.write(r.text)
soup=bs4.BeautifulSoup(r.text,'lxml')
# tags=soup.find_all('a',class_='tag-link')
# tags=[tag.text.strip() for tag in tags]

# disc=soup.find('div',class_="info open").text

rel_titles=soup.find_all('a',class_="title")
rel_titles=[rel_title.text for rel_title in rel_titles]
print(rel_titles)