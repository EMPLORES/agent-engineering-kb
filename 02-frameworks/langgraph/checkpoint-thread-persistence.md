# LangGraph Checkpoint、Thread 与 Persistence 机制

## 1. Checkpointer 的作用

Checkpointer是真正负责checkpoint怎么存储，存在哪里，用什么方式序列化，按什么键检索以及什么时候写入，真正意义上的决定checkpoint如何存储和存储如何实现的问题。

Checkpointer 不需要通过 Builder 构建，而是在 Graph 编译时通过 `compile(checkpointer=...)` 接入。

Builder 负责定义 Graph 的节点、边和状态流转关系；Checkpointer 负责工作流执行过程中的 Checkpoint 保存与读取。

编译完成后，Graph 就具备了通过 Checkpointer 管理工作流状态快照的能力。

checkpoint存储的是某一时间点下state的状态快照，state存储的是当前任务状态下的所有数据内容和状态。

---

## 2. Thread 与 Checkpoint

- `thread_id` 的作用是标识一条工作流执行线程。
- `checkpoint_id` 的作用是通过id的不同在当前工作流执行线程thread中找到需要的checkpoint。

一个 Thread 可以关联多个不同 super-step 产生的 Checkpoint，这些 Checkpoint 共同构成该 Thread 的工作流执行历史。

Thread 本身只是工作流执行上下文的标识，并不是由 Checkpoint 组成的存储对象。实际 Checkpoint 数据由 Checkpointer 负责保存和管理。

通过系统需要的某一时间点的checkpoint，通过checkpoint_id去在整个thread标识的state history中去定位，然后找到当前checkpoint下snapshot的全部内容用与后续工作流的恢复工作。

---

## 3. StateSnapshot 与 State History

- **StateSnapshot 的主要内容**
  - `values`：保存当前 Checkpoint 对应的 State 数据，例如 task_id、description 和 approval_status。
  - `next`：记录当前 Checkpoint 之后尚待执行的节点名称集合。
  - `config`：包含当前 Checkpoint 的配置标识，例如 thread_id 和 checkpoint_id。
  - `metadata`：保存当前 Checkpoint 的执行元数据，例如 Checkpoint 来源（source）、执行步骤（step）以及父级 Checkpoint 关系（parents）等。
  - `tasks`：记录当前 Checkpoint 对应的任务信息，例如任务节点名称、执行路径、错误信息、中断信息以及执行结果等。

- **`get_state()` 的作用**：获取指定 Thread 当前最新的 StateSnapshot；也可以通过指定 checkpoint_id 查询某个历史 Checkpoint 对应的快照。
- **`get_state_history()` 的作用**：获取指定 Thread 的 Checkpoint 历史记录，默认按照从新到旧的顺序返回。

---

## 4. Interrupt 与工作流暂停恢复

- **`interrupt()` 的作用**：当工作流执行到需要人工介入的位置时，暂停当前节点，并向调用方返回人工审核请求。恢复执行时，LangGraph 会将 `Command(resume=...)` 提供的恢复值交给对应的 `interrupt()` 调用。

- **`__interrupt__` 返回内容**：包含 Interrupt 对象，其中的 value 保存了人工审核请求的数据，例如 task_id、description 和 question；同时还包含中断 ID 等信息。

- **工作流暂停时的 StateSnapshot**：存储的当前super-step对应的checkpoint保存的内容。

- **`Command(resume=...)` 如何恢复执行**：通过将中断响应的HITL结果提供给interrupt（）。

- **恢复时节点从头重新执行的机制**：恢复时LangGraph会通过request_approval节点的开头进行执行，而不是直接从上次interrupt（）中断后面的代码继续。

- **`interrupt()` 前副作用操作的风险**：应该避免付款，发送邮件，修改账户权限 等操作，否则恢复时可能会重复执行当前操作。

---

## 5. Persistence 与存储边界

### InMemorySaver 的工作方式

将当前的数据内容存储到python对象中，一旦程序关闭所有数据内容都会丢失。

### 同一进程与跨进程的状态读取区别

同一 Python 进程中，如果进程 A 和进程 B 使用同一个 InMemorySaver 实例、相同的 Thread 配置，就能够读取之前保存的 Checkpoint。

如果是两个独立 Python 进程，即使使用相同的 thread_id，只要各自创建了独立的 InMemorySaver 实例，也无法共享之前的 Checkpoint。

跨进程恢复需要两个进程连接到同一个持久化存储，并使用兼容的 Checkpointer 配置、thread_id 和 checkpoint 命名空间等条件，才能找到之前保存的工作流状态。

相同thread_id仅能代表对于当前工作流的标识相同，但由于数据存储的方式以及方法等各项因素的不同导致仅凭thread_id 并不能恢复状态。

### 持久化 Checkpointer 的作用

当 Graph 接入持久化 Checkpointer 后，LangGraph 会在工作流执行过程中按照 Checkpoint 机制自动保存状态快照。开发者不需要在每个节点中手动编写数据库保存逻辑。

SQLite / PostgreSQL 可以作为持久化 Checkpointer 的底层存储，将工作流 Checkpoint 保存到数据库中，使状态能够跨进程保留，为后续恢复执行提供基础。

---

## 6. 工程实践总结

Thread 用于标识一整条工作流执行上下文，而不同 Checkpoint 记录了这条工作流在不同执行阶段的状态快照，共同构成该 Thread 的执行历史。后续在进行HITL等恢复执行进程时通过interrupt（）将执行进程暂停，并返回工作流暂停时提供__interrupt__ 返回内容，在中断后恢复进程时通过command将approval的内容返回给interrupt，后续恢复进程再次进入request approval 节点执行到达执行interrupt时LangGraph识别到这是一次恢复调用将之前通过command(resume=...)传入的人工审核结果交给interrupt()，继续执行后面的代码。

长时间运行工作流需要将任务流数据内容存储到数据库中，放止数据的丢失无法恢复之前的执行进程。

在生产级 Agent 运行框架中，需要通过持久化 Checkpointer 将工作流状态长期保存，方便在之后执行进程中进行调用以及避免由于程序中断而导致的数据丢失等情况。

需要注意，Checkpoint 持久化不等于工作流自动恢复。





