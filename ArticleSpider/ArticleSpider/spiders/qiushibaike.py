# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from items import QiushibaikeItem
import  re
from urllib import parse
from items import ArticleItemLoader
from utils.common import get_md5
import  random
from scrapy.http import Request
class QiushibaikeSpider(scrapy.Spider):
    name = "qiushibaike"
    allowed_domains = ["http://www.qiushibaike.com"]
    # start_urls = ['http://http://www.qiushibaike.com/']

    # start_urls = [
    #     "http://www.qiushibaike.com/8hr/page/%s" % i for i in range(1, 50)
    # ]

    start_urls = [
        # 'http://www.qiushibaike.com/',
        'http://www.qiushibaike.com/hot/',
        # 'http://www.qiushibaike.com/imgrank/',
        # 'http://www.qiushibaike.com/text/',
        # 'http://www.qiushibaike.com/history/',
        # 'http://www.qiushibaike.com/pic/',
        # 'http://www.qiushibaike.com/textnew/',
    ]


    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Cache-Control": "max-age=0",
        "Host": "www.qiushibaike.com",
        "Proxy-Connection": "keep-alive",
        "Referer": "http://www.qiushibaike.com/",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/40.0.2214.111 Chrome/40.0.2214.111 Safari/537.36"
    }


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
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Cache-Control": "max-age=0",
            "Host": "www.qiushibaike.com",
            "Proxy-Connection": "keep-alive",
            "Referer": "http://www.qiushibaike.com/",
            "Host": "http://www.qiushibaike.com/",
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
        testUrl = "http://www.qiushibaike.com/textnew/"
        match_re = re.match("^http://www.qiushibaike.com/(\w+)?.*$", testUrl)
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
        article_item = QiushibaikeItem()
        # 通过item loader加载item
        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        flagTrue = response.meta.get("flag", "")  # 标识
        original = "http://www.tuicool.com/" + response.css("span.from a::attr(href)").extract_first("")
        item_loader = ArticleItemLoader(item=QiushibaikeItem(), response=response)
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
        yield article_item



    def parse(self, response):

        xhs = Selector(response).xpath('//div[@class="article block untagged mb15"]')


        for xh in xhs:
            item = QiushibaikeItem()
            item['author'] = xh.xpath('div/a[2]/h2/text()').extract_first()
            item['content'] = xh.xpath('//*[@class="article block untagged mb15"]/a[1]/div/span').xpath("string(.)").extract_first().strip()
            item['haoxiao_num'] = xh.xpath('//*[@class="article block untagged mb15"]/div[2]/span[1]/i/text()').extract_first()
            item['comment_num'] = xh.xpath('//*[@class="article block untagged mb15"]/div[2]/span[2]/a/i/text()').extract_first()
            textUrl = xh.xpath('//*[@class="article block untagged mb15"]/a[1]/@href').extract_first()
            match_re = re.match("^/article/(\d+)$", textUrl)
            if match_re:
                flag = int(match_re.group(1))
            else:
                flag = 1;
            print(flag)
            item['id'] =flag
            yield item

