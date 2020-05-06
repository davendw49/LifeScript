import json
import uuid
import time
import requests
import datetime
from bs4 import BeautifulSoup
import re

def request_blog_list(page):
    """获取博客列表
    主要包括博客的id以及发表时间等
    """
    url = f'https://blog.csdn.net/qq_33380032/article/list/{page}'
    reply = requests.get(url)
    parse = BeautifulSoup(reply.content, "lxml")
    spans = parse.find_all('div', attrs={'class':'article-item-box csdn-tracking-statistics'})
    blogs = []
    for span in spans[:3]:
        try:
            href = span.find('a', attrs={'target':'_blank'})['href']
            read_num = span.find('span', attrs={'class':'num'}).get_text()
            date = span.find('span', attrs={'class':'date'}).get_text()
            blog_id = href.split("/")[-1]
            blogs.append([blog_id, date, read_num])
        except:
            print('Wrong, ' + href)
    return blogs

def request_md(blog_id):
    """获取博客包含markdown文本的json数据"""
    url = u"https://blog-console-api.csdn.net/v1/editor/getArticle?id="+blog_id
    print(url)
    # url = f"https://mp.csdn.net/console/editor/html/{blog_id}"
    headers = {
        #"cookie": "uuid_tt_dd=10_7363320700-1563628438907-864526; dc_session_id=10_1563628438907.833516; Hm_ct_6bcd52f51e9b3dce32bec4a3997715ac=6525*1*10_7363320700-1563628438907-864526!5744*1*qq_36962569!1788*1*PC_VC; UN=qq_36962569; smidV2=20190712194742cdeda8c033ea9ef003a9a0003c79154a00358928f445b7b50; UserName=qq_36962569; UserInfo=3a33c991856940a79235b113cb42ff0d; UserToken=3a33c991856940a79235b113cb42ff0d; UserNick=%E5%AD%90%E8%80%B6; AU=5A5; BT=1566296770044; p_uid=U000000; TINGYUN_DATA=%7B%22id%22%3A%22-sf2Cni530g%23HL5wvli0FZI%22%2C%22n%22%3A%22WebAction%2FCI%2FpostList%252Flist%22%2C%22tid%22%3A%22e0a1148715d862%22%2C%22q%22%3A0%2C%22a%22%3A42%7D; ViewMode=list; aliyun_webUmidToken=T9204DD7B1A1971E571EFE43913410386D4C2C9D905BA336A2BEDBC206D; hasSub=true; c_adb=1; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1567074771,1567083797,1567083801,1567084099; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1567084279; dc_tos=px01z9",
        "cookie": "uuid_tt_dd=10_33968713050-1581675381704-279219; dc_session_id=10_1581675381704.373278; __gads=ID=020aa3f4b43157e3:T=1581675383:S=ALNI_MZ5EB7qQCbHgF052OwOvq-gKPYAFA; UN=qq_33380032; Hm_ct_6bcd52f51e9b3dce32bec4a3997715ac=6525*1*10_33968713050-1581675381704-279219!5744*1*qq_33380032; _ga=GA1.2.83376576.1584521441; UserName=qq_33380032; UserInfo=a344dbf8aa8d44588b90393780d8d743; UserToken=a344dbf8aa8d44588b90393780d8d743; UserNick=davendw; AU=EAA; BT=1587992373030; p_uid=U000000; dc_sid=578d1b784327c090bfaed9d2a4fc1013; c_first_ref=www.baidu.com; c_first_page=https%3A//www.csdn.net/; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1587995335,1587995728,1587997258,1588045231; announcement=%257B%2522isLogin%2522%253Atrue%252C%2522announcementUrl%2522%253A%2522https%253A%252F%252Fblog.csdn.net%252Fblogdevteam%252Farticle%252Fdetails%252F105203745%2522%252C%2522announcementCount%2522%253A0%252C%2522announcementExpire%2522%253A3600000%257D; c_ref=https%3A//blog.csdn.net/qq_33380032/article/list/2; dc_tos=q9hcyj; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1588047068"
    }
    data = {"id": blog_id}
    reply = requests.get(url, headers=headers, data=data)
    print(reply)
    try:
        write_hexo_md(reply.json())
    except Exception as e:
        print("***********************************")
        print(e)
        print(url)
    #print(reply.json())

def write_hexo_md(data):
    invalid = r"[\/\\\:\*\?\"\<\>\|]"
    """将获取的json数据解析为hexo的markdown格式"""
    title = data["data"]["title"]
    title = title.replace("【","[")
    title = title.replace( "】","]")
    title = title.replace(" "," ")
    title = re.sub(invalid, "-", title)
    tags = data["data"]["tags"]
    # 页面唯一标识符，用于统计系统和评论系统
    key = "key" + str(uuid.uuid4())

    name = f"{title}"
    tag = "tags:\n    - " + "\n    - ".join(tags.split(","))
    
    header = "---\n" + f"title: {title}\n" + tag + "\n" + f"key: {key}\n" + "---\n\n"

    if data["data"]["markdowncontent"].replace("@[toc]", "") != "":
        content = data["data"]["markdowncontent"].replace("@[toc]", "")
    else:
        content = data["data"]["content"].replace("@[toc]", "")

    with open(f"blogs/{name}.md", "w", encoding="utf-8") as f:
        f.write(header + content)

    print(f"写入 {name}")


def main_batch():
    """
    获取博客列表，包括id，时间
    获取博客markdown数据
    保存hexo格式markdown
    """
    blogs = []
    # for page in range(1, 3):
    #     print(page)
    #     blogs.extend(request_blog_list(page))
    f = open("list1.txt", 'r')
    for line in f:
        blogs.append((line[:-1]))
    print(blogs)
    for blog in blogs:
        blog_id = blog
        request_md(blog_id)
        time.sleep(5)

def main(id):
    request_md(id)

if __name__ == '__main__':
    # main("78274569")
    main_batch()