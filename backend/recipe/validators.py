from rest_framework.exceptions import ValidationError


def validate_color(value):
    if not value[0] == '#' or len(value) != 7:
        raise ValidationError("Invalid hex color")
    try:
        int(value[1:], 16)
    except ValueError:
        raise ValidationError("Invalid hex color")
