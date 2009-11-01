
from google.appengine.ext.db import djangoforms

import models

class RegisterForm(djangoforms.ModelForm):
    class Meta:
        model = models.RunAroundUser
        exclude = ['fb_uid']