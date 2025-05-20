from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def star_rating(value):
    try:
        value = float(value)
    except:
        return ''
    full_stars = int(value)
    empty_stars = 5 - full_stars
    return '★' * full_stars + '☆' * empty_stars
