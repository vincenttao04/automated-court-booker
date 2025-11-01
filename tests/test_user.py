import os


def test_user_env_variables_exist():
    required_env_variables = [
        "USER_NUMBER",
        "USER_PASSWORD",
        "LOGIN_URL",
        "LOGOUT_URL",
        "USER_DATA",
    ]

    for var in required_env_variables:
        value = os.getenv(var)
        assert value, f"Missing environment variable: {var}"
