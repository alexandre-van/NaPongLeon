from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import CustomUser, Friendship
import re
#from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    friends = serializers.SerializerMethodField()
    pending_friend_requests = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'email', 'avatar_url', 'nickname', 'friends', 'pending_friend_requests')
        extra_kwargs = {
            'password': {
                'write_only': True,
                'error_messages': {
                    'max_length': 'Password must be 3 characters or less'
                }
            },
            'email': {
                'required': True,
                'validators': [
                    UniqueValidator(
                        queryset=CustomUser.objects.all(),
                        message='Email address must be unique.'
                    )
                ]
            },
            'nickname': {
                'max_length': 30,
                'required': False,
                'error_messages': {
                    'max_length': 'Nickname must be 30 characters or less'
                }
            }
        }

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user
    
    def validate_username(self, value):
        special_chars = re.compile(r'[!@#$%^&*(),.?":{}|<>_-]')
        if special_chars.search(value):
            raise serializers.ValidationError("Username cannot contain special characters")
        return value

    def validate_password(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Password must have at least 10 characters")
        special_chars = re.compile(r'[!@#$%^&*(),.?":{}|<>_-]')
        if not special_chars.search(value):
            raise serializers.ValidationError("Password must have at least a special character")
        has_digit = False
        has_upper = False
        for c in value:
            if c.isupper():
                has_upper = True
            if c.isdigit():
                has_digit = True
            if has_upper and has_digit:
                return value
        if not has_digit:
            raise serializers.ValidationError("Password must have at least a numerical character")
        if not has_upper:
            raise serializers.ValidationError("Password must have at least a uppercase character")
        
    
    def validate_avatar_url(self, value):
        validator = URLValidator()
        try:
            validator(value)
        except ValidationError:
            raise serializers.ValidationError("Invalid URL for avatar")
        return value

    def get_friends(self, obj):
        return obj.friends
#        return [friend.username for friend in obj.get_friends()] # get_friends from models.py

    def get_pending_friend_requests(self, obj):
        return [user.username for user in obj.get_pending_friend_requests()] # get_pending_friend_requests from models.py

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)



class FriendshipSerializer(serializers.ModelSerializer):
    from_user = serializers.StringRelatedField()
    to_user = serializers.StringRelatedField()

    class Meta:
        model = Friendship
        fields = ('from_user', 'to_user', 'status', 'created_at')
