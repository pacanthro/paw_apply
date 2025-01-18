from core.models import get_current_event
from crispy_forms.bootstrap import InlineField, PrependedText
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout, Submit
from django import forms

from core.models import DaysAvailable
from dancecomp.models import Competitor

class CompetitorForm(forms.ModelForm):
    class Meta:
        model = Competitor
        fields = (
            'email',
            'legal_name',
            'fan_name',
            'competitor_name',
            'phone_number',
            'twitter_handle',
            'telegram_handle',
            'music_url',
            'is_group',
            'performer_two',
            'performer_three',
            'performer_four',
            'performer_five'
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields
        self.fields['twitter_handle'].required = False
        self.fields['telegram_handle'].required = False
        self.fields['performer_two'].required = False
        self.fields['performer_three'].required = False
        self.fields['performer_four'].required = False
        self.fields['performer_five'].required = False

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
            ),
            Fieldset(
                'Competitor Info',
                'competitor_name',
                'music_url',
                'is_group',

            ),
            Fieldset(
                'Group Registration',
                'performer_two',
                'performer_three',
                'performer_four',
                'performer_five'
            )
        )

        self.helper.add_input(Submit('submit', 'Apply', css_class='float-end'))