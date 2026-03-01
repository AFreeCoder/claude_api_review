"""API 客户端 - 封装 HTTP 请求和计时"""

import requests
import time
import uuid
import secrets
from typing import Optional, Dict, Tuple

# Claude Code 客户端完整指纹常量 (来源: apipool/backend/internal/pkg/claude/constants.go)
_CLAUDE_CODE_UA = "claude-cli/2.1.22 (external, cli)"
_CLAUDE_CODE_SYSTEM_PROMPT = "You are Claude Code, Anthropic's official CLI for Claude."
_CLAUDE_CODE_BETA = (
    "claude-code-20250219,oauth-2025-04-20,"
    "interleaved-thinking-2025-05-14,"
    "adaptive-thinking-2026-01-28"
)
_FAKE_USER_ID = (
    f"user_{secrets.token_hex(32)}"
    f"_account__session_{uuid.uuid4()}"
)


class APIClient:
    """Claude API 客户端"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str = "claude-opus-4-6",
        timeout: int = 60,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.headers = {
            "x-api-key": api_key,
            "authorization": f"Bearer {api_key}",
            "anthropic-version": "2023-06-01",
            "anthropic-beta": _CLAUDE_CODE_BETA,
            "content-type": "application/json",
            "user-agent": _CLAUDE_CODE_UA,
            "x-app": "cli",
            "x-stainless-lang": "js",
            "x-stainless-package-version": "0.70.0",
            "x-stainless-os": "Linux",
            "x-stainless-arch": "arm64",
            "x-stainless-runtime": "node",
            "x-stainless-runtime-version": "v24.13.0",
            "x-stainless-retry-count": "0",
            "x-stainless-timeout": "600",
            "anthropic-dangerous-direct-browser-access": "true",
        }

    @staticmethod
    def _inject_claude_code_identity(payload: Dict) -> Dict:
        """向 payload 注入 Claude Code 客户端标识（system prompt + metadata）"""
        payload = dict(payload)
        # 注入 system prompt
        if "system" not in payload:
            payload["system"] = [
                {
                    "type": "text",
                    "text": _CLAUDE_CODE_SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ]
        # 注入 metadata.user_id
        if "metadata" not in payload:
            payload["metadata"] = {"user_id": _FAKE_USER_ID}
        return payload

    def post(
        self, endpoint: str, payload: Dict, timeout: Optional[int] = None
    ) -> Tuple[Dict, float]:
        """
        发送 POST 请求

        Returns:
            (响应字典, 耗时秒数)
        """
        try:
            url = f"{self.base_url}{endpoint}"
            send_payload = self._inject_claude_code_identity(payload)
            start = time.monotonic()
            response = requests.post(
                url,
                headers=self.headers,
                json=send_payload,
                timeout=timeout or self.timeout,
            )
            elapsed = time.monotonic() - start

            try:
                return response.json(), elapsed
            except Exception:
                return {
                    "error": {
                        "type": "parse_error",
                        "message": f"HTTP {response.status_code}: {response.text[:200]}",
                    }
                }, elapsed
        except requests.exceptions.Timeout:
            return {"error": {"type": "timeout_error", "message": "请求超时"}}, 0
        except requests.exceptions.ConnectionError:
            return {"error": {"type": "connection_error", "message": "连接失败"}}, 0
        except Exception as e:
            return {"error": {"type": "unknown_error", "message": str(e)}}, 0

    def post_stream(
        self, endpoint: str, payload: Dict, timeout: Optional[int] = None
    ) -> requests.Response:
        """发送流式 POST 请求，返回原始 Response 对象"""
        url = f"{self.base_url}{endpoint}"
        send_payload = self._inject_claude_code_identity(payload)
        return requests.post(
            url,
            headers=self.headers,
            json=send_payload,
            stream=True,
            timeout=timeout or self.timeout,
        )
