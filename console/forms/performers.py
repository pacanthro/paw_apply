from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, HTML, Layout, Submit
from django import forms
from django.utils.timezone import localtime
from django.urls import reverse

from core.models import DaysAvailable
from performers.models import Performer, PerformerContent

class PerformerScheduleDayForm(forms.ModelForm):
    class Meta:
        model = Performer
        fields = (
            'scheduled_day',
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields
        self.fields['scheduled_day'].queryset =  DaysAvailable.objects.filter(available_scheduling=True).order_by('order')
        
        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'text-capitalize'
        self.helper.layout = Layout(
            'scheduled_day'
        )
        

class PerformerScheduleSlotForm(forms.ModelForm):
    scheduled_time = forms.ChoiceField(choices=[])
    class Meta:
        model = Performer
        fields = (
            'scheduled_time',
        )

    def __init__(self, *args, **kwargs):
        options = kwargs.pop('options', None)

        super().__init__(*args, **kwargs)

        # Fields
        choices = [
            (None, '---------')
        ]
        for option in options:
            choices.append((localtime(option).strftime('%Y-%m-%dT%H:%M:%S%z'), localtime(option).strftime('%I:%M:%S %p')))

        self.fields['scheduled_time'].choices = choices

        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'text-capitalize'
        self.helper.layout = Layout(
            'scheduled_time'
        )

class PerformerUpdateContentForm(forms.ModelForm):
    class Meta:
        model = PerformerContent
        fields = (
            'card_title',
            'card_body',
            'card_cta',
            'page_interstitial',
            'page_apply',
            'page_confirmation',
            'email_confirm',
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
                'email_confirm',
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