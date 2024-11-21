from rest_framework import serializers
from .models import CustomUser, Friendship

class UserSerializer(serializers.ModelSerializer):
    friends = serializers.SerializerMethodField()
    pending_friend_requests = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'avatar_url', 'nickname', 'friends', 'pending_friend_requests')
        extra_kwargs = {
            'password': {'write_only': True},
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
