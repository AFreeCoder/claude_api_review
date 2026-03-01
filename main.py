#!/usr/bin/env python3
"""
Claude API 服务商评测工具 v2.0

使用方法:
    # 批量评测 (推荐)
    python main.py batch --config providers.yaml

    # 单服务商测试
    python main.py single --url https://api.example.com --key sk-xxx

    # 跳过耗费测试
    python main.py batch --config providers.yaml --skip-expensive
"""

import argparse
import sys

from verifier import APIClient, load_config, TestRunner, Reporter


# ---------------------------------------------------------------------------
# 控制台回调
# ---------------------------------------------------------------------------
STATUS_ICONS = {
    "start": "⏳",
    "pass": "✅",
    "fail": "❌",
    "skip": "⏭️",
    "error": "⚠️",
    "uncertain": "❓",
}


def console_callback(index: int, name: str, status: str, message: str):
    """测试进度的控制台输出回调"""
    icon = STATUS_ICONS.get(status, "")
    if status == "start":
        print(f"\n  [{index + 1:>2}] {name}")
        print(f"      {icon} 执行中...")
    else:
        print(f"      {icon} {message}")


# ---------------------------------------------------------------------------
# 单服务商模式
# ---------------------------------------------------------------------------
def run_single(args):
    """单服务商测试"""
    client = APIClient(args.url, args.key, args.model, timeout=args.timeout)
    runner = TestRunner(client, skip_expensive=args.skip_expensive)

    print(f"\n{'=' * 70}")
    print(f"  Claude API 真实性验证测试")
    print(f"{'=' * 70}")
    print(f"  测试目标: {args.url}")
    print(f"  使用模型: {args.model}")
    print(f"{'=' * 70}")

    result = runner.run_all(callback=console_callback)
    Reporter.print_provider_result(result, "单服务商测试")
    Reporter.save_results([("single", result)], args.output_dir)


# ---------------------------------------------------------------------------
# 批量评测模式
# ---------------------------------------------------------------------------
def run_batch(args):
    """批量评测 (从配置文件)"""
    providers = load_config(args.config)

    if not providers:
        print("错误: 配置文件中没有找到服务商配置")
        sys.exit(1)

    Reporter.print_header(len(providers), args.model)

    all_results = []

    for i, provider in enumerate(providers):
        Reporter.print_provider_start(i, len(providers), provider.name)

        client = APIClient(
            provider.url, provider.key, args.model, args.timeout
        )
        runner = TestRunner(client, skip_expensive=args.skip_expensive)
        result = runner.run_all(callback=console_callback)

        Reporter.print_provider_result(result, provider.name)
        all_results.append((provider.name, result))

    # 对比报告
    Reporter.print_comparison(all_results)
    Reporter.save_results(all_results, args.output_dir)

    print(f"\n  评测完成! 共测试 {len(providers)} 个服务商。")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Claude API 服务商评测工具 v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 批量评测多个服务商
  python main.py batch --config providers.yaml

  # 跳过耗费测试 (节省成本)
  python main.py batch --config providers.yaml --skip-expensive

  # 单服务商测试
  python main.py single --url https://api.anthropic.com --key sk-ant-xxx

  # 指定输出目录
  python main.py batch --config providers.yaml --output-dir my_results
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="运行模式")

    # 单服务商模式
    single_parser = subparsers.add_parser("single", help="单服务商测试")
    single_parser.add_argument("--url", required=True, help="API 基础 URL")
    single_parser.add_argument("--key", required=True, help="API 密钥")
    single_parser.add_argument(
        "--model", default="claude-opus-4-6", help="模型 ID (默认: claude-opus-4-6)"
    )
    single_parser.add_argument(
        "--timeout", type=int, default=120, help="请求超时秒数 (默认: 120)"
    )
    single_parser.add_argument(
        "--skip-expensive", action="store_true", help="跳过耗费测试"
    )
    single_parser.add_argument(
        "--output-dir", default="results", help="输出目录 (默认: results)"
    )

    # 批量评测模式
    batch_parser = subparsers.add_parser("batch", help="批量评测 (使用配置文件)")
    batch_parser.add_argument(
        "--config", default="providers.yaml", help="配置文件路径 (默认: providers.yaml)"
    )
    batch_parser.add_argument(
        "--model", default="claude-opus-4-6", help="模型 ID (默认: claude-opus-4-6)"
    )
    batch_parser.add_argument(
        "--timeout", type=int, default=120, help="请求超时秒数 (默认: 120)"
    )
    batch_parser.add_argument(
        "--skip-expensive", action="store_true", help="跳过耗费测试"
    )
    batch_parser.add_argument(
        "--output-dir", default="results", help="输出目录 (默认: results)"
    )

    args = parser.parse_args()

    if args.command == "single":
        run_single(args)
    elif args.command == "batch":
        run_batch(args)
    else:
        parser.print_help()
        print("\n请使用 'single' 或 'batch' 子命令。")


if __name__ == "__main__":
    main()
