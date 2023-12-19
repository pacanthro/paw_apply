from core.models import get_current_event
from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, HTML, Layout, Submit
from django import forms

from core.models import DaysAvailable
from partyfloor.models import PartyHost

class HostForm(forms.ModelForm):
    class Meta:
        model = PartyHost
        fields = (
            'email',
            'legal_name',
            'fan_name',
            'phone_number',
            'twitter_handle',
            'telegram_handle',
            'hotel_primary',
            'hotel_ack_num',
            'party_days',
            'ack_no_smoking',
            'ack_amplified_sound',
            'ack_verify_age',
            'ack_wristbands',
            'ack_closure_time',
            'ack_suspension_policy'
        )
        widgets = {
            'party_days': forms.CheckboxSelectMultiple,
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields
        self.fields['twitter_handle'].required = False
        self.fields['telegram_handle'].required = False
        self.fields['party_days'].queryset = DaysAvailable.objects.filter(available_party=True).order_by('order')
        self.fields['ack_no_smoking'].required = True
        self.fields['ack_amplified_sound'].required = True
        self.fields['ack_verify_age'].required = True
        self.fields['ack_wristbands'].required = True
        self.fields['ack_closure_time'].required = True
        self.fields['ack_suspension_policy'].required = True

        # Crispy
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2 text-capitalize'
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
                'Hotel Info',
                'hotel_primary',
                'hotel_ack_num',
                'party_days'
            ),
            Fieldset(
                'Acknowledgements',
                HTML("""
                     <strong>Please read and acknowledge each of the requirements below.</strong>
                """),
                'ack_no_smoking',
                'ack_amplified_sound',
                'ack_verify_age',
                'ack_wristbands',
                'ack_closure_time',
                'ack_suspension_policy'
            )
        )
        self.helper.add_input(Submit('submit', 'Apply', css_class='float-end'))
    
    def clean_email(self):
        event = get_current_event()
        email = self.cleaned_data['email']

        if PartyHost.objects.filter(event=event, email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email