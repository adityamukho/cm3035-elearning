from rest_framework import serializers
from .models import User, Profile

class ProfileSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['avatar']

    def get_avatar(self, obj):
        if obj.avatar:
            return obj.avatar.url.replace('http://testserver', '')
        return None

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        if 'avatar' in validated_data:
            instance.avatar.name = validated_data['avatar'].name
            instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id', 'username', 'email']

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()
        return instance
