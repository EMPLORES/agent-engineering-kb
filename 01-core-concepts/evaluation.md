# Evaluation（评估）

## 1. Evaluation 是什么

Evaluation 是通过评估标准来判断结果或行为是否达到预期的机制。

## 2. Evaluator 与 Evaluation Criteria 的关系

- **Evaluator（评估器）**：按照评估标准执行判断的机制，用于判断输出结果的质量，例如答案准确率、任务成功率、是否成功调用工具等。
- **Evaluation Criteria（评估标准）**：规定结果或行为需要满足哪些条件。Evaluator 根据这些标准执行评估。

二者互补、相辅相成，共同把"执行完成"和"质量评估"区分开。

## 3. 为什么执行成功不代表结果合格

执行完成只能说明任务在执行层面已经结束，不能说明结果通过了评估标准。

即使 Agent 顺利执行完任务，输出仍可能存在以下问题：

- 答案错误
- 任务目标未达成
- 工具调用不符合预期

因此需要通过 Evaluation 判断结果是否满足预定标准。

## 4. 规则评估与 LLM 评估的区别

| | 规则评估 | LLM 评估 |
| --- | --- | --- |
| 适用场景 | 明确、可验证的条件，例如必需字段、数据类型、数值范围、是否包含指定内容 | 语义、相关性、答案质量等难以完全写成固定规则的标准 |
| 判断方式 | 可以用 Python 等代码准确表达 | 更偏向抽象、语义层面的判断 |
| 优点 | 可预测、结果一致 | 灵活 |
| 缺点 | 死板 | 判断可能不稳定，评估器自身也可能出错 |

实际使用中，两者更适合**结合使用**：既保留规则评估的可预测性和一致性，又利用 LLM 评估的灵活性，同时降低规则评估的死板和 LLM 评估的不稳定。

## 5. 当前实验的实现方式与局限

### 实验一：答案包含关键点（通过）

```text
D:\Projects\agent-engineering-kb>python 04-labs/25_basic_evaluation.py
用户问题： Python 中，列表和元组的主要区别是什么？
Agent 答案： 列表可以修改，元组通常不能修改。
评估结果： {'passed': True, 'checks': {'mentions_list': True, 'mentions_tuple': True, 'mentions_mutability': True}}
```

### 实验二：答案缺少关键点（未通过）

```text
D:\Projects\agent-engineering-kb>python 04-labs/25_basic_evaluation.py
用户问题： Python 中，列表和元组的主要区别是什么？
Agent 答案： 列表和元组都可以存储多个元素。
评估结果： {'passed': False, 'checks': {'mentions_list': True, 'mentions_tuple': True, 'mentions_mutability': False}}
```

### 局限

- Evaluator 的通过结果，只代表通过了**当前这套评估标准**，而不是通过了所有质量标准。
- 当前实验检查的是**关键词**，而不是答案的真实正确性。

## 6. Evaluation 与 Observability / Tracing 的关系

Evaluator 是否需要使用 Observability / Tracing 中的 Span、Metrics 等内容，取决于评估目标：

- **只判断答案是否符合参考答案**：通常只需要问题、Agent 答案、参考答案和评估标准。
- **分析工具调用是否正确、任务为什么失败**：通常需要 Tracing 中 Span 记录的执行过程和状态信息。