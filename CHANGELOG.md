# 更新日志

## v2.0 - 2026-02-17（架构重构 + 多服务商批量评测）

### 架构重构

- 从单文件 `verifier.py` 重构为模块化 `verifier/` 包
- 新增 YAML 配置文件支持，可配置多个服务商批量评测
- 新增多服务商对比报告
- 每项测试自动记录响应耗时

### 新增测试

- **预填充拒绝** (10%) — Opus 4.6 独有：拒绝 assistant 预填充请求
- **Vision 图像处理** (6%) — 发送 PNG 图片验证图像识别能力
- **模型信息一致性** (3%) — 检查响应 model 字段与请求是否匹配

### 测试更新

- **Extended Thinking**: `budget_tokens` (已弃用) → `adaptive` 模式
- **Message 响应结构**: 缓存相关 usage 字段改为可选检查
- **长上下文**: 从 ~5K tokens 升级到 ~200K tokens
- **Tool Use ID**: 新增字符集验证

### 移除

- **Constitutional AI 测试** — 判别力过低（几乎所有 LLM 都会拒绝有害请求）

### 权重调整

| 测试项 | v1.1 | v2.0 |
|--------|------|------|
| Extended Thinking | 28% | 25% |
| Prompt Caching | 18% | 15% |
| Tool Use ID 格式 | 14% | 12% |
| 预填充拒绝 | — | 10% (新增) |
| Streaming Refusals | 10% | 8% |
| Message 响应结构 | 9% | 8% |
| Token 计数端点 | 9% | 8% |
| Vision 图像处理 | — | 6% (新增) |
| 长上下文 (200K) | 9% | 5% |
| 模型信息一致性 | — | 3% (新增) |
| Constitutional AI | 3% | 移除 |

### 其他变更

- 默认模型从 `claude-sonnet-4-5-20250929` 改为 `claude-opus-4-6`
- 清理冗余文件，项目从 21 个文件精简到 11 个
- `.gitignore` 新增 `providers.yaml` 和 `results/` 目录

---

## v1.1 - 2026-02-11（新增 Streaming Refusals 测试）

- 新增测试：Streaming Refusals 机制 (10% 权重)
- 调整全部测试权重

---

## v1.0 - 2026-02-11（初始版本）

- 7 个验证维度
- 命令行接口 + JSON 结果导出
- 节省成本模式
