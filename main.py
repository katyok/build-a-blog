import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Entry(db.Model):
    # created an entity with contraints in orange, you can lookup the stuff in the GAE specs
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)



class MainPage(Handler):
    # def render_front(self, title = "", body = "", error = ""):
    #     entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC LIMIT 5")
    #     self.render("front.html", title=title, body =body, error=error, entries = entries)
    #
    def get(self):
        self.render("newpost.html")

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            #create new thing:
            a = Entry(title = title, body = body)
            #store it in the database:
            a.put()
            self.redirect("/blog/"+str(a.key().id()))
        else:
            error = "Please fill in both the title and the body of the blog entry."
            self.render("newpost.html", title=title, body =body, error=error)

class BlogEntries(Handler):
    def render_entries(self, title = "", body = "", error = ""):
        entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC LIMIT 5")
        self.render("blog.html", title=title, body =body, error=error, entries = entries)

    def get(self):
        self.render_entries()

    def post(self):
        a = Entry(title = title, body = body)
        #store it in the database:
        a.put()

class ViewPostHandler(webapp2.RequestHandler):
    # how can I consolidate and not copypasta the three methods below
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def get(self, id):
        id = int(id)
        blogEntry = Entry.get_by_id(id)
        title = blogEntry.title
        body = blogEntry.body
        blogEntry = [blogEntry]

        if blogEntry:
            self.render("blog.html", title=title, body =body, entries = blogEntry, oneEntry = True)

        else:
            self.response.write("ERROR: You are referencing a blog that doesn't exist. Please go back to the main page.")

app = webapp2.WSGIApplication([
    ('/newpost', MainPage),
    ('/blog', BlogEntries),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
