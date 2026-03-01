# Claude API 服务商评测工具 v2.0

批量评测第三方 Claude API 服务商的自动化工具。通过 10 个验证维度检测 API 真实性，支持 YAML 配置多服务商同时评测和对比。

## 功能特性

- **10 项自动化测试**，覆盖格式、功能、行为三个层面
- **YAML 配置文件**，一次配置多个服务商批量评测
- **对比报告**，多服务商结果并排对比
- **性能计时**，每项测试记录响应耗时
- **成本控制**，可跳过耗费测试

## 测试项与权重

| # | 测试项 | 权重 | 判别力 | 说明 |
|---|--------|------|--------|------|
| 1 | Extended Thinking | 25% | ★★★★★ | 验证 adaptive 模式 + signature 加密签名 |
| 2 | Prompt Caching | 15% | ★★★★ | 验证缓存创建和命中机制 |
| 3 | Tool Use ID 格式 | 12% | ★★★★ | 验证 `toolu_` 前缀 + 字符集 |
| 4 | 预填充拒绝 | 10% | ★★★★★ | Opus 4.6 独有：拒绝 assistant 预填充 |
| 5 | Streaming Refusals | 8% | ★★★★ | 流式传输中的 `stop_reason: "refusal"` |
| 6 | Message 响应结构 | 8% | ★★★ | `msg_` 前缀、stop_reason、usage 字段 |
| 7 | Token 计数端点 | 8% | ★★★ | `/v1/messages/count_tokens` 可用性和精度 |
| 8 | Vision 图像处理 | 6% | ★★★ | 发送图像并验证识别能力 |
| 9 | 长上下文 (200K) | 5% | ★★★ | 发送 ~200K tokens 并验证处理能力 |
| 10 | 模型信息一致性 | 3% | ★★ | 响应 model 字段与请求是否匹配 |

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 方式一：批量评测（推荐）

```bash
# 1. 复制配置文件并填入服务商信息
cp providers_example.yaml providers.yaml

# 2. 编辑 providers.yaml，填入各服务商的 URL 和 API Key

# 3. 运行批量评测
python main.py batch --config providers.yaml
```

### 方式二：单服务商测试

```bash
python main.py single --url https://api.anthropic.com --key sk-ant-xxx
```

### 节省成本模式

跳过 Prompt Caching 和 200K 长上下文测试：

```bash
python main.py batch --config providers.yaml --skip-expensive
```

## 配置文件格式

`providers.yaml` 示例：

```yaml
settings:
  default_model: claude-opus-4-6
  timeout: 120
  skip_expensive: false
  output_dir: results

providers:
  - name: "官方API"
    url: "https://api.anthropic.com"
    key: "sk-ant-your-key"

  - name: "中转站A"
    url: "https://api.example.com"
    key: "sk-your-key"

  - name: "OpenRouter"
    url: "https://openrouter.ai/api/v1"
    key: "sk-or-your-key"
    model: "anthropic/claude-opus-4-6"
```

## 评分标准

| 得分 | 判定 | 说明 |
|------|------|------|
| 90-100 | ✅ 真实的 Claude API | 通过所有或几乎所有关键测试 |
| 70-89 | ⚠️ 可能是真实的 | 通过大部分测试，建议进一步验证 |
| 50-69 | ❌ 可能是假冒 | 未通过多项关键测试 |
| 0-49 | 🚫 高度疑似假冒 | 几乎所有测试未通过 |

## 项目结构

```
claude_api_review/
├── main.py                  # 入口 (single / batch 两种模式)
├── providers_example.yaml   # 配置文件示例
├── requirements.txt         # 依赖
├── verifier/                # 核心包
│   ├── __init__.py
│   ├── client.py            # API 客户端 (含请求计时)
│   ├── config.py            # YAML 配置加载
│   ├── tests.py             # 10 个测试方法
│   ├── runner.py            # 测试调度器
│   └── reporter.py          # 报告生成 + 多服务商对比
└── results/                 # 测试结果输出目录
```

## 成本估算

| 测试模式 | 约消耗 tokens | 约成本 (Opus 4.6) |
|---------|--------------|-------------------|
| 完整测试 | ~220K | ~$1.10 |
| 跳过耗费测试 | ~5K | ~$0.03 |

> 长上下文测试 (200K tokens) 占据了绝大部分成本。使用 `--skip-expensive` 可大幅降低。

## 常见问题

**Q: 可以完全信任测试结果吗？**

不能 100% 保证。如果第三方完全代理官方 API（只是加价转发），工具无法区分。建议结合价格、服务商信誉等因素综合判断。

**Q: 核心测试是哪几个？**

Extended Thinking (25%) + Prompt Caching (15%) + Tool Use ID (12%) + 预填充拒绝 (10%) = 62%。这四项通过即有很高置信度。

**Q: 预填充拒绝测试只适用于 Opus 4.6 吗？**

是的。Opus 4.6 移除了 assistant 预填充功能，其他 Claude 模型仍支持。如果测试其他模型，此项会失败属正常。

## 局限性

1. 完全代理官方 API 的中转站无法区分
2. 网络问题可能导致误判
3. 200K 长上下文测试成本较高
4. API 规范可能随版本更新变化

## 许可

MIT License

## 免责声明

本工具仅用于教育和研究目的。使用时请遵守相关服务条款，注意保护 API 密钥安全。测试结果仅供参考。
