"""Small runtime configuration loaded from the untracked project .env."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="STOCK_", env_file=".env", extra="ignore", env_ignore_empty=True
    )
    data_dir: str = "data"
    output_path: str = "output.md"
    watchlist_file: str = "data/watchlist.csv"
    knowledge_file: str = "knowledge/research.md"
    screener_india_csv: str | None = None
    alpha_vantage_api_key: str | None = None
    alpha_vantage_exchange_timezone: str = "America/New_York"
    research_llm: str = "gemini/gemini-3.1-flash-lite"
    research_llm_base_url: str | None = None
    research_verbose: bool = True
    offline: bool = False
