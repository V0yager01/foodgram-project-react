from rest_framework.exceptions import ValidationError


def validate_me(value):
    if value == 'me':
        raise ValidationError("Unavailable username")
