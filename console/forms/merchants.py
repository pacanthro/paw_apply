from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, HTML, Layout, Submit
from django import forms

from merchants.models import Merchant

class MerchantAssignTableForm(forms.ModelForm):
    class Meta:
        model = Merchant
        fields = (
            'table_number',
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
                'Table Info',
                HTML('<div class="row"><div class="col-sm-2">Merchant Name:</div><div class="col-sm-4">' + self.instance.business_name + '</div></div>'),
                'table_number'
            )
        )
        self.helper.add_input(Submit('submit', 'Apply', css_class='float-end'))