from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, HTML, Layout, Submit
from django import forms

from partyfloor.models import PartyHost

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