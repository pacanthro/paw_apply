from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout
from django import forms

from core.models import EventRoom

class EventRoomEditForm(forms.ModelForm):
    class Meta:
        model = EventRoom
        fields = (
            'room_name',
            'room_type',
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
                'Event Room',
                'room_name',
                'room_type',
            )
        )
