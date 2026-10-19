from django.contrib import admin

from .models import Passage, ReadingAttempt, ReadingQuestion


class ReadingQuestionInline(admin.TabularInline):
    model = ReadingQuestion
    extra = 0


@admin.register(Passage)
class PassageAdmin(admin.ModelAdmin):
    list_display = ("title", "level", "content_version", "is_published")
    list_filter = ("level", "is_published")
    search_fields = ("title", "body", "slug")
    inlines = (ReadingQuestionInline,)


@admin.register(ReadingAttempt)
class ReadingAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "passage", "percentage", "completed_at")
    list_filter = ("passage__level",)
    readonly_fields = ("completed_at", "submitted_answers", "result_details")
