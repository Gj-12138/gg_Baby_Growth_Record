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

    path('like_articles/',views.like_articles,name="like_articles"),

    # 评论提交：单独的Ajax视图（处理POST请求）
    path('article/<int:article_id>/add-comment/', views.add_comment, name='add_comment'),

    path('article/<int:article_id>/delete_comment/', views.delete_comment, name='delete_comment'),

    # 成长记录
    path('record_list/',views.RecordListView.as_view(),name="record_list"),

    path('record_detail/<uuid:pk>/',views.RecordDetailView.as_view(),name="record_detail"),

    path('record_create/', views.RecordCreateView.as_view(), name="record_create"),

    # 上传照片（AJAX 接口）
    path('upload_photos/', views.upload_photos, name='upload_photos'),

#     疫苗
    path('vaccine_list/',views.VaccineListView.as_view(),name='vaccine_list'),

    path('vaccine_detail/<uuid:pk>/',views.VaccineDetailView.as_view(),name='vaccine_detail'),

    path('vaccine_record_list/',views.VaccineRecordListView.as_view(),name='vaccine_record_list'),

    path('vaccine_record_detail/<uuid:pk>/',views.VaccineRecordDetailView.as_view(),name='vaccine_record_detail'),

    path('vaccine_record_create/',views.VaccineRecordCreateView.as_view(),name='vaccine_record_form'),

    path('vaccine_record_confirm_delete/<uuid:pk>/',views.VaccineRecordDeleteView.as_view(),name='vaccine_record_confirm_delete'),

    # 里程碑事件
    path('event_list/', views.EventListView.as_view(), name='event_list'),

    path('event_detail/<uuid:pk>/', views.EventDetailView.as_view(), name='event_detail'),

    path('event_create/<uuid:baby_id>/', views.EventCreateView.as_view(), name='event_create'),

    path('event_update/<uuid:pk>/', views.EventUpdateView.as_view(), name='event_update'),

    path('event_confirm_delete/<uuid:pk>/', views.VaccineRecordDeleteView.as_view(),name='event_confirm_delete'),


]
