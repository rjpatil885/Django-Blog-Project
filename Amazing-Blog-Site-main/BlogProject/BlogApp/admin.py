from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import UserProfile, Category, Post, Comment, Like, NewsletterSubscription, View

admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(NewsletterSubscription)
admin.site.register(View)
