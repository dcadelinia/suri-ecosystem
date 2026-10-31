import os

class Settings:
    PORT: int = int(os.getenv("PORT", 8080))
    DATA_DIR: str = os.getenv("DATA_DIR", "/data")
    MANTAGU_LOG_LEVEL: str = os.getenv("MANTAGU_LOG_LEVEL", "PRODUCTION")
    
    # Stripe parameters
    STRIPE_SECRET_KEY: str = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock_placeholder")
    STRIPE_WEBHOOK_SECRET: str = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_mock_placeholder")

settings = Settings()
