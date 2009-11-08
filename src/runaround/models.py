
from google.appengine.ext import db
from django.newforms.widgets import PasswordInput, TextInput

from runaround import fbconnect

import logging
import Cookie
import re

USER_COOKIE_NAME = 'rb_current_user'

def writeCookie(response,username):
    cookie = Cookie.SimpleCookie()
    cookie[USER_COOKIE_NAME] = username
    cookie[USER_COOKIE_NAME]["Path"] = "/"
    
    h = re.compile('^Set-Cookie:').sub('',cookie.output(),count=1)
         
    response.headers.add_header('Set-Cookie',str(h))
    

class PasswordProperty(db.StringProperty):
    def __init__(self, size=None, maxlength=None, password=False,
                 cssClass=None, **kwargs):
        self._size = size
        self._maxlength = maxlength
        self._password = password
        self._cssClass = cssClass
        super(PasswordProperty, self).__init__(**kwargs) 

    def get_form_field(self, **kwargs):
        defaults = {}
        attrs={}
        if self._size:
            attrs['size']=self._size
        if self._maxlength:
            attrs['maxlength']=self._maxlength
        if self._cssClass:
            attrs['class']=self._cssClass
        if self._password:
            defaults['widget']=PasswordInput(attrs)
        else:
            defaults['widget']=TextInput(attrs)
        defaults.update(kwargs)
        return super(PasswordProperty, self).get_form_field(**defaults)

class RunAroundUser(db.Model):
    username = db.StringProperty(required=True)
    password = PasswordProperty(password=True,required=True)
    name     = db.StringProperty()
    email    = db.EmailProperty()
    fb_uid   = db.StringProperty()
    
    def is_facebook_user(self):
        return (self.fb_uid > 0)
    
    def has_password(self):
        if self.password == "---":
            return False
        
        return True
    
    def getName(self):
        if self.is_facebook_user():
            info = fbconnect.facebook_client().users.getInfo([self.fb_uid], ['name'])[0]
            return info['name']
        
        return self.name
    
    def getEmail(self):
        if self.is_facebook_user():
            info = fbconnect.facebook_client().users.getInfo([self.fb_uid], ['email'])[0]
            return info['name']
        
        return self.email
    
    @staticmethod
    def getLoggedIn(request):
        native_user = RunAroundUser.getLoggedInNative(request)
        fb_client = fbconnect.facebook_client()
        user = None
        if fb_client.check_session(request):
            logging.debug("fb_client has a session...")
            fb_uid = fb_client.uid
            if fb_uid:
                logging.debug("User with fb_uid " + fb_uid) 
                user = RunAroundUser.getByFacebookUID(fb_uid)
                if native_user:
                    native_user.logOut()
                    native_user.connectWithFacebookUID(fb_uid)
                    user = native_user
                elif user is None :
                    logging.debug("Create a user from its facebook uid ..")
                    user = RunAroundUser.createByFacebookUID(fb_uid)
                 
        if (native_user and (user is None)):
            logging.debug("Making native user as user...")
            user = native_user
                 
        return user  
                   
    @staticmethod
    def getByUserName(username):
        logging.debug("Finding user by the username: " + username)
        return RunAroundUser.all().filter("username =", username).get()
          
          
    @staticmethod
    def getLoggedInNative(request):
        
        username = None
        
        logging.debug(request.cookies)
        
        if request.cookies.has_key(USER_COOKIE_NAME):
            username = request.cookies[USER_COOKIE_NAME]
            
        if username is None:
            return None
            
        logging.debug("Username from cookie is: " + username)
        if username and username != 'unknown':
            return RunAroundUser.getByUserName(username)
        else:
            return None
    
    @staticmethod
    def getByFacebookUID(fb_uid):
        if fb_uid is None:
            return None
        
        user = RunAroundUser.all().filter("fb_uid =", fb_uid).get()
        
        if user is None:
            logging.debug("Did not find user with fb_uid " + fb_uid)
        
        return user
    
    @staticmethod
    def getFacebookUserEmailHashes(fb_uid):
        info = fbconnect.facebook_client().users.getInfo([fb_uid], ['email_hashes'])[0]
        
        logging.debug("Email hashes are: ")
        logging.debug(info["email_hashes"])
        
        return info
    
    @staticmethod
    def getByFacebookEmailHashes(info):
        email_hashes = info['email_hashes']
        
    
    @staticmethod
    def createByFacebookUID(fb_uid):
        """
        Create an account for the user based on Facebook UID.
   
        Note that none of the Facebook data is actually stored in the DB - basically
        we store only the UID and generate all other info (name, pic, etc) on the fly.
        """
        
        # First check if there is a local account so
        # we do not create the account again
        email_hashes = RunAroundUser.getFacebookUserEmailHashes(fb_uid)
        
        user = None
        
        if user:
            user.fb_uid = fb_uid
        else:
            username = "FaceBookUser_" + fb_uid
            
            user = RunAroundUser(fb_uid=fb_uid,
                                 username=username,
                                 password="---")
            
        user.put()
        
        return user 
    
    def logIn(self, request, response, password=None):
        if self.is_facebook_user() and fbconnect.facebook_client().check_session(request):
            return False
        
        if password != None and self.password != password :
            return False
        
        writeCookie(response,self.username)
        return True
        
    
    def logOut(self,response):
        writeCookie(response,'unknown')
        
        # TODO : Need to invalidate facebook session
        pass
    
    def connectWithFacebookUID(self,fb_uid):
        fb_user = RunAroundUser.getByFacebookUID(fb_uid)
        if fb_user:
            # if there are two separate accounts for the same
            # user, then delete the Facebook-specific one
            # and connect the facebook id with the existing
            # account.
            #
            # a real site wouldn't actually delete an account -
            # the user should probably control the merging
            # of data from the to-be-deleted account to their own
            if fb_user.username != self.username:
                fb_user.delete()
            
        if fb_uid is None:
            return False
        
        logging.debug("Saving the fb_uid in the user ...")
        
        self.fb_uid = fb_uid
        self.save()
        
class Run(db.Model):
    user = db.ReferenceProperty(RunAroundUser)
    route = db.StringProperty()
    date = db.DateProperty()
    miles = db.IntegerProperty()
    
    