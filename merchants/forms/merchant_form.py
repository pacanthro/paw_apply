from core.models import get_current_event
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit
from django import forms

from core.models import DaysAvailable
from merchants.models import Merchant, Table

class MerchantForm(forms.ModelForm):
    class Meta:
        model = Merchant
        fields = (
            'email',
            'legal_name',
            'fan_name',
            'phone_number',
            'table_size',
            'business_name',
            'wares_description',
            'helper_legal_name',
            'helper_fan_name',
            'special_requests',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields
        self.fields['table_size'].queryset = Table.objects.filter(deleted=False).order_by('order')
        
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
                'phone_number'
            ),
            Fieldset(
                'Business Info',
                'table_size',
                'business_name',
                'wares_description',
            ),
            Fieldset(
                'Helper Info',
                'helper_legal_name',
                'helper_fan_name',
            ),
            Fieldset(
                'Extras',
                'special_requests'
            )
        )
        self.helper.add_input(Submit('submit', 'Apply', css_class='float-end'))

    def clean_email(self):
        event = get_current_event()
        email = self.cleaned_data['email']

        if Merchant.objects.filter(event=event, email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email