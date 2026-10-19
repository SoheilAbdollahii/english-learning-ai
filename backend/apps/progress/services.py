from .models import LearningActivity


def record_activity(user, activity_type, object_id=None, metadata=None):
    """Persist a minimal learner activity event without storing submitted content."""
    return LearningActivity.objects.create(
        user=user,
        activity_type=activity_type,
        object_id=object_id,
        metadata=metadata or {},
    )
