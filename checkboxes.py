import webapp2

form = """
<html>
<form method="post" action="/testform">
    <input name="q"> <input type="submit">
</form>
</html>
"""

form = """
<html>
<form method="post" action="/testform">
    <input type="checkbox" name="q">q<br>
    <input type="checkbox" name="r" checked>r<br>
    <input type="checkbox" name="s">s<br>
    <br>
    <input type="submit">
</form>
</html>
"""

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/html'
        self.response.out.write(form)

class TestHandler(webapp2.RequestHandler):
    def post(self):
        self.response.headers['Content-Type'] = 'text/html'
        q=self.request.get("q") 
        self.response.out.write("q = %s<br>" % q)
        r=self.request.get("r") 
        self.response.out.write("r = %s<br>" % r)
        s=self.request.get("s") 
        self.response.out.write("s = %s<br>" % s)

application = webapp2.WSGIApplication([('/', MainPage),
                              ('/testform', TestHandler)],
                             debug=True)
