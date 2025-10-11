from django.urls import path

from users import views
from users.views import BabyListView,  BabyInfoDetailView, BabyDeleteView, BabyCreateView, BabyUpdateView

app_name = 'users'
urlpatterns = [


    path('baby/',BabyListView.as_view(),name="baby"),

    path('babydetail/<uuid:pk>/',BabyInfoDetailView.as_view(),name="baby_detail"),

    path('babyadd/',BabyCreateView.as_view(),name="baby_add"),

    path('babyupdate/<uuid:pk>/',BabyUpdateView.as_view(),name="baby_update"),

    path('babydelete/<uuid:pk>/',BabyDeleteView.as_view(),name="baby_delete"),

    path('login/', views.login, name='login'),

    path("register/", views.register, name="register"),

    path("logout/", views.logout, name="logout"),

    path("passwordchange/", views.passwordchange, name="passwordchange"),

    path("usercenterchange/", views.usercenterchange, name="usercenterchange"),

    path("usercenter/", views.usercenter, name="usercenter"),

    path("active/<str:id>", views.active, name="active"),

    path("admin", views.UserManagement.as_view(), name="admin"),

]