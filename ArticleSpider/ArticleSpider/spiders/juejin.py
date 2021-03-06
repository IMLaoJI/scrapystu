# -*- coding: utf-8 -*-
import scrapy
import  re
import  random
from urllib import parse
from scrapy.http import Request
from ArticleSpider.items import TuiCoolArticleItem,ArticleItemLoader
from ArticleSpider.utils.common import get_md5
# from items import ZhihuQuestionItem, ZhihuAnswerItem

class JuejinSpider(scrapy.Spider):
    name = "juejin"
    allowed_domains = ["https://juejin.im"]
    start_urls = ['http://https://juejin.im/']



    start_urls = [
        # 'https://juejin.im/',
        # 'https://juejin.im/welcome/android',
        # 'https://juejin.im/welcome/frontend',
        # 'https://juejin.im/welcome/ios',
        # 'https://juejin.im/welcome/backend',
        # 'https://juejin.im/welcome/design',
        'https://juejin.im/welcome/product',
    ]

    # def parse(self, response):
    #     pass

    # start_urls = open('topics.txt').readlines()
    user_agent_list = [
        'User-Agent:Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
        'User-Agent:Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
        'User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
        'User-Agent: Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)',
        'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
        'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko'
    ]

    def set_headers(self):
        # agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0"
        agent = self.user_agent_list[random.randint(0, 5)]
        # print (agent)
        headers = {
            "Host": "www.tuicool.com",
            'User-Agent': agent
        }
        return headers

    def start_requests(self):

        for url in self.start_urls:
            print('正在访问' + url)
            # time.sleep(5)
            yield Request(
                url=url.strip('\n'),
                headers=self.set_headers(),
                # cookies=cookielib.LWPCookieJar(filename='cookies'),
                callback=self.parse,
                meta={'page': 1}
            )

    def parse(self, response):
        """
        1. 获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2. 获取下一页的url并交给scrapy进行下载， 下载完成后交给parse
        """
        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        # print("为啥没来")
        # if response.status == 404:
        #     self.fail_urls.append(response.url)
        #     self.crawler.stats.inc_value("failed_url")
        # http: // www.tuicool.com / a / 1 / 0?lang = 0
        testUrl = "https://juejin.im/welcome/product"
        match_re = re.match("https://juejin.im/(welcome)?/({a-z}*)?", testUrl)
        if match_re:
            flag = int(match_re.group(1))
        else:
            flag = 1;
        print(flag)
        post_nodes = response.css("div.list_article_item")
        for post_node in post_nodes:
            image_url = post_node.css("div.article_thumb_image img::attr(src)").extract_first("")
            post_url = post_node.css("div.aricle_item_info div.title a::attr(href)").extract_first("")
            yield Request(url=parse.urljoin("http://www.tuicool.com/", post_url),
                          meta={"front_image_url": image_url, "flag": flag},
                          callback=self.parse_detail)

        # 提取下一页并交给scrapy进行下载
        # list_article > div:nth-child(27)
        # list_article > div:nth-child(3) > div.aricle_item_info > div.title
        # body > div.container - fluid > div.row - fluid > div.span9 > div: nth - child(6) > div > ul > li.next > a
        next_url = response.css("li.next a::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin("http://www.tuicool.com", next_url), callback=self.parse)

    def parse_detail(self, response):
        article_item = TuiCoolArticleItem()
        # 通过item loader加载item
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        flagTrue = response.meta.get("flag", "")  # 标识
        original = "http://www.tuicool.com/" + response.css("span.from a::attr(href)").extract_first("")
        item_loader = ArticleItemLoader(item=TuiCoolArticleItem(), response=response)
        item_loader.add_css("title", ".article_row_fluid div:nth-child(1) h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_date", "span.timestamp::text")
        item_loader.add_value("front_image_url", [front_image_url])
        item_loader.add_value("sites", original)
        item_loader.add_value("flag", flagTrue)
        item_loader.add_css("original", "div.source a::text")
        item_loader.add_css("tags", "span.new-label::text")
        item_loader.add_css("content", "div.article_body")
        article_item = item_loader.load_item()
























        # def parse(self, response):
    #     """
    #     提取出html页面中的所有url 并跟踪这些url进行一步爬取
    #     如果提取的url中格式为 /question/xxx 就下载之后直接进入解析函数
    #     """
    #     all_urls = response.css("a::attr(href)").extract()
    #     all_urls = [parse.urljoin(response.url, url) for url in all_urls]
    #     all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
    #     for url in all_urls:
    #         match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
    #         if match_obj:
    #             # 如果提取到question相关的页面则下载后交由提取函数进行提取
    #             request_url = match_obj.group(1)
    #             yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
    #         else:
    #             # 如果不是question页面则直接进一步跟踪
    #             yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    # def start_requests(self):
    #     return [scrapy.Request('https://juejin.im', headers=self.headers, callback=self.login)]
    #
    # def login(self, response):
    #     post_url = "https://api.leancloud.cn/1.1/login"
    #     post_data = {
    #         "username": "15605020969",
    #         "password": "jilonglong520"
    #     }
    #
    #     return [scrapy.FormRequest(
    #         url=post_url,
    #         formdata=post_data,
    #         headers=self.headers,
    #         callback=self.check_login
    #     )]
    #
    # def check_login(self, response):
    #     # 验证服务器的返回数据判断是否成功
    #     text_json = json.loads(response.text)
    #     print("dasjdsajj")
    #     if "msg" in text_json and text_json["msg"] == "登录成功":
    #         for url in self.start_urls:
    #             yield scrapy.Request(url, dont_filter=True, headers=self.headers)
    #
