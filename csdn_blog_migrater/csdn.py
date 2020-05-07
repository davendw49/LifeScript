import json
import uuid
import time
import requests
import datetime
from bs4 import BeautifulSoup
from lxml import etree
import re
import argparse

def request_get(url):
    '''
    get the request's response
    para: url
    warn: you need to change the headers data
    '''
    headers = {'User-Agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
    response = requests.get(url, headers=headers, timeout=5)
    return response

def write_md(data):
    '''
    using re to convert json of blog into markdown
    para: data: response json data in api of csdn website
    '''
    invalid = r"[\/\\\:\*\?\"\<\>\|]"
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
    
class csdn():
    '''
    one csdn entity with construction parameter of userid, e.g. mine is qq_33380032
    '''
    def __init__(self, userid):
        '''
        construction function of csdn
        para: userid
        warn: the cookies need to be changed
        '''
        self.userid = userid
        self.headers =  {
            "cookie": "_33968713050-1581675381704-279219; dc_session_id=10_1581675381704.373278; __gads=ID=020aa3f4b43157e3:T=1581675383:S=ALNI_MZ5EB7qQCbHgF052OwOvq-gKPYAFA; UN=qq_33380032; Hm_ct_6bcd52f51e9b3dce32bec4a3997715ac=6525*1*10_33968713050-1581675381704-279219!5744*1*qq_33380032; _ga=GA1.2.83376576.1584521441; UserName=qq_33380032; UserInfo=a344dbf8aa8d44588b90393780d8d743; UserToken=a344dbf8aa8d44588b90393780d8d743; UserNick=davendw; AU=EAA; BT=1587992373030; p_uid=U000000; dc_sid=578d1b784327c090bfaed9d2a4fc1013; c_first_ref=www.baidu.com; c_first_page=https%3A//www.csdn.net/; Hm_lvt_6bcd52f51e9b3dce32bec4a3997715ac=1587995335,1587995728,1587997258,1588045231; announcement=%257B%2522isLogin%2522%253Atrue%252C%2522announcementUrl%2522%253A%2522https%253A%252F%252Fblog.csdn.net%252Fblogdevteam%252Farticle%252Fdetails%252F105203745%2522%252C%2522announcementCount%2522%253A0%252C%2522announcementExpire%2522%253A3600000%257D; c_ref=https%3A//blog.csdn.net/qq_33380032/article/list/2; dc_tos=q9hcyj; Hm_lpvt_6bcd52f51e9b3dce32bec4a3997715ac=1588047068"
        }
    
    def get_article_id_list(self, least_id="0"):
        '''
        get a blog list of a user
        para: least_id, start page, default in "0"
        '''
        ans_list = []
        base_url = 'https://blog.csdn.net/' + self.userid + '/article/list/'
        start_url = base_url + '1'
        now_list_id = 1
        article_num = 0
        html = request_get(start_url)
        '''
        if code==200 http response correct
        '''
        while html.status_code ==200:
            selector = etree.HTML(html.text)
            cur_article_list_page = selector.xpath('//*[@id="mainBox"]/main/div[2]')
            d = cur_article_list_page[0].xpath('//*[@id="mainBox"]/main/div[2]/div[2]/h4/a')
            l = cur_article_list_page[0].findall('data-articleid')
            for elem in cur_article_list_page[0]:
                item_content = elem.attrib
                '''
                By comparing the data obtained with the effective data in the web page, it is found that each list in article_list returns one or two extra elements, and each extra element has a style attribute. Use this feature to filter
                '''
                if item_content.has_key('style'):
                    continue
                else:
                    if item_content.has_key('data-articleid'):
                        articleid = item_content['data-articleid'].strip()
                        if int(articleid) <= int(least_id.strip()):
                            return ans_list
                        article_num += 1
                        ans_list.append(articleid)
                        print(".", end="")

            now_list_id += 1
            next_url = base_url + str(now_list_id)
            if now_list_id > 3:
                break
            html = request_get(next_url)
        print(len(ans_list), "in total")
        self.blog_list = ans_list 
        return ans_list
    
    def request_md(self, blog_id):
        """
        obtain the blogs and transfer into markdown
        para: blog_id: a blog id in self.blog_list
        """
        url = u"https://blog-console-api.csdn.net/v1/editor/getArticle?id="+str(blog_id)
        print(url)
        data = {"id": blog_id}
        reply = requests.get(url, headers=self.headers, data=data)
        print(reply)
        try:
            write_md(reply.json())
        except Exception as e:
            print("***********************************")
            print(e)
            print(url)
    
    def convert_batch(self):
        for item in self.blog_list:
            self.request_md(item)
            time.sleep(4)
    
    def convert_single(self, blog_id):
        self.request_md(blog_id)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-m', '--mode', default="all", help='mode: single blog or batch')
    parser.add_argument('-u', '--userid', help='all the mode need to input user_id, in order to activate the headers, from a safe angle')
    parser.add_argument('-l', '--least_id', default="0", help='start page')
    parser.add_argument('-b', '--blog_id', default="0", help='single blog id, if you know')
    args = parser.parse_args()
    
    if args.mode == "all":
        cd = csdn(args.userid)
        cd.get_article_id_list(args.least_id)
        cd.convert_batch()
    if args.mode == "list":
        cd = csdn(args.userid)
        print(cd.get_article_id_list(args.least_id))
    if args.mode == "single":
        cd = csdn(args.userid)
        cd.convert_single(args.blog_id)