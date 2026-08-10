from django.db import models
from django.conf import settings

# Create your models here.
def image_upload_path(instance, filename):
    return f'{instance.pk}/{filename}'

class Tag(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Post(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, blank=True)
    image = models.ImageField(upload_to=image_upload_path, blank=True, null=True)
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    like = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='likes', blank=True)
    like_count = models.PositiveIntegerField(default=0)
    click_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, blank=False, null=False, on_delete=models.CASCADE, related_name='comments')
    writer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
