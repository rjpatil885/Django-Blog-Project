from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from django.template.defaultfilters import slugify


class UserProfile(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  profile_picture = models.ImageField(upload_to='profile_pictures', null=True, blank=True)
  bio = models.TextField()
  social_media_links = models.URLField()

  def __str__(self):
    return self.user.username


class Category(models.Model):
  name = models.CharField(max_length=100)
  slug = models.SlugField(unique=True)

  def __str__(self):
      return self.name

  def save(self, *args, **kwargs):
      # Generate a unique slug from the name field
      self.slug = slugify(self.name)

      super().save(*args, **kwargs)



class Post(models.Model):
  title = models.CharField(max_length=200)
  content = models.TextField()
  date_posted = models.DateTimeField(default=timezone.now)
  author =  models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  categories = models.ManyToManyField(Category)
  featured_image = models.ImageField(upload_to='post_images', null=True, blank=True)
  slug = models.SlugField(unique=True)
  view_count = models.PositiveIntegerField(default=0)

  def display_image(self):
    if self.featured_image:
      return self.featured_image.url
    else:
      return "No Image Available"

  def __str__(self):
    return self.title

  def get_absolute_url(self):
    return reverse('post-detail', kwargs={'slug': self.slug})

  def save(self, *args, **kwargs):
    if not self.slug:
      self.slug = slugify(self.title)
    super().save(*args, **kwargs)


class Comment(models.Model):
  post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
  author =  models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  content = models.TextField()
  date_posted = models.DateTimeField(default=timezone.now)
  active = models.BooleanField(default=True)

  def __str__(self):
    return f'Comment by {self.author} on {self.post}'


class Like(models.Model):
  post = models.ForeignKey(Post, on_delete=models.CASCADE)
  user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

  def __str__(self):
    return f'Like by {self.user.username} on {self.post.title}'



class NewsletterSubscription(models.Model):
  email = models.EmailField(unique=True)

  def __str__(self):
    return self.email


class View(models.Model):
  user = models.ForeignKey(User, on_delete=models.PROTECT)
  post = models.ForeignKey(Post, on_delete=models.SET_NULL, null=True)
  viewed_at = models.DateTimeField(auto_now_add=True)

