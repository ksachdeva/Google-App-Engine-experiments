from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import os
import cgi

from runaround import models

template.register_template_library('runaround.templatetags.runaround_tags')

from runaround import rforms

class MainPage(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'templates/index_loggedout.html')
        self.response.out.write(template.render(path, template_values))

class RegisterPage(webapp.RequestHandler):
    def get(self):
        template_values = {
            'form' : rforms.RegisterForm() 
        }
        path = os.path.join(os.path.dirname(__file__), 'templates/register.html')
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        data = rforms.RegisterForm(data=self.request.POST)
        if data.is_valid():
            # save the data and redirect to the run page
            entity = data.save(commit=False)
            entity.put()
            self.redirect('/runaround/')
        else:
            # re-print the form
            template_values = {
                'form' : data
            }
            path = os.path.join(os.path.dirname(__file__), 'templates/register.html')
            self.response.out.write(template.render(path, template_values))

_URLS = [
    ('/runaround/', MainPage),
    ('/runaround/register/',RegisterPage),
]

application = webapp.WSGIApplication(_URLS, debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
