from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from django import forms

from core.models import DaysAvailable
from volunteers.models import TimesAvailable, Volunteer


class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = (
            'email',
            'legal_name',
            'fan_name',
            'phone_number',
            'twitter_handle',
            'telegram_handle',
            'department_interest',
            'volunteer_history',
            'special_skills',
            'days_available',
            'time_availble',
            'avail_setup',
            'avail_teardown'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields
        self.fields['days_available'].queryset = DaysAvailable.objects.filter(party_only=False).order_by('order')
        self.fields['time_availble'].queryset = TimesAvailable.objects.order_by('order')

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
                'Volunteer Interests',
                'department_interest',
                'volunteer_history',
                'special_skills',
                'days_available',
                'time_availble',
                'avail_setup',
                'avail_teardown'
            )
        )
        self.helper.add_input(Submit('submit', 'Apply', css_class='float-end'))