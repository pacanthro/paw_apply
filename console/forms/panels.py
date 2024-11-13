from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, HTML, Layout, Submit
from django import forms
from django.utils.timezone import localtime
from django.urls import reverse

from core.models import get_current_event, DaysAvailable, Event, EventRoom, RoomType
from panels.models import Panel

class PanelScheduleRoomDayForm(forms.ModelForm):
    class Meta:
        model = Panel
        fields = (
            'scheduled_room',
            'scheduled_day',
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        event = get_current_event()

        # Fields
        self.fields['scheduled_room'].queryset = EventRoom.objects.filter(event=event).filter(room_type=RoomType.ROOM_PANELS)
        self.fields['scheduled_day'].queryset =  DaysAvailable.objects.filter(available_scheduling=True).order_by('order')
        
        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'text-capitalize'
        self.helper.layout = Layout(
            'scheduled_room',
            'scheduled_day'
        )

class PanelScheduleSlotForm(forms.ModelForm):
    scheduled_time = forms.ChoiceField(choices=[])
    class Meta:
        model = Panel
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
            choices.append((localtime(option).strftime('%Y-%m-%dT%H:%M:%S%z'), localtime(option).strftime('%I:%M %p')))
        
        self.fields['scheduled_time'].choices = choices
        
        # Crispy
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.label_class = 'text-capitalize'
        self.helper.layout = Layout(
            'scheduled_time'
        )