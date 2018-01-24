# -*- coding: utf-8 -*-
__author__ = 'bobby'

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "jobbole"])
# execute(["scrapy", "crawl", "qiushibaike"])
# execute(["scrapy", "crawl", "zhihu"])
# execute(["scrapy", "crawl", "juejin"])
# execute(["scrapy", "crawl", "tuicool"])
# execute(["scrapy", "crawl", "lagou"])
execute(["scrapy", "crawl", "cloudMusicArtistSpider"])
# execute(["scrapy", "crawl", "jwc.jmu.edu.cn"])