# BGnet : Bilibili-style Comment Generator



#### 1. pj目标

``bilibili.com``是国内知名的视频弹幕网站，虽然网站的主要目的是展示视频，但是网站为了提高用户粘性，加强用户反馈的获取与交流，每一个视频都有大量可以获取的文本信息，主要包括视频标题、简介、播放量等数据、用户评论、弹幕文本、相关推荐视频标题，这些文本都是进行分析的数据来源。

基于网站的上述特性，我们小组的目标是获取视频的相关文本信息，试图生成符合用户习惯的评论。我的工作是网站数据采集以及简单的数据统计。

#### 2. 基本页面信息获取

处于性能考虑，直接抓取html页面不一定能获取所有的数据，尤其是访问量高的网站通常采用异步数据加载的方式，一方面将网站的请求流量分散处理，另一方面可以便于播放量等数据的实时更新。我们的首要目标是区分html页面数据和异步加载的数据。

我们随便打开一个页面，获取它的url（红框部分）：

<img src="C:\Users\大菠萝\AppData\Roaming\Typora\typora-user-images\image-20201218093944886.png" alt="image-20201218093944886" style="zoom: 50%;" />

编写一个简单的程序获取请求这个url可以得到的数据，并且将它写入``demo.html``以便后续分析。

然后通过插件``live server``预览这个页面，可以发现与原来网站显示的页面有一定的区别：

![image-20201218105959284](C:\Users\大菠萝\AppData\Roaming\Typora\typora-user-images\image-20201218105959284.png)

所以我们可以在这个页面获得的信息是标题、简介、视频标签、推荐视频标题。但是下面绿框部分也就是我们最关心的评论信息没有显示，那么就可以基本确定评论是通过异步加载的方式获取的，我们需要找到相关的请求api以获得这部分的信息。

<img src="C:\Users\大菠萝\AppData\Roaming\Typora\typora-user-images\image-20201218134532977.png" alt="image-20201218134532977" style="zoom:50%;" />

参考https://github.com/fython/BilibiliAPIDocs这个开源项目，里面收集了``bilibili.com``的公开的api接口，可以找到我们需要的api参数规则，根据这些字段很容易构造出我们的请求url：``https://api.bilibili.com/x/v2/reply?jsonp=jsonp&pn=1&type=1&oid={}&sort=1``，注意为了获得优质的评论，最后加上了sort字段为1，让服务器帮我们从高赞评论排序下来，减少本机计算资源的消耗。

最终我们确定通过``https://www.bilibili.com/video/av{}``、``https://api.bilibili.com/x/web-interface/archive/stat?aid={}``以及上述的评论获取的api共三个rul获取视频相关的各种信息，整个爬虫的设计图如下：

<img src="C:\Users\大菠萝\AppData\Roaming\Typora\typora-user-images\image-20201218143709337.png" alt="image-20201218143709337" style="zoom:67%;" />

本系统设计主要包括4个模块：

1. **task pool**：获取目标url，然后通过接口将url队列分配给**spider engine**。
2. **spider engine**：与服务器进行交互，发送请求，接收应答数据，传送给**spider parser**。
3. **spider parser**：解析获取的xml数据或json数据，传送给**databse**。
4. **database**：mongodb数据库，存储获取的数据。

效果图如下：

- 性能截图：

<img src="C:\Users\大菠萝\AppData\Roaming\Typora\typora-user-images\image-20201205160534834.png" alt="image-20201205160534834" style="zoom: 50%;" />

- 命令行输出：

![](C:\Users\大菠萝\AppData\Roaming\Typora\typora-user-images\image-20201211212357430.png)

- 数据库表项：

<img src="C:\Users\大菠萝\AppData\Roaming\Typora\typora-user-images\image-20201218140003111.png" alt="image-20201218140003111" style="zoom:50%;" />

#### 3. 进一步的设计

前面的系统已经成功获取到了数据，但是依然存在下面的问题：

1. 缺少异常处理，网络数据异常会导致爬虫停止
2. 如果使用校园网爬虫虽然带宽较大，但是容易被反爬虫
3. 没有应对反爬虫的策略
4. 不具备高速爬行的能力

基于上述问题，新的设计如下图：

<img src="C:\Users\大菠萝\AppData\Roaming\Typora\typora-user-images\image-20201218152824239.png" alt="image-20201218152824239" style="zoom:67%;" />

主要的改进在下面几个方面：

1. **thread sipder engine**：将爬虫引擎改为多线程模型，因为爬虫是io繁忙而cpu空闲的任务，大量的时间用于网卡的收包和发包，所以多线程能够很好地提高效率。

2. 针对反爬虫的检测：

   api返回的数据为json格式，经过实验出现反爬虫可以通过查看code字段，如果code等于0则说明数据被正确返回，不等于0则是出现了异常，检测起来比较简答。

   html页面的异常，在实验中发现的异常有2种：

   + title字段提取之后得到 *“视频去哪了呢？_哔哩哔哩 (゜-゜)つロ 干杯~-bilibili”* ，这一类属于视频号不存在，或者视频已经下架造成的异常，不需要理会，继续爬行即可。

   + title字段显示 *"出错啦"* 或者一串乱码，这就证明我们的请求已经被反爬虫机制检测到，甚至当前ip已经被禁封，需要及时修改爬行请求的参数。

3. 针对反爬虫的策略：**proxy pool** & **ua pool**

   + 调用``fake_useragent``库，获取大量虚假``user-agent``，在爬行过程中频繁更换。

   - 使用代理，代理的基本思路是使用部署在互联网上的代理服务器，我们的系统在请求的过程中不直接向目标域名请求，而是将请求包发送给代理，让代理帮助我们用自己的ip发送出请求，这样可以解决禁封ip的反爬虫措施。实践中我使用了github上的开源代理池https://github.com/jhao104/proxy_pool，这个代理通过部署在本机的爬虫向添加到配置中的免费代理服务器发送请求，确认代理服务器是否可以使用，可以就存入数据库，以后定期请求新的代理服务器并检查数据库中的服务器是否还可以使用。再通过在本机特定端口提供服务api的方式允许其他进程获取可用的代理地址。

实验过程中发现，尽管使用了非常优秀的开源项目，我们在请求数据，尤其是两个api的数据时似乎更容易被反爬虫，程序在运行过程中大量的数据包用于尝试和更换代理，而不是像预期那样大量地请求数据，推测可能是由于免费代理质量不佳或者目标网站针对这些免费代理制定了反爬虫策略，或许采用付费代理可以获得较好效果。最终我们的数据还是通过单线程增大爬虫间隔时间爬取的，经过实验间隔时间略大于1秒可以稳定长时间爬取。

#### 4. 统计结果

- 视频标签词云

视频标签的作用是当创作者在投稿的时候为了帮助推荐系统分析自己的视频而选用的可以反应视频主题的文本词汇，视频标签相当于已经完成分词的文本，可以直接用于词频统计，绘制的词云图片如下，可以一定程度上体现爬取视频的主题，我们可以看到出现频率较高的是 *“游戏”*、*“生活”* 等主题。

<img src="C:\Users\大菠萝\AppData\Roaming\Typora\typora-user-images\image-20201218190704484.png" alt="image-20201218190704484" style="zoom: 67%;" />

- 推荐视频标题与原视频标题相关度

使用``tf-idf``计算网站推荐视频与原视频标题的相关度：

<img src="C:\Users\大菠萝\AppData\Roaming\Typora\typora-user-images\image-20201218190543019.png" alt="image-20201218190543019" style="zoom:67%;" />

- 评论与标题相关度

我们通过``tf-idf``，计算评论与标题的相似度，可以看到大部分的评论相似度很低，甚至大量视频的评论完全没有相似度：

<img src="C:\Users\大菠萝\AppData\Roaming\Typora\typora-user-images\image-20201218185524872.png" alt="image-20201218185524872" style="zoom:67%;" />

我们将相似度为0的评论剔除，以评论的点赞排名单独作图，比较赞数不同的评论与其相似度，似乎是关系不大，这也符合我们对b站的认知，得到大家共识的评论不一定和视频有很大关系，不过不排除视频标题与视频没有直接关联的情况：

<img src="C:\Users\大菠萝\AppData\Roaming\Typora\typora-user-images\image-20201218184533546.png" alt="image-20201218184533546" style="zoom:67%;" />



