from django import template
from ..views import tags
from random import choice, randint
from ..models import Tag, Profile
register = template.Library()
@register.inclusion_tag('askme/components/tags.html')
def most_popular_tags():
    colors = ['danger', 'primary', 'success', 'dark', 'info', 'warning', 'secondary', 'light']
    tags = Tag.objects.popular()
    most_popular_tags_arr = [{'tag_': tag, 'color': choice(colors)} for tag in tags]
    return {'most_popular_tags_arr' : most_popular_tags_arr}

@register.inclusion_tag('askme/components/best_members.html')
def best_members():
    members = Profile.objects.top_users()[:10]

    # members = ['MrMr', 'ChatGPT', 'Aboba', 'MrBeast', 'Shrek', 'Watermelon', 'Kony Tanev']
    return {'best_members_arr' : members}