from core.models import get_current_event
from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit
from django import forms

from core.models import DaysAvailable
from performers.models import Performer

class PerformerForm(forms.ModelForm):
    class Meta:
        model = Performer
        fields = (
            'email',
            'legal_name',
            'fan_name',
            'phone_number',
            'twitter_handle',
            'telegram_handle',
            'biography',
            'dj_history',
            'set_link'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields
        
        # Crispy
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10'
        self.helper.layout = Layout(
            Fieldset(
                'Contact Info',
                'email',
                'legal_name',
                'fan_name',
                'phone_number',
                PrependedText('twitter_handle', '@'),
                PrependedText('telegram_handle', '@')
            ),
            Fieldset(
                'Performance Info',
                'biography',
                'dj_history',
                'set_link'
            )
        )
        self.helper.add_input(Submit('submit', 'Apply', css_class='float-end'))
    
    def clean_email(self):
        event = get_current_event()
        email = self.cleaned_data['email']

        if Performer.objects.filter(event=event, email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email