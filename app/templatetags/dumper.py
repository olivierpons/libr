from django import template
from django.template.defaultfilters import linebreaksbr
from django.utils.html import escape

try:
    from django.utils.safestring import mark_safe
except ImportError:  # v0.96 and 0.97-pre-autoescaping compat
    def mark_safe(x): return x
from pprint import pformat


register = template.Library()


@register.filter('raw_dump')
def raw_dump(x):
    if hasattr(x, '__dict__'):
        d = {
            '__str__': str(x),
            '__unicode__': x,
            '__repr__': repr(x),
        }
        d.update(x.__dict__)
        x = d
    output = pformat(x)+'\n'
    return output


@register.filter('dump')
def dump(x):
    return mark_safe(linebreaksbr(escape(raw_dump(x))))

