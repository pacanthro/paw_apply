from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, HTML, Layout, Submit
from django import forms

from dancecomp.models import CompetitorContent

class CompetitorUpdateContentForm(forms.ModelForm):
    class Meta:
        model = CompetitorContent
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
                'email_waitlisted'
            ),
        )