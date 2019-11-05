from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout
from django.shortcuts import get_object_or_404
from .models import Post, Vote, Comment
from django.views import View
from django.contrib import messages
from django.db.models import Count
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
		posts = Post.objects.prefetch_related('vote', 'comment').annotate(Count('vote', distinct=True)).annotate(Count('comment', distinct=True)).values(
			'id', 'title', 'content', 'vote__count', 'comment__count')
		voted_post_ids = Vote.objects.prefetch_related('posts').filter(votedby_id=request.session['user_id']).values_list('post', flat=True)
		for post in posts:
			is_voted = False
			if post['id'] in voted_post_ids:
				is_voted = True
			context['posts'].append({
				'id' : post['id'],
				'title' : post['title'],
				'content' : post['content'],
				'votes' : post['vote__count'],
				'is_voted' : is_voted,
				'total_comments' : post['comment__count']
			})
		return render(request, self.template_name, context)

	def post(self, request, *args, **kwargs):
		user_id = request.session['user_id']
		post_title = request.POST.get('post_title')
		post_content = request.POST.get('post_content')
		post = Post(title=post_title, content=post_content, createdby_id=user_id)
		post.save()
		messages.success(request, 'Posted Successfully')
		return redirect('posts')

def create_vote(request, post_id):
	user_id = request.session['user_id']
	vote, created = Vote.objects.get_or_create(votedby_id=user_id, post_id=post_id)
	if created:
		messages.success(request, 'Voted Successfully')
	else:
		messages.warning(request, "Sorry, you have voted already!")
	return redirect('posts')

def get_post(request, post_id):
	user_id = request.session['user_id']
	post = Post.objects.prefetch_related('vote', 'comment').filter(id=post_id).annotate(Count('vote', distinct=True)).annotate(Count('comment', distinct=True)).values(
			'id', 'title', 'content', 'vote__count', 'comment__count')
	voted_post_ids = Vote.objects.prefetch_related('posts').filter(votedby_id=request.session['user_id']).values_list('post', flat=True)
	post_comments = Post.objects.prefetch_related('comment').filter(id=post_id).values(
			'comment__commentedby__username','comment__text')
	post = post[0]
	comments = []
	for post_comment in post_comments:
		if post_comment['comment__commentedby__username'] is not None:
			comments.append({
					'commentedby' : post_comment['comment__commentedby__username'],
					'text' : post_comment['comment__text']
				})
	is_voted = False
	if post['id'] in voted_post_ids:
		is_voted = True
	context = {
		'id' : post['id'],
		'title' : post['title'],
		'content' : post['content'],
		'votes' : post['vote__count'],
		'is_voted' : is_voted,
		'total_comments' : post['comment__count'],
		'comments' : comments
	}
	return render(request, 'post/post.html', context)


def create_comment(request, post_id):
	context = {
		'posts' : None
	}
	user_id = request.session['user_id']
	if request.method == 'POST':
		if 'comment' in request.POST:
			post_comment = request.POST.get('post_comment')
			comment = Comment.objects.create(commentedby_id=user_id, text=post_comment, post_id=post_id)
			messages.success(request, 'Commented Successfully')
	return redirect('get_post', post_id)

def logout_view(request):
	logout(request)
	return redirect(login)