import markdown

from django.template import Template, Context

def helper_expand_email_content(content, context):
    template = Template(markdown.markdown(content))

    return template.render(Context(context))