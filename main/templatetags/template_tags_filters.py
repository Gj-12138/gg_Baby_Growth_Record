from django.template.library import Library

from main.models import Category
from users.models import User

register = Library()

@register.filter()
def my_attr(value,classname):
    # print(dir(value))
    return value.as_widget(attrs={'class':classname})

@register.simple_tag()
def get_usersname():
    value = User.objects.values('username')

    print(dir(value))
    return value


@register.simple_tag
def get_categorys():
    return Category.objects.filter(classification_parent__isnull=True)
