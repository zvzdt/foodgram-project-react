from rest_framework import serializers


def validate_amount(amount):
    if amount <= 0:
        raise serializers.ValidationError(
            'Минимаьное количество ингредиентов - 1')
    return amount
