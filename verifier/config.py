"""配置加载 - 从 YAML 文件读取服务商列表"""

import yaml
from dataclasses import dataclass
from typing import List


@dataclass
class ProviderConfig:
    """单个服务商配置 (仅三个字段)"""
    name: str
    url: str
    key: str


def load_config(config_path: str) -> List[ProviderConfig]:
    """
    从 YAML 配置文件加载服务商列表

    配置文件格式:
        providers:
          - name: "官方API"
            url: "https://api.anthropic.com"
            key: "sk-ant-xxx"
    """
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    providers = []
    for p in data.get("providers", []):
        providers.append(
            ProviderConfig(
                name=p["name"],
                url=p["url"],
                key=p["key"],
            )
        )

    return providers
