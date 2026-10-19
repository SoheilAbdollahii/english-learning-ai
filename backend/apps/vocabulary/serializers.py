from django.utils import timezone
from rest_framework import serializers

from .models import VocabularyCard


class VocabularyCardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VocabularyCard
        fields = ("id", "word", "definition", "example_sentence", "translation")
        read_only_fields = ("id",)

    def validate_word(self, value):
        normalized = value.strip()
        if not normalized:
            raise serializers.ValidationError("Enter a word to study.")
        user = self.context["request"].user
        duplicates = VocabularyCard.objects.filter(user=user, word__iexact=normalized)
        if self.instance:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise serializers.ValidationError("This word is already in your vocabulary.")
        return normalized

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["due_at"] = timezone.now()
        return super().create(validated_data)


class VocabularyCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = VocabularyCard
        fields = (
            "id", "word", "definition", "example_sentence", "translation",
            "status", "repetitions", "interval_days", "ease_factor", "due_at",
            "last_reviewed_at", "created_at", "updated_at",
        )
        read_only_fields = fields


class VocabularyReviewSerializer(serializers.Serializer):
    quality = serializers.IntegerField(min_value=0, max_value=5)


class VocabularyReviewEventSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import VocabularyReviewEvent

        model = VocabularyReviewEvent
        fields = (
            "id", "card", "word_snapshot", "quality",
            "repetitions_before", "repetitions_after",
            "interval_days_before", "interval_days_after",
            "ease_factor_before", "ease_factor_after",
            "status_before", "status_after", "reviewed_at",
        )
        read_only_fields = fields
