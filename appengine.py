import webapp2
from google.appengine.api import urlfetch

class UpdateHandler(webapp2.RequestHandler):
    def get(self, offset):
        result = urlfetch.fetch('http://feeds.dannysu.com/update/'+str(offset))
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('')

app = webapp2.WSGIApplication([
        ('/update/([0-9]+)', UpdateHandler)
    ],
    debug=True)
