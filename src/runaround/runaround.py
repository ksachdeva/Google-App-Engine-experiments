from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

import os
import logging
import cgi

from runaround import fbconnect
from runaround import models

template.register_template_library('runaround.templatetags.runaround_tags')

from runaround import rforms

class MainPage(webapp.RequestHandler):
    def get(self):
        
        user = models.RunAroundUser.getLoggedIn(self.request)
        
        template_values = {
            'user' : user
        }
        
        logging.debug(user)
        
        if user is None:
            template_path = "templates/index_loggedout.html"
        else:
            template_path = "templates/index.html"
        
        path = os.path.join(os.path.dirname(__file__), template_path)
        self.response.out.write(template.render(path, template_values))
        
    def post(self):
        user = models.RunAroundUser.getLoggedIn(self.request)
        
        route = cgi.escape(self.request.get('route',None))
        miles = cgi.escape(self.request.get('miles',None))
        date = cgi.escape(self.request.get('date',None))
        
        logging.debug(date)
        
        
class XdReceiverPage(webapp.RequestHandler):
    def get(self):
        template_values = {}
        path = os.path.join(os.path.dirname(__file__), 'templates/xd_receiver.html')
        self.response.out.write(template.render(path, template_values))
        
class LogoutPage(webapp.RequestHandler):
    def get(self):
        user = models.RunAroundUser.getLoggedIn(self.request)
        
        if user is not None:
            user.logOut(self.response)

        self.redirect('/runaround/')
        
class AccountPage(webapp.RequestHandler):
    def get(self):
        
        user = models.RunAroundUser.getLoggedIn(self.request)
      
        if user is None:
            self.redirect('/runaround/')
            return
               
        template_values = {
            'user' : user,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/account.html')
        self.response.out.write(template.render(path, template_values))
     
    def post(self):
      
        user = models.RunAroundUser.getLoggedIn(self.request)
      
        if user is None:
            self.redirect('/runaround/')
            return
        
        error = ''
        
        # update name, email and password
        name = cgi.escape(self.request.get('name',None))
        email = cgi.escape(self.request.get('email',None))
        password = cgi.escape(self.request.get('password',None))
        
        if not ((name is None) or (email is None) or (password is None) or (password == "PASSWORD_PLACEHOLDER")):
            user.password = password
            user.email = email
            user.name = name
            user.save()
            
            # redirect
            self.redirect('/runaround/')
        else:
            error = "Fields can not be empty"
            
        
        template_values = {
            'user' : user,
            'error' : error,
        }
            
        path = os.path.join(os.path.dirname(__file__), 'templates/account.html')
        self.response.out.write(template.render(path, template_values))
        
class LoginPage(webapp.RequestHandler):
    def get(self):
        user = models.RunAroundUser.getLoggedIn(self.request)
        
        logging.debug(user)
        
        if user is not None:
            self.redirect('/runaround/')
        else:
            template_values = {}
            path = os.path.join(os.path.dirname(__file__), 'templates/login.html')
            self.response.out.write(template.render(path, template_values))
        
    def post(self):
        username = cgi.escape(self.request.get('username', None))
        password = cgi.escape(self.request.get('password', None))
        
        error = ''
        
        if username != None and password != None:
            user = models.RunAroundUser.getByUserName(username)
            if user is None:
                error = "Unknown username: <b> " + username + " </b>"
            else:
                # match the password
                if user.logIn(self.request, self.response, password) is False:
                    error = "Bad password for username: <b> " + username + " </b>"
                else:
                    self.redirect('/runaround/')
        
        template_values = {
            'error' : error 
        }
        
        path = os.path.join(os.path.dirname(__file__), 'templates/login.html')
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
    ('/runaround/xd_receiver/',XdReceiverPage),
    ('/runaround/login/',LoginPage),
    ('/runaround/logout/',LogoutPage),
    ('/runaround/account/',AccountPage),
]

logging.getLogger().setLevel(logging.DEBUG)
application = webapp.WSGIApplication(_URLS, debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
