import os

SECRET_KEY = os.getenv("AQUALOG_SECRET_KEY", "aqualog-dev-secret-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60