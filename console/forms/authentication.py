from crispy_forms.helper import FormHelper
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(AuthenticationForm, *args, **kwargs)

        # Crispy
        self.helper = FormHelper()
        self.helper.label_class = 'text-capitalize'