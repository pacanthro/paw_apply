from core.models import get_current_event
from crispy_forms.bootstrap import PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from django import forms

from core.models import DaysAvailable, Department
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
        widgets = {
            'department_interest': forms.CheckboxSelectMultiple,
            'days_available': forms.CheckboxSelectMultiple,
            'time_availble': forms.CheckboxSelectMultiple
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields
        self.fields['department_interest'].queryset = Department.objects.exclude(deleted=True).order_by('order')
        self.fields['days_available'].queryset = DaysAvailable.objects.filter(party_only=False).order_by('order')
        self.fields['time_availble'].queryset = TimesAvailable.objects.order_by('order')

        # Crispy
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2 text-capitalize'
        self.helper.field_class = 'col-sm-10'
        self.helper.labels_uppercase = True
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

    def clean_email(self):
        event = get_current_event()
        email = self.cleaned_data['email']

        if Volunteer.objects.filter(event=event, email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email