from django.core.management.base import BaseCommand
from core.models import Question, Skill, Topic
import csv
from pathlib import Path


class Command(BaseCommand):
    help = "Import questions from CSV file"

    def handle(self, *args, **options):
        file_path = Path("core/data/questions.csv")

        if not file_path.exists():
            self.stdout.write(self.style.ERROR("questions.csv not found"))
            return

        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                skill, _ = Skill.objects.get_or_create(name=row["skill"])
                topic, _ = Topic.objects.get_or_create(
                    name=row["topic"],
                    skill=skill
                )

                Question.objects.create(
                    skill=skill,
                    topic=topic,
                    difficulty=row["difficulty"],
                    question_text=row["question_text"],
                    option_a=row["option_a"],
                    option_b=row["option_b"],
                    option_c=row["option_c"],
                    option_d=row["option_d"],
                    correct_option=row["correct_option"].lower(),
                    question_type=row.get("question_type", "mcq"),
                    explanation=row.get("explanation", ""),
                    is_active=True
                )

        self.stdout.write(self.style.SUCCESS("Questions imported successfully"))