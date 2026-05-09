"""Application settings and configuration."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "ontology-knowledge-base"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_timeout: int = 600
    api_workers: int = 4
    
    # PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "ontology_kb"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    
    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j"
    neo4j_database: str = "neo4j"
    
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # LLM APIs - Azure OpenAI
    azure_openai_api_key: str = "test_key"
    azure_openai_endpoint: str = "https://test.openai.azure.com"
    azure_openai_api_version: str = "2025-01-01-preview"
    azure_openai_deployment_name: str = "gpt-4.1"
    azure_openai_embedding_deployment: str = "text-embedding-ada-002"
    llm_provider: str = "azure_openai"
    
    # Security
    jwt_secret_key: str = "test_secret_key_change_in_production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7
    
    # Processing Configuration
    max_file_size_mb: int = 50
    chunk_size_words: int = 5000
    chunk_overlap_words: int = 500
    batch_size: int = 1000
    duplicate_threshold: float = 0.9
    semantic_similarity_threshold: float = 0.95
    
    # Retry Configuration
    max_retries: int = 3
    retry_initial_delay: int = 2
    retry_exponential_base: int = 2
    
    # Circuit Breaker
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_timeout_seconds: int = 60
    
    # Lock Configuration
    lock_timeout_minutes: int = 30
    
    # Audit
    audit_log_retention_days: int = 730
    
    @property
    def postgres_url(self) -> str:
        """Get PostgreSQL connection URL."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
