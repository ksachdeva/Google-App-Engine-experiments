
from facebook import Facebook

API_KEY = ""
SECRET_KEY = ""

def facebook_client():
    return Facebook(API_KEY,SECRET_KEY)