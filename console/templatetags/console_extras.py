from datetime import timedelta
from django import template
from django.template.base import TemplateSyntaxError

register = template.Library()

@register.filter()
def pretty_delta(timedeltaobj):
    """Convert a datetime.timedelta object into Days, Hours, Minutes, Seconds."""
    if not isinstance(timedeltaobj, timedelta): raise TemplateSyntaxError("pretty_delta requires a timedelta object.")

    secs = timedeltaobj.total_seconds()
    timetot = ""
    if secs > 86400: # 60sec * 60min * 24hrs
        days = secs // 86400
        timetot += "{} days".format(int(days))
        secs = secs - days*86400

    if secs > 3600:
        hrs = secs // 3600
        timetot += " {} hours".format(int(hrs))
        secs = secs - hrs*3600

    if secs > 60:
        mins = secs // 60
        timetot += " {} minutes".format(int(mins))
        secs = secs - mins*60

    if secs > 0:
        timetot += " {} seconds".format(int(secs))
    return timetot
