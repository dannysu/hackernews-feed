from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request 
from hackernews.items import HackernewsItem

class HackernewsSpider(BaseSpider):
	name = "hackernews"
	hn_prefix = "http://news.ycombinator.com/"
	allowed_domains = ["ycombinator.com"]
	start_urls = [
		"http://news.ycombinator.com/over?points=100"
	]
	hn_domain = 'http://news.ycombinator.com'

	def parse(self, response):
		hxs = HtmlXPathSelector(response)
		links = hxs.select('//td[@class="title"]')
		subtexts = hxs.select('//td[@class="subtext"]/a')

		for l, s in zip(links, subtexts):
			a = l.select('a')
			src = l.select('span')
			if len(a) < 1:
				continue

			title = a[0].select('text()').extract()[0]
			if len(src) == 1:
				title += src.select('text()').extract()[0]
			else:
				title += " (hackernews) "
			link = a.select('@href').extract()[0]
			if link.startswith('/'):
				continue
			if not link.startswith('http://') and not link.startswith('https://'):
				link = self.hn_prefix + link

			item = HackernewsItem()
			item['title'] = title
			item['link'] = link

			for a in s.select('@href').extract():
				if a.startswith('item?'):
					item['comment'] = self.hn_prefix + a

			yield item

		# only parse first 2 pages of news
		if response.url in self.start_urls and len(links) == len(subtexts) + 1:
			yield Request(
				url = self.hn_domain + links[-1].select('.//a/@href')[0].extract()
			)
