from django.db.models import Count
from core.models import Question


class BlueprintValidationError(Exception):
    """Raised when blueprint configuration is invalid"""
    pass


def validate_blueprint(blueprint):
    """
    Strict validation:
    - Ensures enough active questions exist for each rule
    """

    errors = []

    for rule in blueprint.rules.all():
        available = Question.objects.filter(
            skill=rule.skill,
            difficulty=rule.difficulty,
            is_active=True
        ).count()

        if available < rule.number_of_questions:
            errors.append(
                f"{rule.skill.name} ({rule.difficulty.capitalize()}): "
                f"Required {rule.number_of_questions}, available {available}"
            )

    if errors:
        raise BlueprintValidationError(" | ".join(errors))