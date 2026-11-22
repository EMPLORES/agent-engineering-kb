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

