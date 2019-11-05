from django.urls import path
from . import views
from .views import PostView

urlpatterns = [
	path('register/', views.register, name='register'),
	path('login/', views.login, name='login'),
	path('posts/', PostView.as_view(), name='posts'),
	path('post/<post_id>', views.get_post, name='get_post'),
	path('post/<post_id>/vote', views.create_vote, name='create_vote'),
	path('post/<post_id>/comment', views.create_comment, name='create_comment'),
	path('logout/', views.logout_view, name='logout_view')
]