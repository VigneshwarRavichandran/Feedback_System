from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.shortcuts import get_object_or_404
from .models import Post, Vote, Comment
from django.views import View
from django.contrib import messages
from django.http import HttpResponse

def register(request):
	context = {
		'error' : None,
	}
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		email = request.POST.get('email')
		try:
			user = User.objects.create_user(username, email, password)
			user.save()
			return redirect(login)
		except:
			context['error'] = 'User already exsists'
	return render(request, 'register.html', context)

def login(request):
	context = {
		'error' : None,
	}
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user is not None:
			setattr(request, 'user', user)
			request.session['user_id'] = user.id
			return redirect('posts')
		context['error'] = 'Invalid credentials'
		return render(request, 'login.html', context)
	return render(request, 'login.html', context)

class PostView(View):
	template_name = 'post/posts.html'
  
	def get(self, request, *args, **kwargs):
		context = {
		 'posts' : []
		}
		posts = Post.objects.all()
		print(posts)
		# posts = Post.objects.prefetch_related('votes', 'comments').annotate(Count('votes', distinct=True)).annotate(Count('comments', distinct=True)).values(
		# 	'id', 'title', 'content', 'votes__count', 'comments__count')
		# voted_post_ids = Vote.objects.prefetch_related('posts').filter(votedby_id=request.session['user_id']).values_list('post', flat=True)
		# for post in posts:
		# 	is_voted = False
		# 	if post['id'] in voted_post_ids:
		# 		is_voted = True
		# 	context['posts'].append({
		# 		'id' : post['id'],
		# 		'title' : post['title'],
		# 		'content' : post['content'],
		# 		'votes' : post['votes__count'],
		# 		'is_voted' : is_voted,
		# 		'total_comments' : post['comments__count']
		# 	})
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		user_id = request.session['user_id']
		post_title = request.POST.get('post_title')
		post_content = request.POST.get('post_content')
		post = Post(title=post_title, content=post_content, createdby_id=user_id)
		post.save()
		messages.success(request, 'Posted Successfully')
		return redirect('posts')