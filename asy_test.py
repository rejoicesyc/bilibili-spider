import aiohttp
import asyncio
import bs4

# 设置请求头信息
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'

}


# 创建特殊函数，获取网页信息
async def request(url):
    async with aiohttp.ClientSession() as s:
        async with await s.get(url, headers=headers) as response:
            page_text = await response.text()
            print(page_text)
            return page_text


urls = []
url = 'https://www.bilibili.com/video/av'
for page in range(1,3):
    urls.append(url+str(page))


# 回调函数
def parse(task):
    page_text = task.result()
    # 乱码处理，这里处理乱码存在问题,可以实现replace替换保存字符
    soup=bs4.BeautifulSoup(page_text,'lxml')
    title=soup.select('title')[0].text
    print(title)


# 任务列表
tasks = []
for url in urls:
    c = request(url)
    task = asyncio.ensure_future(c)
    task.add_done_callback(parse)
    tasks.append(task)

# 创建事件循环对象
loop = asyncio.get_event_loop()
# 多任务对象注册到事件循环，并挂起
loop.run_until_complete(asyncio.wait(tasks))