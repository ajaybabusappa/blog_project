from rest_framework import serializers
from .models import UserModel, Blog, Comment


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserModel
        fields = ["username", "fullname", "email", "password", "role"]
        extra_kwargs = {
            "password": {"write_only": True},
        }



class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "content",
            "category",
            "status",
            "author",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author", "created_at", "updated_at"]


    
class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "user", "post", "comment_content", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "created_at", "updated_at"]