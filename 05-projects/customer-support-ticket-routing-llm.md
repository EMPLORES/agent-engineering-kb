# Experiment35：LLM 驱动的工单理解与分类（DeepSeek Integration）

## 1. 实验目标与升级背景

Experiment34 原本采用的是 `if/elif` 的方式，通过关键词判断来进行工单分类。

原有关键词规则过于死板，只能根据我们预定义的几个关键词进行判断，更无法解决一些特殊情况。例如，对于一些描述较为模糊的工单，无法解决，只能直接进入 `Manual Triage` 阶段。

Experiment35 选择引入 DeepSeek，是为了实现真正意义上的智能 LLM 驱动工单理解和分类。

本次升级希望实现通过 LLM 对工单进行智能理解、思考和判断。

## 2. DeepSeek API 接入

记录本次实际使用的技术配置：

- **模型：** `deepseek-v4.1-flash`
- **API 接口：** OpenAI SDK 兼容的 Chat Completions
- **配置方式：** 通过 `.env` 加载环境变量
- **API 调用方式：** `client.chat.completions.create()`
- **结构化输出：** `response_format={"type": "json_object"}`

> 注意：不要记录真实 API Key。

## 3. LLM 结构化分类

说明模型需要返回的四个字段：

| 字段 | 含义 |
|---|---|
| `category` | 最终分类 |
| `matched_categories` | 匹配到的业务类别 |
| `confidence` | 分类信心等级 |
| `reason` | 分类理由 |

重点解释五种分类结果：

- **Account：** 通过 LLM 进行工单理解判断，认为是账号类问题。
- **Technical：** 通过 LLM 进行工单理解判断，认为是技术类问题。
- **Order：** 通过 LLM 进行工单理解判断，认为是订单类问题。
- **Unknown：** 通过 LLM 进行工单理解判断，给出无法理解或 `confidence` 较低的结果，进而进入 `Manual Triage`。
- **Multiple：** 通过 LLM 进行工单理解判断，认为涉及到多种工单类别。

## 4. Python 结果校验与安全控制

结合实际代码说明：

- **JSON 解析：** 要求模型返回 JSON 格式，将返回的 JSON 文本解析成 Python 字典，方便程序读取和校验。
- **必需字段检查：** JSON 的格式合法正确，但不意味着内容正确，需要检查必须字段来确认。
- **类别合法性检查：** 检查模型返回的 `category` 是否属于程序预先定义的五种类别：`Account`、`Technical`、`Order`、`Unknown`、`Multiple`。
- **置信度合法性检查：** 检查模型返回的 `confidence` 是否属于程序预先允许的三个等级：`High`、`Medium`、`Low`。
- **分类结果之间的一致性检查：** 检查模型返回的不同字段之间是否存在逻辑矛盾。
- **Medium / Low 置信度降级为 Unknown：** 具体分为两种情况：
  1. 模型直接判断无法明确分类，返回 `Unknown`。
  2. 模型虽然识别出某个类别，但置信度为 `Medium` 或 `Low`，程序将 `category` 降级为 `Unknown`。
- **API 调用或结果校验失败时的异常回退：** API 调用失败或结果校验失败时，Python 通过异常捕获机制处理错误，将工单类别设置为 `Unknown`，同时保存异常类型和统一的人工处理说明。随后 LangGraph 按照原有条件路由机制，将工单交给 `Manual Triage`，保证单个节点的异常不会直接中断整个工作流。

### 核心设计

**LLM 负责理解和判断，Python 程序负责校验和控制自动路由。**

## 5. LangGraph 工作流升级

本次具体改动：

- 原有 `classify_ticket()` 从关键词判断升级为 DeepSeek API 调用。
- 新增 State 字段：
  - `confidence`
  - `classification_reason`
  - `classification_error`
- 保留原有 `assess_priority()`、条件路由和处理队列节点。
- `Unknown`、`Multiple` 继续进入人工分流。

### 升级后的执行流程

```text
START
  ↓
validate_ticket
  ↓
classify_ticket（DeepSeek）
  ↓
assess_priority
  ↓
route_category
  ├── Account → Account Support
  ├── Technical → Technical Support
  ├── Order → Order Support
  └── Unknown / Multiple → Manual Triage
  ↓
finalize_ticket
  ↓
END
```

## 6. 实验测试与结果

记录六组实际测试：

| 测试 | 输入类型 | 实际结果 |
|---|---|---|
| T001 | 账号问题 | Account |
| T002 | 严重技术故障 | Technical |
| T003 | 订单问题 | Order |
| T004 | 空工单 | Invalid |
| T005 | 企业合作咨询 | Unknown |
| T006 | 账号与订单问题 | Multiple |

**六组测试均通过。**

> 注意：目前没有直接打印 `confidence` 和 `classification_reason`，因此不能声称六组测试已经验证了置信度门控的具体触发情况。

## 7. Experiment34 与 Experiment35 对比

| 维度 | Experiment34 | Experiment35 |
|---|---|---|
| 分类依据 | 预定义关键词 | LLM 语义理解 |
| 分类规则 | 程序员编写 | 模型根据提示词判断 |
| 不确定情况 | Unknown / Multiple | Unknown / Multiple + 置信度控制 |
| 外部依赖 | 无模型 API | DeepSeek API |

## 8. 当前实验的局限与后续方向

- LLM 分类存在非确定性。
- API 调用会增加延迟和成本。
- 当前还没有专门验证 API 故障回退。
- 当前没有直接输出模型置信度和分类理由。
- 当前仍然是单个 LLM 分类节点，并非 Multi-Agent 系统。

## 9. Day27 · LLM 分类可靠性与可观测性

### 9.1 分类结果可观测性

记录新增的分类信息字段：

- `category`
- `matched_categories`
- `confidence`
- `classification_reason`
- `classification_error`

无效工单未执行 LLM 分类，实际执行路径为：

```text
validate_ticket → invalid_ticket → finalize_ticket
```

有效工单执行分类后，如果最终类别为 Unknown，则进入人工分流，实际执行路径为：

```text
validate_ticket → classify_ticket → assess_priority → manual_triage → finalize_ticket
```

两者代表不同的业务情况：

- 无效工单：未通过工单验证，因此没有执行 LLM 分类。
- Unknown 工单：通过了工单验证，也执行了 LLM 分类，但无法归入现有业务类别，或者因置信度不足被门控降级，因此需要人工分流。

未执行分类的字段显示空白会导致整体的运行情况是“模糊的”，而程序需要“明确的”。

### 9.2 置信度门控与路由验证

记录 `apply_confidence_gate()` 的设计：

| 原始类别 | 置信度 | 最终类别 |
|---|---|---|
| Account / Technical / Order | High | 保留原类别 |
| Account / Technical / Order | Medium / Low | Unknown |
| Unknown / Multiple | 任意合法等级 | 保留原类别 |

- `category`：模型给出的分类结论，经过置信度门控后，成为系统最终使用的分类结果。
- `matched_categories`：模型识别出的具体业务类别列表，保留原始匹配结果，即使 category 被降级为 Unknown，也不会丢失这些信息。

**单元测试：** 是为了验证置信度门控能否按照设计影响真实分类判断的结果。

**集成测试：** 是为了验证置信度门控逻辑接入 LangGraph 后能否真正影响到工作流执行路径。

Mock 模型 API 响应的目的是人为控制模型返回的数据，使测试结果可重复。

测试中只模拟 OpenAI 客户端的 API 响应，保留真实的 `classify_ticket()`、JSON 解析、字段校验、业务规则校验、置信度门控和 State 更新逻辑，同时保留真实的 LangGraph 图执行。

因此，我们能够在不调用真实 LLM 的情况下，验证分类节点与 LangGraph 工作流的衔接，而不是测试模型本身的智能判断能力。

### 9.3 异常处理与安全恢复

记录三种模拟故障：

| 故障 | 异常类型 |
|---|---|
| API 调用异常 | `ConnectionError` |
| 非法 JSON | `JSONDecodeError` |
| 业务校验失败 | `ValueError` |

`classify_ticket()` 通过 `try/except` 捕获异常，将异常转换为包含 Unknown、Low、`classification_error` 等信息的 State 更新并正常返回。

对于 LangGraph 来说，节点调用已经正常返回了 State 更新。只要没有继续向外抛出未处理的异常，工作流就可以按照原有的边和条件路由继续执行。

随后，`route_category()` 根据 `category = Unknown` 将工单送入 `manual_triage`，最终完成工单结果汇总。

### 9.4 实验结果与当前边界

必须保留真实测试证据：

| 验证项目 | 结果 |
|---|---:|
| 置信度门控单元测试 | 15/15 |
| LangGraph 路由集成测试 | 5/5 |
| 异常恢复集成测试 | 3/3 |
| 真实 DeepSeek 工单测试 | 6/6 |

共完成 23 组自动化测试，全部通过；另外运行了 6 组真实 DeepSeek 工单案例，均正常完成。

当前能力边界记录三点即可：

- Mock 测试不能证明 LLM 本身的分类准确率。
- 当前没有实现自动重试机制。
- 尚未建立完整的生产级 Tracing、Monitoring 和 Evaluation 体系。