from django.db import migrations, models


def populate_legacy_question_snapshots(apps, schema_editor):
    ReadingAttempt = apps.get_model("reading", "ReadingAttempt")
    for attempt in ReadingAttempt.objects.all().iterator():
        snapshots = []
        for index, detail in enumerate(attempt.result_details or [], start=1):
            snapshots.append({
                "question_id": detail.get("question_id"),
                "prompt": detail.get("prompt", ""),
                "options": {},
                "correct_option": detail.get("correct_option", ""),
                "explanation": detail.get("explanation", ""),
                "points": 0,
                "order": index,
                "selected_option": detail.get("selected_option", ""),
                "correct": bool(detail.get("correct", False)),
            })
        attempt.question_snapshots = snapshots
        attempt.save(update_fields=["question_snapshots"])


class Migration(migrations.Migration):
    dependencies = [
        ("reading", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="readingattempt",
            name="question_snapshots",
            field=models.JSONField(default=list),
        ),
        migrations.RunPython(populate_legacy_question_snapshots, migrations.RunPython.noop),
    ]
