"""测试调度器 - 按顺序运行所有测试并计算评分"""

from datetime import datetime
from typing import Callable, Optional

from .client import APIClient
from .tests import TEST_REGISTRY


class TestRunner:
    """测试运行器"""

    def __init__(self, client: APIClient, skip_expensive: bool = False):
        self.client = client
        self.skip_expensive = skip_expensive

    def run_all(
        self, callback: Optional[Callable] = None
    ) -> dict:
        """
        运行所有测试

        Args:
            callback: 进度回调 callback(index, name, status, message)
                      status: "start" | "pass" | "fail" | "skip" | "error" | "uncertain"

        Returns:
            完整的测试结果字典
        """
        results = []
        total_score = 0

        for i, test in enumerate(TEST_REGISTRY):
            name = test["name"]
            weight = test["weight"]

            # 跳过耗费测试
            if self.skip_expensive and test["expensive"]:
                results.append(
                    {
                        "test": name,
                        "passed": None,
                        "message": "跳过（节省成本）",
                        "weight": weight,
                        "data": None,
                        "perf": None,
                    }
                )
                if callback:
                    callback(i, name, "skip", "跳过（节省成本）")
                continue

            if callback:
                callback(i, name, "start", "执行中...")

            try:
                result = test["func"](self.client)

                if result.passed:
                    total_score += weight

                status = (
                    "pass"
                    if result.passed
                    else ("uncertain" if result.passed is None else "fail")
                )

                results.append(
                    {
                        "test": name,
                        "passed": result.passed,
                        "message": result.message,
                        "weight": weight,
                        "data": result.data,
                        "perf": result.perf,
                    }
                )

                if callback:
                    callback(i, name, status, result.message)

            except Exception as e:
                results.append(
                    {
                        "test": name,
                        "passed": False,
                        "message": f"异常: {str(e)}",
                        "weight": weight,
                        "data": None,
                        "perf": None,
                    }
                )
                if callback:
                    callback(i, name, "error", str(e))

        verdict, recommendation = self._get_verdict(total_score)

        return {
            "timestamp": datetime.now().isoformat(),
            "provider": {
                "url": self.client.base_url,
                "model": self.client.model,
            },
            "score": total_score,
            "max_score": 100,
            "verdict": verdict,
            "recommendation": recommendation,
            "tests": results,
        }

    @staticmethod
    def _get_verdict(score: int):
        if score >= 90:
            return (
                "✅ 真实的 Claude API",
                "该 API 很可能是官方正版 Claude API。",
            )
        elif score >= 70:
            return (
                "⚠️ 可能是真实的",
                "通过了大部分测试，建议进行更多验证。",
            )
        elif score >= 50:
            return (
                "❌ 可能是假冒",
                "未通过多项关键测试，可能使用了其他模型。",
            )
        else:
            return (
                "🚫 高度疑似假冒",
                "几乎所有测试未通过，极可能是假冒 API。",
            )
