# Arbiter

Arbiter 是一个面向法规与合规领域的结构化审阅工作台。它将外部法规与内部制度的 Markdown/文本转换为可审阅的结构化草案（spec001），并通过前端工作台（spec003）支持专家审阅、编辑与导出。运行时 Agent 循环（spec002）处于规划阶段，尚未实现。

## 三大模块

| 模块 | 路径 | 状态 | 说明 |
|------|------|------|------|
| **001 Regulation Structuring** | `src/arbiter/structuring/` | **已实现** | Admin-only 离线结构化管道。将 Markdown/文本转换为 `StructuringPipelineOutput` 草案 bundle，包含文档元数据、条款树、语义草稿、引用候选、依赖图和验证报告。 |
| **002 Bounded Agent Runtime** | `specs/002-bounded-agent-runtime-loop/` | **规划中** | 运行时 Agent 循环与合规判断。当前未实现，不产生活跃 `RulePack`、正式 `RuleItem` 或最终 `JudgmentResult`。 |
| **003 Workbench UI** | `frontend/` | **MVP 已实现** | React 专家审阅工作台。支持 Markdown 导入、001 JSON 回放、语义字段编辑、审阅判定记录与整合审阅包导出。 |

## 核心设计原则

- **Admin / Runtime 分离**：spec001 只产草案（`review_status = needs_review`），不产运行时可直接消费的安全资产。
- **统一模型调用**：所有 LLM 辅助行为均通过 `LLMClient / ModelProvider` 协议路由；前端不直接调用模型提供商。
- **不可变基线输出**：前端审阅时，`base_output` 冻结不变；所有编辑以 `StructuringReviewPatch` / `StructuringReviewDecision` / `AssetCurationRecord` 形式存在，仅合并到 `merged_output`。
- **零真实模型调用测试**：测试仅使用 mock `ModelProvider`，无需 API key。

## 技术栈

**后端**
- Python 3.11+
- Pydantic（schema 与验证）
- pytest（单元与集成测试）

**前端**
- Vite + React 18 + TypeScript
- Zod（前端合约校验镜像）
- Vitest + Testing Library（单元/合约测试）
- Playwright（冒烟测试）

## 目录结构

```
.
├── specs/
│   ├── 001-regulation-structuring/      # 结构化管道规格、合约与任务
│   ├── 002-bounded-agent-runtime-loop/  # 运行时 Agent 规格（规划中）
│   └── 003-arbiter-workbench-ui/        # 前端工作台规格、合约与任务
├── src/arbiter/
│   ├── llm/                             # ModelProvider 协议与实现
│   ├── schemas/
│   │   └── regulation_structuring.py    # Pydantic 结构化合约
│   └── structuring/                     # 001 结构化管道
│       ├── intake.py                    # 输入校验与归一化
│       ├── extraction.py                # 确定性提取
│       ├── llm_extraction.py            # LLM 辅助提取包装器
│       ├── pipeline.py                  # 主编排：structure_regulation(...)
│       ├── validation.py                # 验证报告组装
│       ├── export.py                    # JSON 导出与敏感信息扫描
│       └── workbench_adapter.py         # Workbench 调用边界
├── tests/structuring/                   # 001 测试套件（131+ 测试）
└── frontend/
    ├── src/contracts/                   # Zod 合约镜像
    ├── src/adapters/                    # Admin 适配器客户端、运行时 Mock 适配器
    ├── src/workbench/                   # 审阅 UI 组件与会话状态
    └── tests/                           # 合约、Fixture、冒烟测试
```

## 快速开始

### 环境准备

项目已包含 Python 虚拟环境 `.venv` 与前端 `node_modules`。

```bash
# 后端依赖（如需重新安装）
./.venv/bin/python -m pip install -e .

# 前端依赖（如需重新安装）
cd frontend && npm install
```

### 运行测试

**001 结构化管道（全部）**
```bash
PYTHONPATH=src ./.venv/bin/python -m pytest tests/structuring -q
```

**001 Workbench 调用边界（单独）**
```bash
PYTHONPATH=src ./.venv/bin/python -m pytest tests/structuring/test_workbench_invocation_boundary.py -q
```

**前端合约与单元测试**
```bash
cd frontend && npm run test
```

**前端生产构建**
```bash
cd frontend && npm run build
```

### 本地启动工作台

```bash
# 终端 1：启动 001 Admin structuring adapter
PYTHONPATH=src ./.venv/bin/python -m arbiter.cli.server

# 终端 2：启动前端
cd frontend && npm run dev
```
前端默认端口 `5173`，本地 adapter 默认端口 `8000`。

如需真实 LLM 辅助解析，在启动 adapter 前配置 provider；否则前端勾选
“使用 LLM 辅助解析”会返回结构化失败，不会静默降级成本地解析。

```bash
export ARBITER_LLM_PROVIDER=deepseek
export DEEPSEEK_API_KEY=...
export DEEPSEEK_BASE_URL=https://api.deepseek.com
export ARBITER_LLM_MODEL=deepseek-chat
```

## LLM 国际化（i18n）

`OpenAICompatibleModelProvider` 支持通过 `locale` 参数将 JSON Schema 中的枚举值本地化为目标语言后再发送给 LLM。LLM 返回的本地化枚举值会在客户端 Pydantic 验证前自动映射回英文，因此内部数据流（Pydantic Schema、JSON API、前端 Zod 合约、数据库存储）**始终保持英文不变**。

### 启用中文输出

在启动 adapter 前设置环境变量：

```bash
export ARBITER_LLM_LOCALE=zh
```

当 `locale=zh` 时：
- System prompt 中注入的 JSON Schema 会将英文枚举值替换为中文（如 `"obligation"` → `"义务"`）
- LLM 输出的中文枚举值只会在 JSON Schema 声明的枚举字段路径上被映射回英文，再通过 Pydantic 验证
- 自由文本字段（`summary`、`definitions[]`、`evidence_text[]` 等）仍需配合 prompt 中的语言指令才能输出中文
- 自由文本即使完整等于某个枚举译文（如 `"未知"`、`"待审阅"`），也不会被当作枚举反译

### 维护枚举映射字典

翻译字典集中位于 `src/arbiter/llm/i18n_enums.py`。每个 Pydantic `Enum` 或 `Literal` 类型对应一个 `*_I18N` 字典，并统一注册在 `ENUM_REGISTRY` 列表中。

**添加新的枚举翻译：**

1. 在 `i18n_enums.py` 中新增一个字典（键为英文枚举值，值为本地化显示值）：
   ```python
   MY_NEW_ENUM_I18N: dict[str, str] = {
       "english_value": "中文值",
       # ...
   }
   ```
2. 将该字典追加到 `ENUM_REGISTRY` 列表末尾。
3. 运行测试确保无冲突：
   ```bash
   PYTHONPATH=src ./.venv/bin/python -m pytest tests/test_llm_i18n_enums.py -q
   ```

**冲突检查规则（模块加载和自动化测试共同守护）：**

| 规则 | 说明 |
|------|------|
| Key Set 唯一性 | 任意两个枚举的**英文 key 集合**不能完全相同，否则 schema 匹配时会混淆 |
| Value 映射唯一性 | 任意两个枚举的**中文 value** 不能映射到不同的英文 key，否则响应反向翻译时会误转 |

若发生冲突，请调整其中一个字典的中文翻译，重新运行测试直至通过。

## 关键合约

### `structure_regulation(input, model_provider=None) -> StructuringPipelineOutput`

001 核心操作。接受 `NormalizedTextInput`，返回包含以下内容的草案 bundle：

- `document` — `RegulationDocumentDraft`（含分类、时间元数据）
- `units` — `RegulationUnitDraft[]`（条款树，含 `parent_unit_id`、`order_index`、`display_label`）
- `reference_candidates` — `ReferenceCandidate[]`
- `dependency_graph` — `ResolvedDependencyGraphDraft`（含 `DependencyEdgeDraft[]`）
- `validation_report` — `StructuringValidationReport`
- `extraction_provenance` — 提取方法溯源（不含密钥、完整 prompt 或原始 provider payload）

### `run_structuring_from_markdown(request) -> StructuringRunResult`

001 拥有的 Workbench 调用边界。将 `StructuringRunRequest`（含 Markdown）转为 `NormalizedTextInput` 并委托给 `structure_regulation`。返回结构化状态：`succeeded`、`failed`、`validation_failed` 或 `cancelled`。

### 前端合约镜像

前端在 `frontend/src/contracts/structuringOutput.ts` 中维护与 001 对称的 Zod 校验，确保 `StructuringRunRequest`、`StructuringRunResult` 与 `StructuringPipelineOutput` 的跨语言一致性。

## 边界与限制

- **不实现**：PDF/DOCX 解析、OCR、数据库持久化、向量搜索、规则执行、资产晋升工作流。
- **不输出**：`JudgmentResult`、活跃 `RulePack`、正式 `RuleItem`、最终合规结论。
- **前端不直接调用模型**：所有模型使用均位于 001 `LLMClient / ModelProvider` 之后。
- **测试不使用真实模型**：mock `ModelProvider` 覆盖全部 LLM 辅助路径。

## 许可证

（待补充）
