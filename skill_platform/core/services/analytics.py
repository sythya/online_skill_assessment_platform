from django.db.models import Count, Q
from core.models import Attempt


def skill_wise_performance():
    return (
        Attempt.objects
        .all()
        .values('skill__name')
        .annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True))
        )
    )


def difficulty_wise_performance():
    return (
        Attempt.objects
        .all()
        .values('difficulty')
        .annotate(
            total=Count('id'),
            correct=Count('id', filter=Q(is_correct=True))
        )
    )