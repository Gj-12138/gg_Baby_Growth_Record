
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from main.forms import ArticleForm
from main.models import Articles, Category


# Create your views here.
def index(request):
    return render(request,'main/index.html')

class ArticleListView(ListView):
    model = Articles
    context_object_name = 'articles'
    template_name = 'main/article_list.html'
    paginate_by = 10

class ArticleDetailView(DetailView):
    queryset = Articles.objects.all()
    context_object_name = 'articles'
    template_name = 'main/article_detail.html'

class ArticleCreateView(CreateView):
    model = Articles
    context_object_name = 'articles'
    template_name = 'main/article_form.html'
    form_class = ArticleForm
    success_url = reverse_lazy('main:article_list')

class ArticleUpdateView(UpdateView):
    model = Articles
    context_object_name = 'articles'
    template_name = 'main/article_form.html'
    form_class = ArticleForm
    success_url = reverse_lazy('main:article_list')

class ArticleDeleteView(DeleteView):
    model = Articles
    context_object_name = 'articles'
    template_name = 'main/article_confirm_delete.html'
    success_url = reverse_lazy('main:article_list')


class CategoryListView(ListView):
    model = Category
    template_name = 'main/classification.html'
    extra_context = {
        "category" : Category.objects.filter(classification_parent__isnull=True).order_by('classification'),
    }
