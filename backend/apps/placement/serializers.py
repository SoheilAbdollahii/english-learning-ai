from rest_framework import serializers

from .models import Assessment, PlacementAttempt, Question


class PublicQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ("id", "prompt", "options", "points", "order")


class AssessmentListSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(source="questions.count", read_only=True)

    class Meta:
        model = Assessment
        fields = ("id", "title", "version", "question_count")


class AssessmentDetailSerializer(AssessmentListSerializer):
    questions = PublicQuestionSerializer(many=True, read_only=True)

    class Meta(AssessmentListSerializer.Meta):
        fields = AssessmentListSerializer.Meta.fields + ("questions",)


class AttemptCreateSerializer(serializers.Serializer):
    assessment_id = serializers.IntegerField(min_value=1)
    answers = serializers.DictField(
        child=serializers.CharField(max_length=32, trim_whitespace=True),
        allow_empty=False,
    )

    def validate(self, attrs):
        assessment = Assessment.objects.filter(pk=attrs["assessment_id"], is_published=True).first()
        if assessment is None:
            raise serializers.ValidationError({"assessment_id": "Assessment not found or not published."})
        questions = list(assessment.questions.all())
        expected_ids = {str(question.pk) for question in questions}
        submitted_ids = set(attrs["answers"])
        if submitted_ids != expected_ids:
            raise serializers.ValidationError({"answers": "Submit exactly one answer for every question."})
        allowed = {str(question.pk): set(question.options.keys()) for question in questions}
        for question_id, answer in attrs["answers"].items():
            if answer not in allowed[question_id]:
                raise serializers.ValidationError({"answers": f"Invalid option for question {question_id}."})
        attrs["assessment"] = assessment
        attrs["questions"] = questions
        return attrs


class AttemptResultSerializer(serializers.ModelSerializer):
    assessment_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = PlacementAttempt
        fields = ("id", "assessment_id", "score", "max_score", "estimated_level", "scoring_version", "completed_at")
