from . import views
from django.urls import path

urlpatterns = [
    path('user/register/', views.Register.as_view()),
    path('user/login/', views.Login.as_view()),
    path('user/update/', views.UserView.as_view()),
    path('blog/', views.Blog.as_view()),
]
