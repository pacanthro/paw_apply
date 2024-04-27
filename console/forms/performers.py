from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, HTML, Layout, Submit
from django import forms
from django.utils.timezone import localtime
from django.urls import reverse

from core.models import DaysAvailable
from performers.models import Performer

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