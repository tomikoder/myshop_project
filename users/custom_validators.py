from django.core.exceptions import ValidationError

def validate_sign(value):
    if not value[2] == '-':
        raise ValidationError("Wstaw znak - np 23-400")

def validate_length(value):
    if len(value) != 6:
        raise ValidationError("Kod pocztowy składa się z 6 znaków")

def validate_number(value):
    if value > 999999999:
        raise ValidationError("Podaj poprawny numer telefonu składający się z 9 cyfr")
    elif value <= 99999999:
        raise ValidationError("Podaj poprawny numer telefonu składający się z 9 cyfr")


