from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import DetailView, ListView
from .models import Post, Comment, Like, Category, View, UserProfile
from .forms import CommentForm, LoginForm, SignupForm, UserProfileForm, ContactForm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from django.utils import timezone
import random

def home(request):
    try:
        posts = Post.objects.all().order_by('-date_posted')[:4]
        featured_post  = Post.objects.all().order_by('view_count')[:3]
        category = Category.objects.all()
        recomend = get_user_recommendations(request.user.id, 5)
        context = {
            'posts': posts,
            'category': category,
            'recomend': recomend,
            'featured_post':featured_post
        }
    except Exception as e:

        context = {
            'error_message': str(e)
        }
    return render(request, 'home.html', context)

def search(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        query = request.GET.get('q')
        results = []
        if query:
            search_terms = query.split()
            query_filters = Q()
            for term in search_terms:
                query_filters |= Q(title__icontains=term) | Q(content__icontains=term)
            results = Post.objects.filter(query_filters)
        data = [{'title': post.title, 'content': post.content} for post in results]
        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
def detailed_blog(request, slug):
    detailed_blog = get_object_or_404(Post, slug=slug)
    detailed_blog.view_count += 1
    detailed_blog.save()
    category = Category.objects.all()
    comments = detailed_blog.comments.filter(active=True).order_by('-date_posted')

    if request.user.is_authenticated:
        View.objects.create(user=request.user, post=detailed_blog, viewed_at=timezone.now())

    is_liked = False
    is_disliked = False
    if request.user.is_authenticated:
        user = request.user
        is_liked = Like.objects.filter(post=detailed_blog, user=user).exists()
        is_disliked = Like.objects.filter(post=detailed_blog, user=user).exists()

    if 'like' in request.GET and not is_liked and not is_disliked:
        like = Like(comment=comments[0], user=request.user)
        like.save()
        is_liked = True
    elif 'dislike' in request.GET and not is_liked and not is_disliked:
        dislike = Like(comment=comments[0], user=request.user)
        dislike.save()
        is_disliked = True
    total_like = Like.objects.filter(post=detailed_blog)

    if request.method == 'POST' and request.user.is_authenticated:
        try:
            form = CommentForm(request.POST)

            if form.is_valid():
                Comment.objects.create(
                    post=Post.objects.filter(slug=detailed_blog.slug).first(),
                    author=User.objects.get(id=request.user.id),
                    content=form.cleaned_data['content'],
                    active=True
                )
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'errors': f'{form.errors}'})
        except:
            return JsonResponse({'success': False, 'errors': f'Please log in to write a comment.', 'login_required': True})
    else:
        form = CommentForm()

    return render(request, 'detailed_blog.html',
                  {'blog': detailed_blog, 'category': category, 'comments': comments, 'is_liked': is_liked,
                   'is_disliked': is_disliked, 'total_like': total_like, 'comment_form': form})


@login_required
def like_view(request):
    if request.method == 'GET':
        try:
            post_slug = request.GET.get('post_slug')
            post = Post.objects.filter(slug=post_slug).first()

            if post:
                user = request.user

                if not Like.objects.filter(post=post, user=user).exists():
                    like_count = Like.objects.filter(post=post)
                    like = Like(post=post, user=user)
                    like.save()
                    return JsonResponse({'success': True, 'like_count': len(like_count)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error occurred while processing the like action.', 'error': str(e)})

    return JsonResponse({'success': False})

@login_required
def dislike_view(request):
    if request.method == 'GET':
        try:
            post_slug = request.GET.get('post_slug')
            post = Post.objects.filter(slug=post_slug).first()
            user = request.user

            if Like.objects.filter(post=post, user=user).exists():
                like_count = Like.objects.filter(post=post)
                Like.objects.filter(post=post, user=user).delete()
                return JsonResponse({'success': True, 'like_count': len(like_count)})
        except Exception as e:
            return JsonResponse({'success': False, 'message': 'Error occurred while processing the dislike action.', 'error': str(e)})

    return JsonResponse({'success': False})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            messages.success(request, 'Thank you for your message! We will get back to you soon.')
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


def post_list_by_category(request, category_slug):
    try:
        category = get_object_or_404(Category, slug=category_slug)
        posts = Post.objects.filter(categories=category)
        return render(request, 'post_list.html', {'category': category, 'posts': posts})
    except ObjectDoesNotExist:
        return HttpResponse('Page Not Found')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('profile')
        return super().get(request, *args, **kwargs)


class RegistrationView(CreateView):
    form_class = SignupForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        response = super().form_valid(form)

        user_profile = UserProfile.objects.create(user=self.object)

        return response

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('profile')
        return super().dispatch(request, *args, **kwargs)

@login_required
def profile(request):
    return render(request, 'registration/profile.html',{'in_profile':True})

@login_required
def update_profile(request):
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('myaccount')
        else:
            messages.error(request, 'Error updating your profile. Please correct the errors below.')
    else:
        user_form = UserProfileForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)

    return render(request, 'registration/profile.html', {'update_form': user_form, 'profile_form': profile_form})

@login_required
def myaccount(request):
   
    try:
        if request.user.is_superuser:
            print('yes')
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        else:
            user_profile = UserProfile.objects.get(user=request.user)

    except UserProfile.DoesNotExist:
        user_profile = None
    return render(request, 'registration/profile.html', {'user_profile': user_profile})

@method_decorator(login_required, name='dispatch')
class PostListView(ListView):
    model = Post
    template_name = 'registration/profile.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context['posts']:
            context['post_empty'] = True
        return context

@method_decorator(login_required, name='dispatch')
class PostDetailView(DetailView):
    model = Post
    template_name = 'registration/profile.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    context_object_name = 'post'

@method_decorator(login_required, name='dispatch')
class CategoryListView(ListView):
    model = Category
    template_name = 'registration/profile.html'
    context_object_name = 'categories'
    ordering = ['name']
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context['categories']:
            context['category_empty'] = True
        return context
    
@method_decorator(login_required, name='dispatch')
class PostCreateView(CreateView):
    model = Post
    fields = ['title', 'content', 'categories', 'featured_image']
    template_name = 'registration/profile.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.slug = slugify(post.title)
        post.author = self.request.user

        try:
            form.instance.validate_unique()
        except ValidationError:
            form.add_error('title', 'A post with the same title already exists.')
            return self.form_invalid(form)

        post.save()
        messages.info(self.request, 'Your post has been successfully added.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        form.fields['title'].widget.attrs['class'] = 'form-control'
        form.fields['title'].widget.attrs['placeholder'] = 'Enter the title'
        form.fields['content'].widget.attrs['class'] = 'form-control'
        form.fields['content'].widget.attrs['placeholder'] = 'Enter the content'
        form.fields['categories'].widget.attrs['class'] = 'form-control'
        form.fields['categories'].widget.attrs['placeholder'] = 'Enter the categories'
        form.fields['featured_image'].widget.attrs['class'] = 'form-control'
        form.fields['featured_image'].widget.attrs['placeholder'] = 'Enter the featured image'
        context['post_create_form'] = form
        return context
        

@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ['title', 'content', 'categories', 'featured_image']
    template_name = 'registration/profile.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    context_object_name = 'update_post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        form.fields['title'].widget.attrs['class'] = 'form-control'
        form.fields['title'].widget.attrs['placeholder'] = 'Enter the title'
        form.fields['content'].widget.attrs['class'] = 'form-control'
        form.fields['content'].widget.attrs['placeholder'] = 'Enter the content'
        form.fields['categories'].widget.attrs['class'] = 'form-control'
        form.fields['categories'].widget.attrs['placeholder'] = 'Enter the categories'
        form.fields['featured_image'].widget.attrs['class'] = 'form-control'
        form.fields['featured_image'].widget.attrs['placeholder'] = 'Enter the featured image'
        context['post_update_form'] = form
        return context
    
    def form_valid(self, form):
        post = form.save(commit=False)
        post.slug = slugify(post.title)
        post.author = self.request.user
        post.save()
        messages.info(self.request, 'Your Post has been successfully updated.')
        return super().form_valid(form)

@login_required
def delete_post(request, slug):

    main_post = get_object_or_404(Post, slug = slug)

    main_post.delete()

    messages.error(request, 'Post deleted successfully.')

    return redirect('post-list')

@login_required
def delete_category(request, slug):

    main_category = get_object_or_404(Category, slug = slug)

    main_category.delete()

    messages.error(request, 'Category deleted successfully.')

    return redirect('category-list')

@method_decorator(login_required, name='dispatch')
class CategoryCreateView(CreateView):
    model = Category
    fields = ['name']
    template_name = 'registration/profile.html'
    success_url = reverse_lazy('category-list')

    def form_valid(self, form):
        category = form.instance
        category.slug = slugify(category.name)

        if Category.objects.filter(slug=category.slug).exists():
            form.add_error('name', 'Category with the same name already exists.')
            return self.form_invalid(form)
        
        messages.info(self.request, 'The category has been successfully added.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        form.fields['name'].widget.attrs['class'] = 'form-control'
        form.fields['name'].widget.attrs['placeholder'] = 'Enter the title'
        context['category_create_form'] = form
        return context

@method_decorator(login_required, name='dispatch')
class CategoryUpdateView(UpdateView):
    model = Category
    fields = ['name']
    template_name = 'registration/profile.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('category-list')
 
    def form_valid(self, form):
        category = form.save(commit=False)
        category.slug = slugify(category.name)  
        category.save()
        messages.info(self.request, 'Your Category has been successfully updated.')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = context['form']
        form.fields['name'].widget.attrs['class'] = 'form-control'
        form.fields['name'].widget.attrs['placeholder'] = 'Enter the title'
        context['category_update_form'] = form
        return context

@method_decorator(login_required, name='dispatch')
class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'category_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('category_list')


def terms_condition(request):
    return render(request, 'terms_condition.html')


def get_user_recommendations(user_id, num_recommendations=5):
    liked_posts = set(Like.objects.filter(user_id=user_id).values_list('post_id', flat=True))
    viewed_posts = set(View.objects.filter(user_id=user_id).values_list('post_id', flat=True))
    commented_posts = set(Comment.objects.filter(author_id=user_id).values_list('post_id', flat=True))

    posts = Post.objects.all()
    post_titles = [post.title for post in posts]
    post_content = [post.content for post in posts]

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(post_content)
    cosine_similarities = linear_kernel(tfidf_matrix, tfidf_matrix)

    similarity_scores = {}

    for post_id in liked_posts | viewed_posts | commented_posts:
        post_index = post_titles.index(Post.objects.get(id=post_id).title)
        scores = list(enumerate(cosine_similarities[post_index]))

        for index, score in scores:
            if index != post_index:
                if index in similarity_scores:
                    similarity_scores[index] += score
                else:
                    similarity_scores[index] = score

    sorted_scores = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)
    random.shuffle(sorted_scores) 
    sorted_posts = [posts[index] for index, _ in sorted_scores]
    top_n_posts = sorted_posts[:num_recommendations]

    return top_n_posts

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')
