from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def verbose_name(instance):
    return instance._meta.verbose_name

@register.simple_tag
def star_rating(rating, max_rating=5):
    html = ''.join([f'<span class="star unfilled">☆</span>' for _ in range(max_rating - int(rating))] +
                   [f'<span class="star filled">★</span>' for _ in range(int(rating))])
    return mark_safe(html)