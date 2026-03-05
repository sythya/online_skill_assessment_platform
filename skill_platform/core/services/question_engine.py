from core.models import Question


def generate_questions_for_blueprint(blueprint):
    selected_questions = []

    for rule in blueprint.rules.all():
        qs = Question.objects.filter(
            skill=rule.skill,
            difficulty=rule.difficulty
        )[:rule.number_of_questions]

        if qs.count() < rule.number_of_questions:
            raise ValueError(
                f"Not enough questions for {rule.skill.name} ({rule.difficulty})"
            )

        selected_questions.extend(qs)

    return selected_questions