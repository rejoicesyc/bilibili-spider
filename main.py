import json
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, wait, ALL_COMPLETED

from biliSpider import BiliSpider
from config import *

def set_task():
    for i in range(max_task):
        with open(config_file_path+'config{}.json'.format(str(i)),'w') as f:
            json.dump({'begin':10**8+i*(10**7),'end':10**8+(i+1)*(10**7)},f)

if __name__=="__main__":
    start_time=time.time()
    set_task()

    biliSpider=BiliSpider()
    biliSpider.run()
    # biliSpider.sub_task(0,10000060,10005000)

    print("finish.")
    print("used time:"+str(time.time()-start_time))