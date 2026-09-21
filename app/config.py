from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # LLM Configuration
    openai_api_key: str = ""
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.7

    # CTF Target Configuration
    ctf_target_host: str = "localhost"
    ctf_target_port: int = 8000
    allowed_networks: str = "127.0.0.1/8,localhost"

    # Agent Configuration
    max_agent_steps: int = 50
    command_timeout: int = 30
    tool_timeout: int = 60

    # Vector Database
    chroma_persist_directory: str = "./data/chroma"

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 5000
    api_reload: bool = True

    # Flag Patterns
    flag_patterns: str = "CTF\\{[^}]+\\},FLAG\\{[^}]+\\},flag\\{[^}]+\\}"

    # Docker Configuration
    docker_image_name: str = "ctf-demo-challenge"
    docker_container_name: str = "ctf-demo-challenge-container"

    class Config:
        env_file = ".env"
        case_sensitive = False

    @property
    def allowed_networks_list(self) -> List[str]:
        return [net.strip() for net in self.allowed_networks.split(",")]

    @property
    def flag_patterns_list(self) -> List[str]:
        return [pattern.strip() for pattern in self.flag_patterns.split(",")]


settings = Settings()
