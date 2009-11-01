
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

from django.newforms.widgets import PasswordInput

import models

class RegisterForm(djangoforms.ModelForm):
    class Meta:
        model = models.RunAroundUser
        exclude = ['fb_uid']