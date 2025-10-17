from django.template.library import Library
from django.utils.html import strip_tags
from django.utils.text import Truncator

from main.models import Category, Tag, Collect, Like
from users.models import User

register = Library()

@register.filter()
def my_attr(value,classname):
    # print(dir(value))
    return value.as_widget(attrs={'class':classname})

@register.simple_tag()
def get_usersname():
    value = User.objects.values('username')
    return value


@register.simple_tag
def get_categorys():
    """
    分类
    :return:
    """
    return Category.objects.filter(classification_parent__isnull=True)
@register.simple_tag
def get_tags():
    """
    标签
    :return:
    """
    return Tag.objects.filter()


@register.filter(name='safe_truncate')
def safe_truncate(value, length=150):
    """
    先移除富文本中的HTML标签，再截断到指定长度
    :param value: 富文本内容（含HTML标签）
    :param length: 截断后的最大长度
    :return: 处理后的纯文本片段
    """
    # 移除所有HTML标签，得到纯文本
    plain_text = strip_tags(value)
    # 截断纯文本到指定长度，末尾添加省略号
    truncated_text = Truncator(plain_text).chars(length, truncate='...')
    return truncated_text

@register.filter(name='has_collected')
def collect_state(article,user):
    bool_state = Collect.objects.filter(article=article,user=user).exists()
    if bool_state:
        return True
    return False

@register.filter(name='has_liked')
def liked_state(article,user):
    bool_state = Like.objects.filter(article=article, user=user).exists()
    if bool_state:
        return True
    return False


