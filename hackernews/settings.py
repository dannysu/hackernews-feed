# Scrapy settings for hackernews project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'hackernews'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['hackernews.spiders']
NEWSPIDER_MODULE = 'hackernews.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
ITEM_PIPELINES = ['hackernews.pipelines.HackernewsPipeline']
LOG_LEVEL = 'ERROR'
