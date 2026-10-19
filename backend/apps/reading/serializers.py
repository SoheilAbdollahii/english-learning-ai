from rest_framework import serializers

from .models import Passage, ReadingAttempt, ReadingQuestion


class PublicReadingQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReadingQuestion
        fields = ("id", "prompt", "options", "points", "order")


class PassageListSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(source="questions.count", read_only=True)

    class Meta:
        model = Passage
        fields = ("id", "slug", "title", "level", "content_version", "question_count")


class PassageDetailSerializer(PassageListSerializer):
    questions = PublicReadingQuestionSerializer(many=True, read_only=True)

    class Meta(PassageListSerializer.Meta):
        fields = PassageListSerializer.Meta.fields + ("body", "source_note", "questions")


class ReadingAttemptCreateSerializer(serializers.Serializer):
    passage_id = serializers.IntegerField(min_value=1)
    answers = serializers.DictField(
        child=serializers.CharField(max_length=32, trim_whitespace=True),
        allow_empty=False,
    )

    def validate(self, attrs):
        passage = Passage.objects.filter(pk=attrs["passage_id"], is_published=True).first()
        if passage is None:
            raise serializers.ValidationError({"passage_id": "Passage not found or not published."})
        questions = list(passage.questions.all())
        expected_ids = {str(question.pk) for question in questions}
        if set(attrs["answers"]) != expected_ids:
            raise serializers.ValidationError({"answers": "Submit exactly one answer for every question."})
        allowed = {str(question.pk): set(question.options.keys()) for question in questions}
        for question_id, answer in attrs["answers"].items():
            if answer not in allowed[question_id]:
                raise serializers.ValidationError({"answers": f"Invalid option for question {question_id}."})
        attrs["passage"] = passage
        attrs["questions"] = questions
        return attrs


class ReadingAttemptSerializer(serializers.ModelSerializer):
    passage_title = serializers.CharField(source="passage.title", read_only=True)

    class Meta:
        model = ReadingAttempt
        fields = (
            "id", "passage", "passage_title", "passage_version",
            "submitted_answers", "result_details", "question_snapshots", "score", "max_score",
            "percentage", "completed_at",
        )
        read_only_fields = fields
