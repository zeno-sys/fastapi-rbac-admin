from pathlib import Path
from pydantic import Field, MySQLDsn,PostgresDsn, computed_field
import yaml
import os
from typing import Dict, Any

def load_config() -> Dict[str, Any]:
    """加载并返回配置字典"""
    env = os.getenv("ENV", "dev")  # 默认用dev环境
    base_path = Path("config")
    # 加载基础配置
    with open(base_path / "base.yaml",encoding="utf-8") as f:
        config: dict = yaml.safe_load(f)

    # 加载环境特定配置并覆盖base
    with open(base_path / f"{env}.yaml",encoding="utf-8") as f:
        env_config: dict = yaml.safe_load(f)
        if env_config:
            config.update(env_config)
    return config



# 全局配置对象
CONFIG = load_config()

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 安全配置
    SECRET_KEY: str = Field(default="lLNiBWPGiEmCLLR9kRGidgLY7Ac1rpSWwfGzTJpTmCU", env="SECRET_KEY")
    REFRESH_SECRET_KEY: str = Field(default="lLNiBWPGiEmCLLR9kRGidgLY7Ac1rpSWwfGzTJpTmCU", env="REFRESH_SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")  # 访问令牌有效期
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")  # 刷新令牌有效期
    
    # 项目配置
    project_name: str = Field(
        default=CONFIG.get("project", {}).get("name"),
        env="PROJECT_NAME",
    )
    project_description: str = Field(
        default=CONFIG.get("project", {}).get("description"),
        env="PROJECT_DESCRIPTION"
    )
    project_version: str = Field(
        default=CONFIG.get("project", {}).get("version"),
        env="PROJECT_VERSION"
    )
    api_v1_str: str = Field(
        default=CONFIG.get("api", {}).get("v1_str"),
        env="API_V1_STR"
    )
    @computed_field
    @property
    def async_mysql_dsn(self) -> MySQLDsn:
        source: dict = CONFIG.get("database", {}).get("primary", {})
        schema=source.get("schema")
        username=source.get("user")
        password=source.get("password")
        host=source.get("host")
        port=source.get("port")
        database=source.get('database')
        return f"{schema}://{username}:{password}@{host}:{port}/{database}"
    
    class Config:  
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore" 

settings = Settings()

