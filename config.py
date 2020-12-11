config_file_path='./config/'
txt_file_path='./txt_result/'
csv_file_path='./csv_result/'

max_task=1
ua_freq=20
login_freq=100
ua_pool=50

# bilibili data request api
data_url_root="https://api.bilibili.com/x/web-interface/archive/stat?aid={}"
# bilibili html url 
title_url_root="https://www.bilibili.com/video/av{}"  
# bilibili reply data request api
reply_url_root="https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn=1&type=1&oid={}&sort=1"