from django.contrib import admin

from .models import VocabularyCard


@admin.register(VocabularyCard)
class VocabularyCardAdmin(admin.ModelAdmin):
    list_display = ("word", "user", "status", "due_at", "last_reviewed_at")
    list_filter = ("status",)
    search_fields = ("word", "user__username")
    readonly_fields = ("created_at", "updated_at", "last_reviewed_at")
