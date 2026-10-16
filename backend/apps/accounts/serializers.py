from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Profile
User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("locale", "target_level", "daily_goal_minutes", "timezone")

class MeSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()
    class Meta:
        model = User
        fields = ("id", "username", "email", "first_name", "last_name", "profile")
        read_only_fields = ("id", "username", "email")
    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if validated_data:
            instance.save()
        profile, _ = Profile.objects.get_or_create(user=instance)
        for field, value in profile_data.items():
            setattr(profile, field, value)
        if profile_data:
            profile.save()
        return instance
