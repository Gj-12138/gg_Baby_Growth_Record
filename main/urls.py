from django.urls import path

from main import views

app_name = 'main'
urlpatterns = [
    path('',views.index,name="index"),

    path('article_list/',views.ArticleListView.as_view(),name="article_list"),

    path('article_detail/<int:pk>/',views.ArticleDetailView.as_view(),name="article_detail"),

    path('article_form/',views.ArticleCreateView.as_view(),name="article_form"),

    path('article_update/<int:pk>/',views.ArticleUpdateView.as_view(),name="article_update"),

    path('article_delete/<int:pk>/',views.ArticleDeleteView.as_view(),name="article_delete"),

    path('category/',views.CategoryListView.as_view(),name="category"),


]
