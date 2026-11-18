# Customer Support Ticket Routing（企业客服工单分流系统）项目文档

## 1. 项目概述（Project Overview）

- **项目名称**：Customer Support Ticket Routing（企业客服工单分流系统）
- **技术框架**：Python + LangGraph
- **当前版本定位**：基于确定性业务规则的第一版工作流，不是完整的 AI 客服系统。
- **核心任务**：接收工单 → 验证内容 → 识别类别 → 判断优先级 → 分配处理队列 → 生成最终结果。

当前版本实现了一个完整的基础工单分流流程，重点验证 LangGraph 节点如何读取和更新 State，以及条件边如何根据当前状态决定下一步执行路径。

---

## 2. 项目要解决的问题（Problem Statement）

企业每天会收到大量不同类型的客服工单，例如账户问题、技术问题和订单问题。如果全部依靠人工识别和分配，会增加客服人员的工作负担，降低处理效率。因此，需要一个自动化工单分流系统，根据工单内容识别问题类别，并将工单分配到对应的处理队列。

系统需要处理以下三类特殊情况：

1. **用户问题为空**：系统应识别并将其标记为无效工单（`invalid`），同时记录验证失败原因，避免无效数据继续进入后续分类和分流流程。
2. **无法识别类别**：归类为 `Unknown`，并转交 Manual Triage 进行人工分流，避免系统在缺乏足够信息的情况下进行错误分配。
3. **同时涉及多个类别**：系统不应直接选择其中一个类别，而应保留所有匹配结果，并转交 Manual Triage。对于涉及多个业务领域的复合型工单，需要进一步分析后才能确定合适的处理方式。

---

## 3. 系统功能与业务规则（Features & Business Rules）

### 3.1 当前已实现的功能

| 功能 | 当前实现 |
| --- | --- |
| 工单验证 | 检查用户问题是否为空 |
| 工单分类 | Account、Technical、Order |
| 未知类别 | 进入人工分流 |
| 多类别匹配 | 进入人工分流，保留匹配类别 |
| 优先级判断 | 根据预定义规则判断 |
| 队列分配 | 分配对应业务支持队列 |
| 无效工单处理 | 标记为 `invalid` |
| 结果汇总 | 统一生成最终工单结果 |

> **重点说明**：当前版本的分类、优先级判断和队列分配均由 Python 预定义业务规则完成，**没有使用 LLM**。因此，该系统目前属于基于确定性规则的工作流，而不是具备自然语言理解能力的 AI 客服系统。

---

## 4. 系统架构与工作流设计（Architecture & Workflow）

### 4.1 当前节点

| 节点 | 说明 |
| --- | --- |
| `validate_ticket` | 验证工单内容 |
| `invalid_ticket` | 标记无效工单并记录执行信息 |
| `classify_ticket` | 识别工单类别 |
| `assess_priority` | 判断优先级 |
| `assign_account_queue` | 分配至账户支持队列 |
| `assign_technical_queue` | 分配至技术支持队列 |
| `assign_order_queue` | 分配至订单支持队列 |
| `manual_triage` | 人工分流 |
| `finalize_ticket` | 统一生成最终结果 |

### 4.2 执行路径

系统根据工单验证结果和分类结果形成不同的执行路径：

- **有效工单**：进入分类和优先级判断阶段，再根据分类结果进入对应业务队列。
- **未知类别 / 多类别工单**：进入 `manual_triage`。
- **无效工单**：通过条件边进入 `invalid_ticket` 节点，由该节点标记工单状态并记录执行信息，跳过分类和优先级判断，随后进入 `finalize_ticket` 统一生成最终结果。

### 4.3 State 设计

- **State** 用于保存当前工单处理过程中的数据和状态，是不同节点之间共享和传递任务信息的载体。
- **`TicketState`** 规定了 State 中有哪些字段，以及字段的数据类型。
- 初始 State 由 `invoke()` 调用时传入。
- State 保存工单信息、处理状态、分类结果、分配结果和执行记录。
- 节点通过返回字典提交需要更新的 State 字段，LangGraph 会根据 State 的更新机制将这些局部更新合并到当前共享状态中，不需要每个节点都重新返回全部字段。

关键字段说明：

| 字段 | 作用 |
| --- | --- |
| `category` | 记录最终分类结果，例如 `Account`、`Technical`、`Order`、`Unknown` 或 `Multiple` |
| `matched_categories` | 保存实际匹配到的所有类别。当一张工单同时涉及多个类别时，仅通过 `category="Multiple"` 无法知道具体匹配了哪些类别，因此需要用它保留详细信息 |
| `processing_steps` | 记录工单实际经过的节点，帮助开发者观察和验证不同工单的执行路径 |

---

## 5. 异常处理与设计决策（Error Handling & Design Decisions）

记录三个实际遇到的问题：

### 问题一：多类别匹配

- **现象**：最初使用 `if/elif`，只会保留第一个匹配类别。
- **解决**：改为独立判断，收集所有匹配类别；多类别工单进入 `manual_triage`。

### 问题二：无效工单缺少 State 字段

- **现象**：无效工单没有经过分类节点，`finalize_ticket()` 直接读取 `matched_categories` 会产生 `KeyError`。
- **解决**：使用 `state.get("matched_categories", [])` 提供默认值。

### 问题三：无效工单绕过统一结果汇总

- **现象**：最初 `invalid_ticket` 直接连接 `END`。
- **解决**：改为连接 `finalize_ticket`，让不同处理路径统一生成最终结果。

> **设计结论**：通过将不同业务分支连接到 `finalize_ticket`，系统实现了统一的结果汇总机制。无论工单最终进入业务队列、人工分流还是验证失败路径，都可以由同一个节点生成标准化的最终结果。

---

## 6. 测试与验证（Testing & Validation）

实际运行的六组测试：

| 测试 | 场景 | 实际结果 | 执行路径 |
| --- | --- | --- | --- |
| T001 | 账号问题 | Account Support / Normal / `routed` | validate → classify → priority → account queue → finalize |
| T002 | 严重技术故障 | Technical Support / High / `routed` | validate → classify → priority → technical queue → finalize |
| T003 | 订单问题 | Order Support / Normal / `routed` | validate → classify → priority → order queue → finalize |
| T004 | 空工单内容 | `invalid` | validate → invalid_ticket → finalize |
| T005 | 未知类别 | Manual Triage / `needs_manual_triage` | validate → classify → priority → manual_triage → finalize |
| T006 | 账号与订单同时匹配 | Manual Triage / `needs_manual_triage`，保留 Account、Order | validate → classify → priority → manual_triage → finalize |

**测试结论**：六组测试均已在本地实际运行通过，验证了正常分流、无效工单处理、未知类别人工分流、多类别匹配以及统一结果汇总等功能。

---

## 7. 当前版本局限与未来扩展（Limitations & Future Development）

### 7.1 当前版本局限

- 使用预定义 Python 规则进行分类。
- 没有接入 LLM。
- 没有 Tool Calling。
- 尚未引入 LangGraph Checkpoint 与 Persistence 机制。
- 没有数据库和 Web API。
- 目前是一个本地运行的基础工作流。

### 7.2 未来扩展方向

结合项目长期演进目标：

1. 引入 LLM，增强工单理解和分类能力。
2. 引入 Tools，连接真实客服业务系统。
3. 引入 Checkpoint / Persistence，实现状态持久化和恢复。
4. 引入 Human-in-the-loop，完善人工审核机制。
5. 进一步扩展为 Multi-Agent 客服处理系统。
6. 最终实现 API 化、容器化和云端部署。

> 以上仅为规划，不代表当前版本已经实现。

