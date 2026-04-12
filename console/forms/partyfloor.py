from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, HTML, Layout, Submit
from django import forms

from partyfloor.models import PartyHost, PartyHostContent

class HostAssignRoomForm(forms.ModelForm):
    class Meta:
        model = PartyHost
        fields = (
            'room_number',
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Crispy
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2 text-capitalize'
        self.helper.field_class = 'col-sm-4'
        self.helper.layout = Layout(
            Fieldset(
                'Room Info',
                HTML('<div class="row"><div class="col-sm-2">Fan Name:</div><div class="col-sm-4">' + self.instance.fan_name + '</div></div>'),
                'room_number'
            )
        )
        self.helper.add_input(Submit('submit', 'Apply', css_class='float-end'))

class PartyHostUpdateContentForm(forms.ModelForm):
    class Meta:
        model = PartyHostContent
        fields = (
            'card_title',
            'card_body',
            'card_cta',
            'page_interstitial',
            'page_apply',
            'page_confirmation',
            'email_submit',
            'email_accepted',
            'email_declined',
            'email_waitlisted',
            'email_assigned'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields
        
        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'text-capitalize'
        self.helper.layout = Layout(
            Fieldset(
                'Card Content',
                HTML('<p>This is the content that shows on the landing page.</p>'),
                'card_title',
                'card_body',
                'card_cta'
            ),
            Fieldset(
                'Page Content',
                HTML('<p>This is the content that is shown before the form.</p>'),
                'page_interstitial',
                HTML('<p>Shown above the form.</p>'),
                'page_apply',
                HTML('<p>Shown after the application is submitted'),
                'page_confirmation'
            ),
            Fieldset(
                'Email Content',
                HTML('<p>This is the email that is sent when the form is submitted.</p>'),
                'email_submit',
                HTML('<p>This is the email that is sent when the application is accepted.</p>'),
                'email_accepted',
                HTML('<p>This is the email that is sent when the application is declined.</p>'),
                'email_declined',
                HTML('<p>This is the email that is sent when the application is declined.</p>'),
                'email_waitlisted',
                HTML('<p>This is the email that is sent when the application scehdeduled.</p>'),
                'email_assigned'
            ),
        )