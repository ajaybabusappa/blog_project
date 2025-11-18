from . import views
from django.urls import path

urlpatterns = [
    path('user/register/', views.Register.as_view()),
    path('user/login/', views.Login.as_view()),
    path('user/update/', views.UserView.as_view()),
    path('blog/', views.BlogView.as_view()),
    path('blog/<int:blog_id>', views.BlogView.as_view()),
    path('comment/', views.CommentView.as_view()),
    path('comment/<int:comment_id>', views.CommentView.as_view()),
]
