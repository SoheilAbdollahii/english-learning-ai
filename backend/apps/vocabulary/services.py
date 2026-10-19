from datetime import timedelta

from django.utils import timezone

from apps.progress.models import LearningActivity
from apps.progress.services import record_activity
from .models import VocabularyCard


def apply_review(card: VocabularyCard, quality: int) -> VocabularyCard:
    """Apply a deterministic SM-2-inspired schedule for a single review outcome.

    Quality is 0..5. Grades below 3 restart the learning interval. Successful
    grades grow intervals and update ease; scheduling is based on review outcome,
    never merely on displaying a card.
    """
    now = timezone.now()
    ease = float(card.ease_factor)
    if quality < 3:
        card.repetitions = 0
        card.interval_days = 1
        card.status = VocabularyCard.Status.LEARNING
    else:
        if card.repetitions == 0:
            card.interval_days = 1
        elif card.repetitions == 1:
            card.interval_days = 6
        else:
            card.interval_days = max(1, round(card.interval_days * ease))
        card.repetitions += 1
        card.status = (
            VocabularyCard.Status.MASTERED
            if card.repetitions >= 5 and card.interval_days >= 21
            else VocabularyCard.Status.REVIEW
        )
        quality_gap = 5 - quality
        ease = max(1.3, ease + 0.1 - quality_gap * (0.08 + quality_gap * 0.02))
        card.ease_factor = round(ease, 2)
    card.last_reviewed_at = now
    card.due_at = now + timedelta(days=card.interval_days)
    card.save(update_fields=(
        "repetitions", "interval_days", "ease_factor", "status",
        "last_reviewed_at", "due_at", "updated_at",
    ))
    record_activity(card.user, LearningActivity.Type.VOCABULARY, card.pk, {"quality": quality})
    return card
