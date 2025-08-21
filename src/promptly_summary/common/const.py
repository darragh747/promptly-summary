class Constant:
    BASE_URL: str = "https://promptly-backend-wwdj.onrender.com"
    SRC_URL: str = f"{BASE_URL}/prompt-history"
    TO_URL: str = f"{BASE_URL}/set-weekly-update"
    CLAUDE_MODEL: str = "claude-opus-4-1-20250805"
    MAX_TOK: int = 32_000
    TEMPERATURE: int = 1
    MIN_DAYS: int = 1
    MAX_DAYS: int = 50
