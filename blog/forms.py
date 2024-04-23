from django import forms

from blog.models import BlogPost
from clients.forms import StyleFormMixin


class BlogPostForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = BlogPost
        exclude = ('slug',)
