import os
import urllib
import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


boxes = ['happy','sad','excited']

class MainPage(webapp2.RequestHandler):

    def get(self):
        global boxes

        template_values = {
            'boxes': boxes,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
# [END main_page]


class TestHandler(webapp2.RequestHandler):

    def post(self):
        from time import sleep
        global boxes
        self.response.headers['Content-Type'] = 'text/html'
        for box in boxes:
          setting=self.request.get(box) 
          if not setting:
            setting='off'
          self.response.out.write("%s = %s<br>" % (box, setting))
        self.response.out.write('<a href="/">back</a>')


application = webapp2.WSGIApplication([('/', MainPage),
                                      ('/testform', TestHandler)],
                                      debug=True)
