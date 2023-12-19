from crispy_forms.bootstrap import InlineCheckboxes, PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, HTML, Layout, Submit
from django import forms

from core.models import DaysAvailable
from panels.models import Panel, PanelDuration, PanelSlot

class PanelForm(forms.ModelForm):
    class Meta:
        model = Panel
        fields = (
            'email',
            'legal_name',
            'fan_name',
            'phone_number',
            'twitter_handle',
            'telegram_handle',
            'panelist_bio',
            'panel_name',
            'panel_description',
            'panel_duration',
            'equipment_needs',
            'mature_content',
            'panel_day',
            'panel_times',
            'check_ids'
        )
        widgets = {
            'panel_day': forms.CheckboxSelectMultiple,
            'panel_times': forms.CheckboxSelectMultiple
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields
        self.fields['panel_day'].queryset = DaysAvailable.objects.filter(party_only=False).order_by('order')
        self.fields['panel_duration'].queryset = PanelDuration.objects.order_by('order')
        self.fields['panel_times'].queryset = PanelSlot.objects.order_by('order')

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
                PrependedText('telegram_handle', '@'),
                'panelist_bio'
            ),
            Fieldset(
                'Panel Info',
                'panel_name',
                'panel_description',
                'equipment_needs',
                'mature_content'
            ),
            Fieldset(
                'Scheduling',
                'panel_duration',
                'panel_day',
                'panel_times'
            ),
            Fieldset(
                'ID Check',
                HTML("""
                     <strong>If your panel is mature, you must check photo ID at the door and not admit anyone under the age of 18.</strong>
                """),
                'check_ids'
            )
        )

        self.helper.add_input(Submit('submit', 'Apply', css_class='float-end'))