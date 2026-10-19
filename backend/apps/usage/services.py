import os
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from .models import AIUsageRecord

User = get_user_model()


def writing_daily_limit():
    try:
        return max(1, min(int(os.environ.get("WRITING_SUBMISSIONS_PER_DAY", "30")), 1000))
    except ValueError:
        return 30


@transaction.atomic
def reserve_writing_usage(user, input_characters):
    """Reserve one rolling-24-hour slot before any provider work starts.

    Locking the user row serializes quota reservations on databases that support
    SELECT FOR UPDATE. The reserved record counts against quota even if the
    provider subsequently fails, preventing retries from bypassing cost controls.
    """
    User.objects.select_for_update().get(pk=user.pk)
    now = timezone.now()
    window_start = now - timedelta(hours=24)
    used = AIUsageRecord.objects.filter(
        user=user,
        operation="writing_analysis",
        created_at__gte=window_start,
        status__in=(AIUsageRecord.Status.RESERVED, AIUsageRecord.Status.SUCCEEDED, AIUsageRecord.Status.FAILED),
    ).count()
    limit = writing_daily_limit()
    if used >= limit:
        return None, limit, used
    record = AIUsageRecord.objects.create(
        user=user,
        operation="writing_analysis",
        provider="pending",
        status=AIUsageRecord.Status.RESERVED,
        input_characters=input_characters,
    )
    return record, limit, used + 1


def finish_usage(record, provider, status, failure_category=""):
    record.provider = provider
    record.status = status
    record.failure_category = failure_category
    record.completed_at = timezone.now()
    record.save(update_fields=("provider", "status", "failure_category", "completed_at"))
    return record


def get_usage_summary(user):
    now = timezone.now()
    window_start = now - timedelta(hours=24)
    records = AIUsageRecord.objects.filter(
        user=user,
        operation="writing_analysis",
        created_at__gte=window_start,
    )
    counted = records.filter(status__in=(AIUsageRecord.Status.RESERVED, AIUsageRecord.Status.SUCCEEDED, AIUsageRecord.Status.FAILED))
    used = counted.count()
    limit = writing_daily_limit()
    return {
        "window": "rolling_24_hours",
        "limit": limit,
        "used": used,
        "remaining": max(0, limit - used),
        "input_characters": sum(records.values_list("input_characters", flat=True)),
        "succeeded": records.filter(status=AIUsageRecord.Status.SUCCEEDED).count(),
        "failed": records.filter(status=AIUsageRecord.Status.FAILED).count(),
        "reserved": records.filter(status=AIUsageRecord.Status.RESERVED).count(),
        "cost_tracking": "unavailable_until_provider_usage_and_pricing_are_configured",
    }
