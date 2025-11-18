from django.db import models

# Create your models here.

class UserModel(models.Model):
    class Roles(models.TextChoices):
        USER = "user"
        ADMIN = "admin"

    username = models.CharField(max_length=150, unique=True, primary_key=True)
    fullname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=Roles.choices, default=Roles.USER)



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    desc = models.TextField()

    def __str__(self):
        return self.name


class Blog(models.Model):

    class STATUS(models.TextChoices):
        PUBLISHED = "published"
        DRAFT = "draft"
        ARCHIEVED = 'ARCHIEVED'

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()

    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS.choices, default=STATUS.DRAFT)

    author = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class Comment(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    post = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="comments")
    comment_content = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"



