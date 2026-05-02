from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, HTML, Layout, Submit
from django import forms

from core.models import Department

class DepartmentEditForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = (
            'department_name',
            'description',
            'order',
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
                'Department',
                'department_name',
                'description',
                'order'
            )
        )
