from django.contrib import admin

from .models import LearningActivity


@admin.register(LearningActivity)
class LearningActivityAdmin(admin.ModelAdmin):
    list_display = ("user", "activity_type", "object_id", "created_at")
    list_filter = ("activity_type",)
    search_fields = ("user__username",)
    readonly_fields = ("user", "activity_type", "object_id", "metadata", "created_at")
