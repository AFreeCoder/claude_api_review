"""报告生成 - 控制台输出、JSON 保存、多服务商对比"""

import json
import os
from datetime import datetime
from typing import List, Tuple


class Reporter:
    """报告生成器"""

    @staticmethod
    def print_header(provider_count: int, default_model: str):
        """打印批量测试的总标题"""
        print(f"\n{'#' * 70}")
        print(f"  Claude API 服务商批量评测 v2.0")
        print(f"  服务商数量: {provider_count}")
        print(f"  默认模型: {default_model}")
        print(f"  测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'#' * 70}")

    @staticmethod
    def print_provider_start(index: int, total: int, name: str):
        """打印单个服务商的开始标记"""
        print(f"\n{'>' * 70}")
        print(f"  [{index + 1}/{total}] 正在评测: {name}")
        print(f"{'>' * 70}")

    @staticmethod
    def print_provider_result(result: dict, provider_name: str):
        """打印单个服务商的测试结果"""
        print(f"\n{'=' * 70}")
        print(f"  服务商: {provider_name}")
        print(f"  API 地址: {result['provider']['url']}")
        print(f"  测试模型: {result['provider']['model']}")
        print(f"  测试时间: {result['timestamp']}")
        print(f"{'=' * 70}")

        for i, test in enumerate(result["tests"]):
            weight = test["weight"]
            passed = test["passed"]

            if passed is None and "跳过" in test.get("message", ""):
                status = "⏭️ 跳过"
            elif passed is True:
                status = "✅ 通过"
            elif passed is False:
                status = "❌ 失败"
            else:
                status = "⚠️ 不确定"

            print(f"\n  [{i + 1:>2}] {test['test']} (权重: {weight}%)")
            print(f"      {status}")
            print(f"      {test['message']}")

            # 性能数据
            if test.get("perf"):
                perf_items = []
                for k, v in test["perf"].items():
                    if v is not None:
                        if isinstance(v, float):
                            perf_items.append(f"{k}: {v:.2f}s")
                        else:
                            perf_items.append(f"{k}: {v}")
                if perf_items:
                    print(f"      性能: {', '.join(perf_items)}")

        # 汇总
        print(f"\n{'=' * 70}")
        print(f"  得分: {result['score']}/{result['max_score']}")
        print(f"  结论: {result['verdict']}")
        print(f"  建议: {result['recommendation']}")
        print(f"{'=' * 70}")

        # 失败项列表
        failed = [r for r in result["tests"] if r["passed"] is False]
        if failed:
            print(f"\n  失败的测试项:")
            for t in failed:
                print(f"    - {t['test']}: {t['message']}")
            print(f"{'=' * 70}")

    @staticmethod
    def print_comparison(all_results: List[Tuple[str, dict]]):
        """打印多服务商对比表"""
        if len(all_results) < 2:
            return

        print(f"\n{'=' * 70}")
        print("  多服务商对比报告")
        print(f"{'=' * 70}")

        # 计算列宽
        max_name_len = max(len(name) for name, _ in all_results)
        col_width = max(max_name_len + 2, 12)

        # 表头
        header = f"  {'测试项':<20}"
        for name, _ in all_results:
            header += f"  {name:<{col_width}}"
        print(header)
        print("  " + "-" * (20 + (col_width + 2) * len(all_results)))

        # 测试项行
        test_names = [t["test"] for t in all_results[0][1]["tests"]]
        for test_name in test_names:
            row = f"  {test_name:<20}"
            for _, result in all_results:
                test = next(
                    (t for t in result["tests"] if t["test"] == test_name), None
                )
                if test:
                    if test["passed"] is None and "跳过" in test.get("message", ""):
                        cell = "⏭️ 跳过"
                    elif test["passed"] is True:
                        cell = "✅ 通过"
                    elif test["passed"] is False:
                        cell = "❌ 失败"
                    else:
                        cell = "⚠️ 不确定"
                else:
                    cell = "-"
                row += f"  {cell:<{col_width}}"
            print(row)

        # 分隔线
        print("  " + "-" * (20 + (col_width + 2) * len(all_results)))

        # 总分行
        score_row = f"  {'总分':<20}"
        for _, result in all_results:
            score = f"{result['score']}/{result['max_score']}"
            score_row += f"  {score:<{col_width}}"
        print(score_row)

        # 结论行
        verdict_row = f"  {'结论':<20}"
        for _, result in all_results:
            v = result["verdict"]
            verdict_row += f"  {v:<{col_width}}"
        print(verdict_row)

        print(f"{'=' * 70}")

    @staticmethod
    def save_results(
        all_results: List[Tuple[str, dict]], output_dir: str = "results"
    ):
        """保存测试结果到 JSON 文件"""
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 保存各服务商结果
        for name, result in all_results:
            safe_name = "".join(
                c if c.isalnum() or c in "-_" else "_" for c in name
            )
            filepath = os.path.join(output_dir, f"{safe_name}_{timestamp}.json")

            # 移除原始响应数据以减小文件体积
            clean_result = _clean_result_for_save(result)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(clean_result, f, ensure_ascii=False, indent=2)
            print(f"  结果已保存: {filepath}")

        # 多服务商对比
        if len(all_results) > 1:
            comparison = {
                "timestamp": datetime.now().isoformat(),
                "summary": [
                    {
                        "name": name,
                        "score": result["score"],
                        "max_score": result["max_score"],
                        "verdict": result["verdict"],
                    }
                    for name, result in all_results
                ],
            }
            filepath = os.path.join(output_dir, f"comparison_{timestamp}.json")
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(comparison, f, ensure_ascii=False, indent=2)
            print(f"  对比报告: {filepath}")


def _clean_result_for_save(result: dict) -> dict:
    """清理结果数据, 移除过大的原始响应以减小文件体积"""
    clean = {**result}
    clean_tests = []
    for test in result.get("tests", []):
        clean_test = {
            "test": test["test"],
            "passed": test["passed"],
            "message": test["message"],
            "weight": test["weight"],
            "perf": test.get("perf"),
        }
        clean_tests.append(clean_test)
    clean["tests"] = clean_tests
    return clean
