from django import template

register=template.Library()
@register.simple_tag
def leads_count(leads_query, category_name):
    return leads_query.filter(category__name=category_name).count()