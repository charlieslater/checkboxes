import os
import urllib
import jinja2
import webapp2
from google.appengine.ext import ndb

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class BoxLine(ndb.Model):
    def __init__(self,line,checked):
        self.line = line
        self.checked = checked

boxes = [BoxLine('happy',False),BoxLine('sad',True),BoxLine('excited',False)]

class MainPage(webapp2.RequestHandler):

    def get(self):
        global boxes

        template_values = {
            'boxes': boxes,
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

    def post(self):
        global boxes
        new_boxes = []
        # each box is an instance of the class BoxLine
        for box in boxes:
          setting=self.request.get(box.line) 
          print "MainPage: post: name = ", box.line
          print "MainPage: post: setting = ", setting
          if setting:
            box.checked = True
          else:
            box.checked = False
          new_boxes.append(box) 
          box.put()
        boxes = new_boxes
        print "MainPage: post: new_boxes = ", new_boxes
        template_values = {
            'boxes': boxes,
        }
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))


class TestHandler(webapp2.RequestHandler):

    def post(self):
        from time import sleep
        global boxes
        self.response.headers['Content-Type'] = 'text/html'
        for box in boxes:
          setting=self.request.get(box[0]) 
          if not setting:
            setting='off'
          self.response.out.write("%s = %s<br>" % (box, setting))
        self.response.out.write('<a href="/">back</a>')


application = webapp2.WSGIApplication([('/', MainPage),
                                      ('/testform', TestHandler)],
                                      debug=True)
