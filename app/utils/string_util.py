import secrets


def generate_otp():
    otp = ''
    for _ in range(6):
        otp += str(secrets.randbelow(9))
    return otp


def decimal_2_places(total):
    return f"{total:.2f}"
