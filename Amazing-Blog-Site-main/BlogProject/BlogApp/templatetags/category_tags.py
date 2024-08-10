from django import template
from BlogApp.models import Category

register = template.Library()

@register.simple_tag
def get_all_categories():
  return Category.objects.all()