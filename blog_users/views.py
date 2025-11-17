import jwt, json
import datetime
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .passwords import hash_password, verify_password
from .serializers import UserSerializer
from .models import UserModel

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
        # but if the client sends PATCH as form-data/Postman form-data, request.POST works.
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



class Blog(View):
    def get(self, request):
        return JsonResponse({'status': 'Worked well'})