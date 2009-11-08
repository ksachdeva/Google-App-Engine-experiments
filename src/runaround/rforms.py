
from google.appengine.ext.db import djangoforms

from runaround import models

class RegisterForm(djangoforms.ModelForm):
    class Meta:
        model = models.RunAroundUser
        exclude = ['fb_uid']