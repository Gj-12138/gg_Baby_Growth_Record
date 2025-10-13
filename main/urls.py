from django.urls import path

from main import views

app_name = 'main'
urlpatterns = [
    path('',views.index,name="index"),

    path('article_list/',views.ArticleListView.as_view(),name="article_list"),

    path('article_manage/',views.ArticleManageView.as_view(),name="article_manage"),

    path('article_detail/<int:pk>/',views.ArticleDetailView.as_view(),name="article_detail"),

    path('article_form/',views.ArticleCreateView.as_view(),name="article_form"),

    path('article_update/<int:pk>/',views.ArticleUpdateView.as_view(),name="article_update"),

    path('article_delete/<int:pk>/',views.ArticleDeleteView.as_view(),name="article_delete"),

    path('collect_articles/',views.collect_articles,name="collect_articles"),

    path('link_articles/',views.like_articles,name="link_articles"),

    # 评论提交：单独的Ajax视图（处理POST请求）
    path('article/<int:article_id>/add-comment/', views.add_comment, name='add_comment'),

]
