import os
import urllib
import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


boxes = [('happy',False),('sad',True),('excited',False)]

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
        for box in boxes:
          name, setting = box
          setting=self.request.get(name) 
          print "MainPage: post: name = ", name
          print "MainPage: post: setting = ", setting
          if setting:
            box=(name,True)
          else:
            box=(name,False)
          new_boxes.append(box) 
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
