import os
import sys
import urllib2
import json
import base64
import re
try:
    from readability.readability import Document
except Exception:
    pass
import datetime
from pyatom import AtomFeed
from flask import Flask
from flask import Response
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.debug=True
db = SQLAlchemy(app)

class Entry(db.Model):
    __tablename__ = 'entries'
    id = db.Column(db.Integer, primary_key = True)
    link = db.Column(db.String(), unique=True)
    title = db.Column(db.String())
    body = db.Column(db.String())

    def __init__(self, link, title, body):
        self.link = link
        self.title = title
        self.body = body

    def __repr__(self):
        return '<Entry %r>' % self.link

db.create_all()

@app.route('/hackernews100.atom')
def hn100():
    feed = AtomFeed(
        title = "Hacker News >100",
        subtitle = "Hacker News over 100 points",
        feed_url = "http://feeds.dannysu.com/hackernews100.atom",
        url = "http://news.ycombinator.com/over?points=100"
    )

    entries = Entry.query.all()
    for entry in entries:
        feed.add(
            url = entry.link,
            title = entry.title,
            content = entry.body,
            content_type = "html",
            updated=datetime.datetime.utcnow()
        )

    return Response(feed.to_string(), mimetype='application/atom+xml')

@app.route('/update/<offset>')
def update(offset):
    offset = int(offset)
    if offset == 0:
        db.session.query(Entry).delete()
        db.session.commit()
        return ''

    # Obtain bearer token from Twitter
    url = "https://api.twitter.com/oauth2/token"
    consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
    consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
    auth = base64.b64encode(consumer_key + ':' + consumer_secret)
    request = urllib2.Request(url, "grant_type=client_credentials", {"Authorization": "Basic "+auth})
    response = urllib2.urlopen(request).read()
    json_response = json.loads(response)
    access_token = json_response['access_token']

    # Obtain HN posts >100 pts
    url = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=newsyc100&count=40"
    request = urllib2.Request(url, headers={"Authorization": "Bearer "+access_token})
    response = urllib2.urlopen(request).read()
    tweets = json.loads(response)

    increment = 2

    start_at = (offset - 1) * increment
    tweets = tweets[start_at:start_at + increment]
    for tweet in tweets:
        title = tweet['text']

        start_link = title.rfind("(http")
        end_link = title.find(")", start_link)
        comment_link = title[start_link+1:end_link]

        title = title[0:start_link]

        start_link = title.rfind("http")
        end_link = title.find(" ", start_link)
        link = title[start_link:end_link]

        title = title[0:start_link]

        try:
            response = urllib2.urlopen(link)
        except urllib2.HTTPError:
            continue

        encoding = response.headers['content-type'].split('charset=')[-1]
        if encoding == 'text/html':
            encoding = 'utf-8'
        if encoding == 'application/pdf':
            continue
        html = response.read().decode(encoding, 'ignore')

        if sys.modules.has_key('readability.readability'):
            body = Document(html).summary()
        else:
            body = html

        body = body.replace('<html><body>', '<html><body><a href="' + comment_link + '">HN Comments</a><br>')
        body = body.replace('<body id="readabilityBody">', '')

        entry = Entry(link, title, body)
        db.session.add(entry)

    db.session.commit()
    return ''

if __name__ == '__main__':
    # Bind to PORT if defined, otherwise default to 5000.
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
