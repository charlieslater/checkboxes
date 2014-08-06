import webapp2
import cgi 
import urllib
import os
import jinja2

from google.appengine.ext import ndb
from google.appengine.api import users

MAIN_PAGE_FOOTER_TEMPLATE = """\
    <form action="/write?%(list_query_params)s" method="post">
      <div><textarea type="checkbox" name="content" rows="1" cols"60"></textarea></div>
      <div><input type="submit" value="Add to List"></div>
    </form>
    <hr>
    <form> List name:
      <input value"%(list_name)s" name="list_name">
      <input type="submit" value="switch">
    </form>
    <a href="%(url)s">%(url_link)s</a>
  </body>
</html>
"""
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):

    def post(self):
        self.get_list_stuff()
        for c in self.listcontents:
          checked_box = self.request.get(c.content)
          if checked_box:
            c.checked = True
          else:
            c.checked = False
          c.put()  #?? do we need a put?  I don't think so.
        self.display_list()

    def get(self):
        print "MainPage:get: calling get_list_stuff"
        self.get_list_stuff()
        print "MainPage:get: calling display_list"
        self.display_list()

    def get_list_stuff(self):
        list_name = self.request.get('list_name', DEFAULT_LIST_NAME)
        print 'list name=', list_name
        listcontents_query = ListContent.query(
            ancestor=list_key(list_name)).order(ListContent.date)
        listcontents = listcontents_query.fetch(10)
        self.list_name = list_name
        self.listcontents = listcontents
        #return (list_name, listcontents)
        
    def display_list(self):
        # boxes = {'fun':True,  'happy':False, 'sad':True}
        urlStrings = {}
        for item in self.listcontents:
           urlStrings[item.content] = item.key.urlsafe()
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout' 
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        list_query_params = urllib.urlencode({'list_name': self.list_name})
        #title = "Weblist Test"
        title = self.list_name
        template_values = {"urlStrings": urlStrings, "title": title, "listcontents": self.listcontents, "list_query_params":list_query_params, "list_name":cgi.escape(self.list_name),
                           "url":url, "url_link": url_linktext}         
          
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

DEFAULT_LIST_NAME = 'default_list'

def list_key(list_name=DEFAULT_LIST_NAME):
    return ndb.Key('List', list_name)

class ListContent(ndb.Model):
    author = ndb.UserProperty()
    checked = ndb.BooleanProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class oldMainPage(webapp2.RequestHandler): 
    def get(self):
        self.response.write('<html><body>')
        list_name = self.request.get('list_name', DEFAULT_LIST_NAME)
        listcontents_query = ListContent.query(
            ancestor=list_key(list_name)).order(-ListContent.date)
        listcontents = listcontents_query.fetch(10)
         
        for c in listcontents:
            if c.author:
                self.response.write('<b>%s</b> added:' % c.author.nickname())
            else:
                self.response.write('anonymous added:')
            self.response.write('<blockquote>%s</blockquote>' % 
                                cgi.escape(c.content))

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout' 
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        list_query_params = urllib.urlencode({'list_name': list_name})

        self.response.write(MAIN_PAGE_FOOTER_TEMPLATE %
                           {"list_query_params":list_query_params, "list_name":cgi.escape(list_name),
                           "url":url, "url_link": url_linktext})         
        
class Lists(webapp2.RequestHandler):
    def post(self):
        list_name = self.request.get('list_name', 
                                     DEFAULT_LIST_NAME)
        listcontent = ListContent(parent=list_key(list_name))
        if users.get_current_user():
            listcontent.author = users.get_current_user()

        listcontent.content = self.request.get('content').strip()
        if len(listcontent.content) > 0:
            listcontent.put()
        
        query_params = {'list_name' : list_name}
        self.redirect('/?' + urllib.urlencode(query_params))

class Delete(webapp2.RequestHandler):
    def get(self):
        urlString = self.request.get('urlString')
        item_key = ndb.Key(urlsafe=urlString)
        item_key.delete()
        list_name = self.request.get('list_name',
                                     DEFAULT_LIST_NAME)
        query_params = {'list_name' : list_name}
        self.redirect('/?' + urllib.urlencode(query_params))        

application = webapp2.WSGIApplication([
    ('/', MainPage), 
    ('/add', Lists), 
    ('/delete', Delete),
], debug=True)

