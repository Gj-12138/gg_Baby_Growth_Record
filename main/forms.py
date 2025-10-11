from ckeditor.widgets import CKEditorWidget
from django import forms
from django.views.generic import UpdateView

from main.models import Articles


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Articles
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class':'form-control'}),
            'content': CKEditorWidget(attrs={'class':'form-control'}),
        }
