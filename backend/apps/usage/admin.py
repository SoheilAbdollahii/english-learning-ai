from django.contrib import admin

from .models import AIUsageRecord


@admin.register(AIUsageRecord)
class AIUsageRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "operation", "provider", "status", "input_characters", "created_at")
    list_filter = ("operation", "provider", "status")
    search_fields = ("user__username",)
    readonly_fields = (
        "user", "operation", "provider", "status", "input_characters",
        "input_tokens", "output_tokens", "estimated_cost_microunits",
        "failure_category", "metadata", "created_at", "completed_at",
    )
