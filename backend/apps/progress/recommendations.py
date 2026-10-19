from django.utils import timezone

from apps.reading.models import ReadingAttempt
from apps.vocabulary.models import VocabularyCard
from apps.writing.models import WritingSubmission
from .models import LearningActivity


def build_recommendations(user):
    """Return short, transparent actions based on persisted learner records."""
    now = timezone.now()
    due_words = VocabularyCard.objects.filter(user=user, due_at__lte=now).count()
    reading_count = ReadingAttempt.objects.filter(user=user).count()
    writing_count = WritingSubmission.objects.filter(user=user).count()
    sessions = LearningActivity.objects.filter(user=user).count()
    recommendations = []

    if due_words:
        recommendations.append({
            "code": "review_due_words",
            "title": "Review words that are due",
            "reason": f"You have {due_words} vocabulary card{'s' if due_words != 1 else ''} ready for review.",
            "href": "/vocabulary",
            "action_label": "Review vocabulary",
            "priority": 1,
        })
    if reading_count == 0:
        recommendations.append({
            "code": "start_reading",
            "title": "Try a short reading",
            "reason": "No reading attempts are saved yet, so one short passage is a useful next step.",
            "href": "/reading",
            "action_label": "Open Reading",
            "priority": 2,
        })
    if writing_count == 0:
        recommendations.append({
            "code": "start_writing",
            "title": "Write a few sentences",
            "reason": "A short writing submission will start your writing practice history.",
            "href": "/writing",
            "action_label": "Open Writing",
            "priority": 3,
        })
    if sessions == 0:
        recommendations.append({
            "code": "start_small",
            "title": "Start with one small session",
            "reason": "There is no recorded learning activity yet. Choose any short practice and build from there.",
            "href": "/",
            "action_label": "Choose a practice",
            "priority": 4,
        })

    if len(recommendations) < 3:
        # Prefer the least-used content area, using counts as evidence rather than a hidden model.
        candidates = [
            (reading_count, "practice_reading", "Keep reading regularly", "Reading practice helps check understanding.", "/reading", "Read a passage", 5),
            (writing_count, "practice_writing", "Keep writing regularly", "Short writing sessions create material to learn from.", "/writing", "Write a few sentences", 6),
        ]
        existing = {item["code"] for item in recommendations}
        for _, code, title, reason, href, action_label, priority in sorted(candidates):
            if code not in existing and len(recommendations) < 3:
                recommendations.append({
                    "code": code, "title": title, "reason": reason,
                    "href": href, "action_label": action_label, "priority": priority,
                })

    return sorted(recommendations, key=lambda item: item["priority"])[:3]
