#
# This module gives you examples of how to delete items from a list.
# 
#
import cgi
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import webapp2

# These template strings use named parameters.  They are meant to be used
# with a Python dictionary.  See:
# http://python.net/~goodger/projects/pycon/2007/idiomatic/handout.html#string-formatting
# https://docs.python.org/2/library/stdtypes.html#string-formatting

MAIN_PAGE_HEADER_TEMPLATE = """\
    <style>
      a { text-decoration:none; }
    </style>
    <form>List name:
      <input value="%(list_name)s" name="list_name">
      <input type="submit" value="switch">
    </form>
"""

MAIN_PAGE_FOOTER_TEMPLATE = """\
    <form action="/add?%(item)s" method="post">
      <div><textarea name="content" rows="1" cols="65"></textarea></div>
      <div><input type="submit" value="Add Item"></div>
    </form>
    <hr>
    <a href="%(url)s">%(url_name)s</a>
  </body>
</html>
"""

ITEM_TEMPLATE = """\
  <li> %(content)s
  <a href="/deleteme?urlsafe=%(urlsafe)s&list_name=%(list_name)s">
  <img 
  src="static/gnome_edit_delete.png" 
  title="Delete" 
  alt="Delete Icon" 
  align="bottom"
  height="15" 
  width="12"/>
  </a></li>
"""

DEFAULT_LIST_NAME = 'default_list'

# Set a parent key (list_key) on the 'Items'. 
# This groups the items in what App Engine Data Store calls an "entity group"
# Per App Enging tutorial, Queries across the single entity group will be 
# consistent.  However, the write rate should be limited to ~1/second.

def list_key(list_name=DEFAULT_LIST_NAME):
    """Constructs a Datastore key for a Edge List with list_name."""
    return ndb.Key('EdgeList', list_name)

class EdgeList(ndb.Model):
    """Edge list."""
    author = ndb.UserProperty()
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)

class Item(ndb.Model):
    """Item on edge list."""
    content = ndb.StringProperty(indexed=False)
    checked = ndb.BooleanProperty()
    crossed_off = ndb.BooleanProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class MainPage(webapp2.RequestHandler):
    def write_form(self):
        #print 'dir(items[3]) =',dir(items[3])
        #print 'items[3].key =',items[3].key
        #print 'items[3].content =',items[3].content
        self.response.write('<div>')
        self.response.write('<form method="post" action="">')
        self.response.write('<ol>')
        for item in self.items:
            self.response.write(
                '<li>%(content)s (delete<input type="checkbox" name="%(content)s">)</li>' %
                {'content': cgi.escape(item.content)})
        self.response.write('</ol>')
        if len(self.items) > 0:
            self.response.write(
                          '<input type="submit" value="Delete Checked Items">')
        self.response.write('</form>')
        self.response.write('</div>')

        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        # Write the submission form and the footer of the page
        add_item_params = urllib.urlencode({'list_name': self.list_name})
        self.response.write(MAIN_PAGE_FOOTER_TEMPLATE % {'item': add_item_params,
                             'url': url, 'url_name': url_linktext})

    def write_footer(self):
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'

        # Write the submission form and the footer of the page
        add_item_params = urllib.urlencode({'list_name': self.list_name})
        self.response.write(MAIN_PAGE_FOOTER_TEMPLATE % {'item': add_item_params,
                             'url': url, 'url_name': url_linktext})

    def write_list(self):
        self.response.write('<ol>')
        for item in self.items:
            item.content = item.content.encode('utf-8').strip()
            print "dir(item) =",dir(item)
            print "item.key.id() =",item.key.id()
            self.response.write(
                ITEM_TEMPLATE % {'content': item.content,
                                 'urlsafe': item.key.urlsafe(),
                                 'list_name': self.list_name})
        self.response.write('</ol>')


    def post(self):
        self.list_name = self.request.get('list_name',
                                          DEFAULT_LIST_NAME)
        ancestor=list_key(self.list_name)
        items_query = Item.query(
            ancestor=list_key(self.list_name)).order(+Item.date)
        print "post: orders = ",items_query._Query__orders
        items = items_query.fetch(20)
        for item in items:
            setting=self.request.get(item.content) 
            if setting:
                item.key.delete()
        self.items = items_query.fetch(20)
        self.write_header()
        #self.write_form()

    def write_header(self):
        self.response.write('<html><body>')
        self.response.write(MAIN_PAGE_HEADER_TEMPLATE %
                            {'list_name': cgi.escape(self.list_name) })

    def get(self):
        self.list_name = self.request.get('list_name',
                                          DEFAULT_LIST_NAME)
        items_query = Item.query(
                         ancestor=list_key(self.list_name)).order(+Item.date)
        print "get: orders = ",items_query._Query__orders
        self.items = items_query.fetch(20)
        self.write_header()
        #self.write_form()
        self.write_list()
        self.write_footer()


class AddItem(webapp2.RequestHandler):
    def post(self):
        list_name = self.request.get('list_name', DEFAULT_LIST_NAME)
        item = Item(parent=list_key(list_name))

        if users.get_current_user():
            item.author = users.get_current_user()

        item.content = self.request.get('content').encode('utf-8').strip()
        print "AddItem: post: item.content = ", item.content
        if len(item.content) > 0:
            item.put()

        query_params = {'list_name': list_name}
        self.redirect('/?' + urllib.urlencode(query_params))

class DeleteMe(webapp2.RequestHandler):
    def get(self):
        urlsafe = self.request.get('urlsafe')
        print "DeleteMe:urlsafe =",urlsafe
        item = ndb.Key(urlsafe=urlsafe).get()
        item.key.delete()
        list_name = self.request.get('list_name', DEFAULT_LIST_NAME)
        print "DeleteMe:list_name =",list_name
        self.redirect('/?' + urllib.urlencode({'list_name': list_name}))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/add', AddItem),
    ('/deleteme', DeleteMe),
], debug=True)
