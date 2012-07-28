from scrapy.spider import BaseSpider
from scrapy.selector import XmlXPathSelector
from scrapy.http import Request 
from hackernews.items import HackernewsItem
import json
import urllib
import time
import random

class HackernewsSpider(BaseSpider):
	name = "hackernews"
	hn_prefix = "http://news.ycombinator.com/"
	allowed_domains = ["twitter.com"]
	start_urls = [
		"http://api.twitter.com/1/statuses/user_timeline.rss?screen_name=newsyc100&count=60"
	]

	def parse(self, response):
		xxs = XmlXPathSelector(response)
		tweets = xxs.select('//item/title/text()').extract()

		for t in tweets:
			title = t.replace("newsyc100: ", "")

			start_link = title.rfind("(http")
			end_link = title.find(")", start_link)
			comment_link = title[start_link+1:end_link]

			start_link = title.find("http")
			end_link = title.find(" ", start_link)
			link = title[start_link:end_link]

			title = title[0:start_link]

			item = HackernewsItem()
			item['title'] = title
			item['link'] = link
			item['comment'] = comment_link

			yield item
