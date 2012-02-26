from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from hackernews.items import HackernewsItem
from readability.readability import Document
import urllib
from pyatom import AtomFeed
import datetime
import codecs
import feedparser

class HackernewsSpider(BaseSpider):
	name = "hackernews"
	hn_prefix = "http://news.ycombinator.com/"
	allowed_domains = ["ycombinator.com"]
	start_urls = [
		"http://news.ycombinator.com/over?points=100"
	]
	output_filename = "hackernews100.atom"
	items = []

	def __init__(self, name=None, **kwargs):
		super(HackernewsSpider, self).__init__(name, **kwargs)
		self.existing = feedparser.parse(self.output_filename)

	def parseContent(self, response):
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

			self.items.append(item)

	def parse(self, response):

		self.parseContent(response)

		# Use Readability to extract article body
		for item in self.items:
			found = False
			for entry in self.existing['entries']:
				if entry.link == item['link']:
					item['body'] = entry.content[0].value
					found = True

			if found:
				continue

			body = ""
			if not item['link'].endswith('.pdf'):
				html = urllib.urlopen(item['link']).read()
				body = Document(html).summary()
			item['body'] = '<a href="' + item['comment'] + '">HN Comments</a>' + body

		feed = AtomFeed(
			title = "Hacker News >100",
			subtitle = "Hacker News over 100 points",
			feed_url = "http://dannysu.com/feeds/hackernews100.atom",
			url = "http://news.ycombinator.com/over?points=100"
		)

		for item in self.items:
			feed.add(
				url = item['link'],
				title = item['title'],
				content = item['body'],
				content_type = "html",
				updated=datetime.datetime.utcnow()
			)

		f = codecs.open(self.output_filename, 'w', 'utf-8')
		f.write(feed.to_string())
