import jwt
import time
from django.http import JsonResponse
from django.conf import settings

from blog_users.models import UserModel  # change to your app name


ALLOWED_PATHS = [
    "/user/register/",
    "/user/login/",
]


class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response



    def __call__(self, request):
        print('Call function called')
        # Allow Register & Login routes without token
        path = request.path
        print(path)
        if path in ALLOWED_PATHS:
            return self.get_response(request)

        # Get Token from header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse(
                {"status": False, "message": "Unauthorized: Token missing"},
                status=401
            )

        # Token must be in 'Bearer <token>' format
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JsonResponse(
                {"status": False, "message": "Unauthorized: Invalid token format"},
                status=401
            )

        token = parts[1]

        try:
            # Decode Token
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
        except jwt.ExpiredSignatureError:
            return JsonResponse(
                {"status": False, "message": "Forbidden: Token expired"},
                status=403
            )

        except jwt.InvalidTokenError:
            return JsonResponse(
                {"status": False, "message": "Forbidden: Invalid token"},
                status=403
            )

        # Fetch user from DB
        try:
            user = UserModel.objects.get(username=payload["username"])
        except UserModel.DoesNotExist:
            return JsonResponse(
                {"status": False, "message": "Forbidden: User does not exist"},
                status=403
            )

        # Attach user object to request
        request.user = user

        return self.get_response(request)
    


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip = request.META.get("REMOTE_ADDR")
        user = getattr(request, "user", None)
        print(ip, user, request.path)

        return self.get_response(request)



class ExecutionTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()

        response = self.get_response(request)

        end = time.time()
        execution_time = round((end - start) * 1000, 2)  # in ms

        response["X-Execution-Time"] = f"{execution_time}ms"

        return response