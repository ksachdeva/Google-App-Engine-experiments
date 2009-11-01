
from google.appengine.ext import db
from django.newforms.widgets import PasswordInput, TextInput

USER_COOKIE_NAME = 'rb_current_user'

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
    name     = db.StringProperty(required=True)
    email    = db.EmailProperty(required=True)
    fb_uid   = db.StringProperty()
    
    def is_facebook_user(self):
        return (self.fb_uid > 0)
    