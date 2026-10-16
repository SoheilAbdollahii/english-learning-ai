from django.contrib import admin
from .models import Profile
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "locale", "target_level", "daily_goal_minutes", "updated_at")
    list_filter = ("locale", "target_level")
    search_fields = ("user__username", "user__email")
