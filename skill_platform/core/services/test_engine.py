from django.utils import timezone
from django.db import transaction

from core.models import Attempt, Result, TestQuestion
from core.services.blueprint_validator import (
    validate_blueprint,
    BlueprintValidationError
)


class TestEngineError(Exception):
    pass


# =========================================================
# 1️⃣ Automatic Question Generation (On Test Creation)
# =========================================================

def generate_test_questions(test):
    """
    Automatically generate questions when a Test is created.
    This function is production-safe:
    - Prevents duplicate generation
    - Validates blueprint
    - Uses transaction atomicity
    """

    # Prevent duplicate generation
    if getattr(test, "is_generated", False):
        return

    # Extra safety check
    if TestQuestion.objects.filter(test=test).exists():
        test.is_generated = True
        test.save(update_fields=["is_generated"])
        return

    blueprint = test.blueprint

    try:
        validate_blueprint(blueprint)
    except BlueprintValidationError as e:
        raise TestEngineError(str(e))

    with transaction.atomic():

        selected_questions = []

        for rule in blueprint.rules.all():

            questions = rule.skill.questions.filter(
                difficulty=rule.difficulty
            ).order_by("?")[:rule.number_of_questions]

            selected_questions.extend(questions)

        if not selected_questions:
            raise TestEngineError("No questions generated from blueprint.")

        for question in selected_questions:
            TestQuestion.objects.create(
                test=test,
                question=question
            )

        test.is_generated = True
        test.save(update_fields=["is_generated"])


# =========================================================
# 2️⃣ Submit Answer (Auto Evaluate)
# =========================================================

from core.models import Attempt, Answer


def submit_answer(user, test, question, selected_option):
    """
    Save candidate answer inside active test session
    """

    # 🔐 Security: Only test owner can answer
    if test.user != user:
        raise TestEngineError("Unauthorized access.")

    # 🔐 Test must be generated
    if not test.is_generated:
        raise TestEngineError("Test is not ready.")

    # 🔐 Cannot answer after completion
    if test.is_completed:
        raise TestEngineError("Test already completed.")

    # 🧠 Get active test session
    attempt = Attempt.objects.filter(
        user=user,
        test=test,
        is_completed=False
    ).first()

    if not attempt:
        raise TestEngineError("No active test session found.")

    # 🔐 Prevent duplicate answer for same question
    if Answer.objects.filter(attempt=attempt, question=question).exists():
        raise TestEngineError("Question already answered.")

    if not selected_option:
        is_correct = False
    else:
        is_correct = selected_option.lower() == question.correct_option.lower()

    # ✅ Store answer (NOT Attempt)
    answer = Answer.objects.create(
        attempt=attempt,
        question=question,
        selected_option=selected_option,
        is_correct=is_correct,
        skill=question.skill,
        difficulty=question.difficulty,
    )

    return answer

# =========================================================
# 3️⃣ Finalize Test (Calculate Result)
# =========================================================

def finalize_test(attempt):
    """
    Finalize test session and generate analytics
    """

    if attempt.is_completed:
        raise TestEngineError("Test already finalized.")

    answers = Answer.objects.filter(attempt=attempt)

    if not answers.exists():
        raise TestEngineError("No answers submitted.")

    total_questions = answers.count()
    correct_answers = answers.filter(is_correct=True).count()

    accuracy = round((correct_answers / total_questions) * 100, 2)

    # 📊 Skill-wise breakdown
    skill_data = {}
    for answer in answers:
        skill_name = answer.skill.name if answer.skill else "Unknown"

        if skill_name not in skill_data:
            skill_data[skill_name] = {"correct": 0, "total": 0}

        skill_data[skill_name]["total"] += 1
        if answer.is_correct:
            skill_data[skill_name]["correct"] += 1

    # 📊 Difficulty-wise breakdown
    difficulty_data = {}
    for answer in answers:
        level = answer.difficulty

        if level not in difficulty_data:
            difficulty_data[level] = {"correct": 0, "total": 0}

        difficulty_data[level]["total"] += 1
        if answer.is_correct:
            difficulty_data[level]["correct"] += 1

    result = Result.objects.create(
        user=attempt.user,
        test=attempt.test,
        attempt=attempt,
        score=correct_answers,
        total_questions=total_questions,
        accuracy=accuracy,
        skill_breakdown=skill_data,
        difficulty_breakdown=difficulty_data
    )

    attempt.is_completed = True
    attempt.completed_at = timezone.now()
    attempt.save(update_fields=["is_completed", "completed_at"])

    attempt.test.is_completed = True
    attempt.test.completed_at = timezone.now()
    attempt.test.save(update_fields=["is_completed", "completed_at"])

    return result