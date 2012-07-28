# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from readability.readability import Document
import urllib
from pyatom import AtomFeed
import datetime
import codecs
import feedparser

class HackernewsPipeline(object):
	output_filename = "hackernews100.atom"

        def __init__(self):
                dispatcher.connect(self.spider_opened, signal=signals.spider_opened)
                dispatcher.connect(self.spider_closed, signal=signals.spider_closed)
		self.existing_feed = feedparser.parse(self.output_filename)

	def spider_opened(self, spider):
		self.feed = AtomFeed(
			title = "Hacker News >100",
			subtitle = "Hacker News over 100 points",
			feed_url = "http://feeds.dannysu.com/hackernews100.atom",
			url = "http://news.ycombinator.com/over?points=100"
		)

	def spider_closed(self, spider):
		f = codecs.open(self.output_filename, 'w', 'utf-8')
		f.write(self.feed.to_string())

	def process_item(self, item, spider):
		found = False
		for entry in self.existing_feed['entries']:
			if entry.link == item['link']:
				item['body'] = entry.content[0].value
				found = True

		if not found:
			body = ""
			if not item['link'].endswith('.pdf'):
				html = urllib.urlopen(item['link']).read()
				body = Document(html).summary()
			item['body'] = '<a href="' + item['comment'] + '">HN Comments</a><br>' + body

		self.feed.add(
			url = item['link'],
			title = item['title'],
			content = item['body'],
			content_type = "html",
			updated=datetime.datetime.utcnow()
		)
		return item
