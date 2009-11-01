from google.appengine.ext.webapp import template

register = template.create_template_register()

def fbconnect_button(button_size="medium"):
    return """
        <fb:login-button size="medium" background="light" length="long"
                [onlogin="facebook_onlogin_ready();"></fb:login-button>
    """
    
register.simple_tag(fbconnect_button)

