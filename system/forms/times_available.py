from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout
from django import forms
from volunteers.models import TimesAvailable

class TimesAvailableEditForm(forms.ModelForm):
    class Meta:
        model = TimesAvailable
        fields = (
            'name',
            'order'
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
                'Time Available',
                'name',
                'order',
            )
        )

class TimesAvailableCreateForm(forms.ModelForm):
    class Meta:
        model = TimesAvailable
        fields = (
            'key',
            'name',
            'order'
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
                'Time Available',
                'key',
                'name',
                'order',
            )
        )
