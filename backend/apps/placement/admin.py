from django.contrib import admin

from .models import Assessment, PlacementAttempt, Question


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "version", "is_published", "created_at")
    list_filter = ("is_published",)
    inlines = (QuestionInline,)


@admin.register(PlacementAttempt)
class PlacementAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "assessment", "score", "max_score", "estimated_level", "completed_at")
    list_filter = ("estimated_level", "scoring_version")
    readonly_fields = ("user", "assessment", "answers", "score", "max_score", "estimated_level", "scoring_version", "completed_at")
