import math
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


def _configured_micro_cost_rate(name):
    raw = os.environ.get(name, "").strip()
    if not raw:
        return None
    try:
        rate = int(raw)
    except ValueError:
        return None
    return rate if rate >= 0 else None


def estimate_writing_cost_microunits(input_tokens, output_tokens):
    """Estimate micro-units using explicitly configured per-million-token rates.

    A micro-unit is one millionth of the billing currency unit. No vendor price
    is assumed: both rates must be configured by the deployment operator.
    """
    input_rate = _configured_micro_cost_rate("GEMINI_INPUT_COST_MICROUNITS_PER_MILLION_TOKENS")
    output_rate = _configured_micro_cost_rate("GEMINI_OUTPUT_COST_MICROUNITS_PER_MILLION_TOKENS")
    if input_rate is None or output_rate is None:
        return None
    if type(input_tokens) is not int or input_tokens < 0:
        return None
    if type(output_tokens) is not int or output_tokens < 0:
        return None
    return math.ceil((input_tokens * input_rate + output_tokens * output_rate) / 1_000_000)


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


def finish_usage(record, provider, status, failure_category="", usage_metadata=None):
    usage_metadata = usage_metadata if isinstance(usage_metadata, dict) else {}
    input_tokens = usage_metadata.get("promptTokenCount")
    output_tokens = usage_metadata.get("candidatesTokenCount")
    record.provider = provider
    record.status = status
    record.failure_category = failure_category
    record.completed_at = timezone.now()
    if type(input_tokens) is int and input_tokens >= 0:
        record.input_tokens = input_tokens
    if type(output_tokens) is int and output_tokens >= 0:
        record.output_tokens = output_tokens
    if record.input_tokens is not None and record.output_tokens is not None:
        record.estimated_cost_microunits = estimate_writing_cost_microunits(
            record.input_tokens, record.output_tokens
        )
    # Persist only aggregate token counts; never store submitted text or provider payloads.
    record.metadata = {
        "total_tokens": usage_metadata["totalTokenCount"]
    } if type(usage_metadata.get("totalTokenCount")) is int and usage_metadata["totalTokenCount"] >= 0 else {}
    record.save(update_fields=(
        "provider", "status", "failure_category", "completed_at", "input_tokens",
        "output_tokens", "estimated_cost_microunits", "metadata",
    ))
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
    input_tokens = sum(records.exclude(input_tokens__isnull=True).values_list("input_tokens", flat=True))
    output_tokens = sum(records.exclude(output_tokens__isnull=True).values_list("output_tokens", flat=True))
    estimated_costs = list(records.exclude(estimated_cost_microunits__isnull=True).values_list("estimated_cost_microunits", flat=True))
    has_token_usage = records.filter(input_tokens__isnull=False, output_tokens__isnull=False).exists()
    if estimated_costs:
        cost_tracking = "estimated_from_configured_rates"
    elif has_token_usage:
        cost_tracking = "token_usage_available_rates_not_configured"
    else:
        cost_tracking = "no_provider_usage_available"
    return {
        "window": "rolling_24_hours",
        "limit": limit,
        "used": used,
        "remaining": max(0, limit - used),
        "input_characters": sum(records.values_list("input_characters", flat=True)),
        "input_tokens": input_tokens if has_token_usage else None,
        "output_tokens": output_tokens if has_token_usage else None,
        "estimated_cost_microunits": sum(estimated_costs) if estimated_costs else None,
        "succeeded": records.filter(status=AIUsageRecord.Status.SUCCEEDED).count(),
        "failed": records.filter(status=AIUsageRecord.Status.FAILED).count(),
        "reserved": records.filter(status=AIUsageRecord.Status.RESERVED).count(),
        "cost_tracking": cost_tracking,
    }
