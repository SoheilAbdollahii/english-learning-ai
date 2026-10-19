from django.db import migrations


def seed_passages(apps, schema_editor):
    Passage = apps.get_model("reading", "Passage")
    Question = apps.get_model("reading", "ReadingQuestion")
    db = schema_editor.connection.alias

    passages = [
        {
            "slug": "a-small-morning-change",
            "title": "A Small Morning Change",
            "body": "Mina wanted her mornings to feel less rushed. She began putting her bag beside the door each night and choosing her clothes before going to bed. At first, the change seemed too small to matter. After a week, however, Mina noticed that she left home on time and felt calmer on the bus. She did not add more tasks to her morning. Instead, she moved two simple decisions to the evening. Mina learned that a useful routine does not need to be complicated; it needs to fit real life.",
            "level": "A2",
            "questions": [
                ("What problem did Mina want to solve?", {"a": "She wanted to cook better meals.", "b": "Her mornings felt rushed.", "c": "She wanted a longer bus ride."}, "b", "The passage says Mina wanted her mornings to feel less rushed."),
                ("When did Mina prepare her bag and clothes?", {"a": "Each evening.", "b": "On the bus.", "c": "After arriving at work."}, "a", "She put her bag by the door and chose clothes before bed."),
                ("What is the main lesson of the passage?", {"a": "Every routine must be difficult.", "b": "People should wake up much earlier.", "c": "Small practical changes can help."}, "c", "Moving two small decisions to the evening helped Mina feel calmer."),
            ],
        },
        {
            "slug": "the-community-library",
            "title": "The Community Library",
            "body": "When the town library noticed that fewer teenagers were visiting, the staff asked local students what would make the space more useful. The students suggested a quiet study area, a monthly book exchange, and workshops on practical skills. Rather than changing everything at once, the library tested the ideas for six weeks. The study area was popular during exam season, while the book exchange attracted families as well as teenagers. The workshops had fewer visitors, so staff decided to ask students which topics they would actually attend. By testing ideas first, the library improved its services without spending its limited budget on activities nobody needed.",
            "level": "B1",
            "questions": [
                ("Why did the library ask teenagers for suggestions?", {"a": "Fewer teenagers were visiting.", "b": "The building was closing.", "c": "The library had too many staff."}, "a", "The passage begins by explaining that teenage visits had decreased."),
                ("How did the library manage the suggested changes?", {"a": "It introduced every idea permanently on day one.", "b": "It tested the ideas for six weeks.", "c": "It cancelled all workshops."}, "b", "The library ran a six-week trial before deciding what to improve."),
                ("What can be inferred about the library's approach?", {"a": "It ignored feedback when an idea was unpopular.", "b": "It spent its whole budget immediately.", "c": "It used feedback and trials to make decisions."}, "c", "It reviewed attendance and planned to ask students about workshop topics."),
            ],
        },
    ]

    for item in passages:
        passage, _ = Passage.objects.using(db).get_or_create(
            slug=item["slug"],
            content_version=1,
            defaults={
                "title": item["title"],
                "body": item["body"],
                "level": item["level"],
                "source_note": "Original Wordwise learning content",
                "is_published": True,
            },
        )
        for index, (prompt, options, correct, explanation) in enumerate(item["questions"], start=1):
            Question.objects.using(db).get_or_create(
                passage=passage,
                order=index,
                defaults={
                    "prompt": prompt,
                    "options": options,
                    "correct_option": correct,
                    "explanation": explanation,
                    "points": 1,
                },
            )


class Migration(migrations.Migration):
    dependencies = [("reading", "0001_initial")]

    operations = [migrations.RunPython(seed_passages, migrations.RunPython.noop)]
