import jwt, json
import datetime
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .passwords import hash_password, verify_password
from .serializers import UserSerializer, BlogSerializer, CommentSerializer
from .models import UserModel, Blog, Comment
from utils.email_utils import send_dynamic_email

# Create your views here.

from django.conf import settings
SECRET_KEY = settings.SECRET_KEY



@method_decorator(csrf_exempt, name='dispatch')
class Register(View):
    def post(self, request):
        data = {
            "username": request.POST.get("username"),
            "fullname": request.POST.get("fullname"),
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
            "role": request.POST.get("role", "USER"),
        }

        if data['password']:
            data['password'] = hash_password(data['password'])

        serializer = UserSerializer(data=data)

        if serializer.is_valid():
            serializer.save()

            send_dynamic_email(request, data.email, data.fullname, 'welcome_email')
            return JsonResponse({
                "status": True,
                "message": "User registered successfully",
                "data": serializer.data  # password hidden automatically
            }, status=201)

        return JsonResponse({
            "status": False,
            "errors": serializer.errors
        }, status=400)




@method_decorator(csrf_exempt, name='dispatch')
class Login(View):
    def post(self, request):

        username = request.POST.get("username")
        password = request.POST.get("password")

        if not username or not password:
            return JsonResponse({"status": False, "message": "Email and password required"}, status=400)

        # Check user existence
        try:
            user = UserModel.objects.get(username=username)
        except UserModel.DoesNotExist:
            return JsonResponse({"status": False, "message": "Invalid email or password"}, status=400)

        # Verify password
        if not verify_password(password, user.password):
            return JsonResponse({"status": False, "message": "Invalid email or password"}, status=400)

        # Create JWT payload
        payload = {
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),  # expiry time
            "iat": datetime.datetime.utcnow()                                # issued at
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return JsonResponse({
            "status": True,
            "message": "Login successful",
            "token": token,
            "user": {
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }, status=200)
    


@method_decorator(csrf_exempt, name='dispatch')
class UserView(View):
    #patch, delete

    def patch(self, request):
        user = request.user   # user is added by your JWT middleware

        if not user:
            return JsonResponse(
                {"status": False, "message": "Unauthorized"},
                status=401
            )

        # Django doesn't parse PATCH body automatically for form-data,
        # but if the client sends PATCH as form-data/Blogman form-data, request.POST works.
        data = json.loads(request.body)
        print(data)

        if data['password']: 
            data['password'] = hash_password(data['password'])

        # Use serializer for partial update
        serializer = UserSerializer(
            user,
            data=data,
            partial=True  # allows updating only provided fields
        )

        if serializer.is_valid():
            serializer.save()
            return JsonResponse({
                "status": True,
                "message": "User updated successfully",
                "data": serializer.data
            }, status=200)

        return JsonResponse({
            "status": False,
            "errors": serializer.errors
        }, status=400)

 

@method_decorator(csrf_exempt, name='dispatch')
class BlogView(View):
    def get(self, request):
        return JsonResponse({'status': 'Worked well'})

    def post(self, request):
        """
        Create a new post
        """
        data = json.loads(request.body)
        print(request.user)
        data['author'] = request.user.username
        print(data)
        serializer = BlogSerializer(data=data)

        #Category missed.

        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        post = serializer.save(author=request.user)
        return JsonResponse(BlogSerializer(post).data, status=201)

    def patch(self, request, blog_id):
        """
        Edit existing post
        """
        try:
            post = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            return JsonResponse({"error": "Blog not found"}, status=404)

        # if not self.has_permission(request, post):
        #     return self.permission_denied()
        print(post.author)
        print(request.user.username)

        if post.author != request.user:
            return JsonResponse(
                {"error": "Permission denied"},
                status=403
            )


        data = json.loads(request.body)

        serializer = BlogSerializer(post, data=data, partial=True)

        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        updated_post = serializer.save()

        return JsonResponse(BlogSerializer(updated_post).data, status=200)

    def delete(self, request, blog_id):
        """
        Delete post (owner or admin only)
        """
        try:
            post = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            return JsonResponse({"error": "Blog not found"}, status=404)

        if (post.author != request.user) and request.user.role != 'admin':
            return JsonResponse(
                {"error": "Permission denied"},
                status=403
            )
        

        post.delete()
        return JsonResponse({"message": "Blog deleted successfully"}, status=200)







@method_decorator(csrf_exempt, name='dispatch')
class CommentView(View):
    def get(self, request):
        return JsonResponse({'status': 'Worked well'})

    def post(self, request):
        """
        Create a new post
        """
        data = json.loads(request.body)
        print(request.user)
        serializer = CommentSerializer(data=data)

        #Category missed.

        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        comment = serializer.save(user=request.user)
        auther_obj = comment.post.author
        send_dynamic_email(request, auther_obj.email, auther_obj.fullname, 'comment_added')

        return JsonResponse(CommentSerializer(comment).data, status=201)

    def patch(self, request, comment_id):
        """
        Edit existing post
        """
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            return JsonResponse({"error": "Comment not found"}, status=404)

        # if not self.has_permission(request, post):
        #     return self.permission_denied()
        print(comment.user)
        print(request.user.username)

        if comment.user != request.user:
            return JsonResponse(
                {"error": "Permission denied"},
                status=403
            )


        data = json.loads(request.body)

        serializer = CommentSerializer(comment, data=data, partial=True)

        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=400)

        updated_comment = serializer.save()

        return JsonResponse(CommentSerializer(updated_comment).data, status=200)

    def delete(self, request, comment_id):
        """
        Delete post (owner or admin only)
        """
        try:
            comment = Comment.objects.get(id=comment_id)
        except Blog.DoesNotExist:
            return JsonResponse({"error": "Blog not found"}, status=404)
        print('Hello')
        print(comment.post)
        print('Hi')
        print(comment.post.author)

        if (comment.user != request.user) and (request.user.role != 'admin') and (request.user != comment.post.author):
            return JsonResponse(
                {"error": "Permission denied"},
                status=403
            )
        

        comment.delete()
        return JsonResponse({"message": "Blog deleted successfully"}, status=200)
