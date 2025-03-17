from django import template
from ..views import tags
from random import choice, randint
register = template.Library()
@register.inclusion_tag('askme/components/tags.html')
def most_popular_tags():
    colors = ['danger', 'primary', 'success', 'dark', 'info', 'warning', 'secondary', 'light']
    most_popular_tags_arr = [{ 'tag_' : tags[randint(0,len(tags) - 1)], 'color' :  choice(colors)} for _ in range(20)]
    colors
    return {'most_popular_tags_arr' : most_popular_tags_arr}

@register.inclusion_tag('askme/components/best_members.html')
def best_members():
    members = ['MrMr', 'ChatGPT', 'Aboba', 'MrBeast', 'Shrek', 'Watermelon', 'Kony Tanev']
    return {'best_members_arr' : members}