\# Runtime Failure, Retry \& Recovery



\## 1. Runtime Failure Classification



\### 1.1 Transient Failure

Transient Failure（临时性失败）：指由于临时因素导致当前步骤执行失败，但再次尝试仍有成功可能性的错误。Runtime 根据预先定义的重试策略，判断是否重新执行当前步骤。

本实验中自动重试机制在于第一次执行collect时发生临时错误，runtime经过判断后满足自动重试机制预定义的条件决定retry



\### 1.2 Permanent Failure

Permanent Failure（永久性失败）：是执行过程中由于部分条件缺失等问题导致在当前条件下无法通过简单重试解决的失败，例如配置错误或缺少必要条件。

本实验中发布的过程中由于发生永久性错误：模拟发布目标配置错误，runtime经过判断决定不进行重试，给出最终输出结果：执行失败，终止任务。



\### 1.3 Execution Interruption

Execution Interruption（执行中断）：指当前执行流程由于异常或其他中断原因停止。后续可以通过加载之前持久化的 Checkpoint，恢复执行流程。



执行中断可以是由于异常情况例如关机等情况发生时，后续可以通过checkpoint由runtime读取然后恢复进程。也可以由于一些特殊原因中断例如涉及超出权限内容，需要人为介入等后可以通过checkpoint再次恢复进程，如果中断涉及权限不足或需要人工审批，恢复执行前可能还需要先解决对应问题或完成人工介入。而普通任务失败的原因可能是一些临时错误，后续经过runtime决定是否retry。
本实验中通过python对象模拟中断情况发生，analyze发生，runtime检测到执行中断，等待恢复后runtime后续通过读取checkpoint后recovery进程




\## 2. Retry Mechanism



\### 2.1 What Is Retry?

Retry：runtime在任务失败后，经过判断决定再次尝试当前步骤的定义，经常发生在由于临时错误导致执行失败后，由runtime判断后决定再次执行



\### 2.2 RetryPolicy

RetryPolicy：规定当前步骤执行失败后的重试策略，其中 max\_attempts 用于限制当前步骤的最大尝试次数，避免无限重试造成不必要的时间和资源消耗。




本实验中，PermanentFailure 不进行重试；TransientFailure 满足预设条件时允许重试，但仍受到 max\_attempts 的限制。



\### 2.3 Retry vs Recovery



\- Retry：负责解决临时错误当前步骤执行失败后，再次尝试当前步骤，执行主体还是当前runtime，仍处于当前执行流程

\- Recovery：负责解决执行过程中中断后，加载checkpoint后恢复执行，执行主体是恢复后runtime，从之前保存的状态继续





\## 3. Checkpoint Mechanism



\### 3.1 What Is a Checkpoint?



Checkpoint：某一时间点保存的 State 快照，用于在执行中断后恢复之前持久化的执行状态。



在本实验中，Checkpoint 通过 JSON 文件进行持久化。如果只保存在 Python 字典中，程序关闭后数据会丢失。



在支持多执行会话的系统中，可以使用 thread ID 等标识关联对应的执行状态和 Checkpoint，便于后续恢复。





\### 3.2 Checkpoint State

\- state：当前任务的整体状态数据。

\- results：记录已完成步骤产生的结果。

\- completed\_steps：记录已经成功完成并被标记的步骤。





\### 3.3 Checkpoint Save Timing

本实验中，当前步骤成功执行后，Runtime 依次执行以下操作：



1\. 将步骤结果写入 results。

2\. 将步骤名称加入 completed\_steps。

3\. 调用 save()，将更新后的 State 保存到磁盘 Checkpoint。



前两个操作更新的是当前 Python 进程中的内存 State，第三个操作才完成磁盘持久化。

analyze 第一次执行时发生中断，尚未完成结果写入、步骤完成标记和 Checkpoint 保存。因此磁盘上的 Checkpoint 仍然保留之前的状态，completed\_steps 中没有 analyze。Recovery 读取旧 Checkpoint 后，会重新执行 analyze。


内存state只是保存在当前的python字典中，程序关闭，内容丢失
磁盘checkpoint完成持久化进程，程序关闭并不会影响后续recovery恢复当前执行状态



\## 4. Execution Recovery



\### 4.1 Loading Checkpoint

本实验中，新 Runtime 通过 CheckpointStore.load() 读取之前保存的 JSON Checkpoint。

在更复杂的多会话系统中，可以使用 thread ID 等标识定位对应的 Checkpoint。




恢复时读取的是中断发生之前最后一次成功持久化的执行状态，而不一定是中断发生前内存中的最新状态。



\### 4.2 Resuming Execution

本实验中，Runtime 根据 Checkpoint 中的 completed\_steps 判断哪些步骤已经完成，并通过 results 获取对应结果。对于已完成的步骤，Runtime 会跳过执行；对于尚未完成的步骤，则继续执行。



不同系统和框架可能采用不同的状态管理和恢复策略，因此具体的恢复行为也可能有所不同。

\### 4.3 Recovery Limitations

任务执行成功，但 Checkpoint 尚未保存就发生崩溃时，Recovery 读取的仍然是上一次成功保存的 Checkpoint，其中没有记录该步骤已经执行成功的信息，因此可能重复执行某个步骤。这种情况具体取决于任务执行结果与 Checkpoint 持久化之间的时序，以及步骤是否涉及外部副作用。



\## 5. Engineering Considerations



\### 5.1 Failure Handling Strategy

再次重试的决定是runtime判断后决定的，对于永久性错误等因素进行重试只会浪费成本，时间，人力等资源，所以重试应针对具有恢复可能性的错误，并结合错误类型、重试策略和最大尝试次数决定是否再次执行，而不是浪费成本和资源


当前实验中的错误类型分为Permanent Failure和Transient Failure。





\### 5.2 Checkpoint Consistency

内存中的执行进度，不等于已经持久化的执行进度。

当程序在两次持久化之间崩溃时，恢复只能依据最后一次成功保存的状态，而不能依据已经丢失的内存状态。







\### 5.3 External Side Effects

本实验中的 analyze 没有真实外部副作用，但如果一个步骤涉及外部操作，例如支付、发送邮件或创建订单，那么在操作已经成功、Checkpoint 尚未保存时发生崩溃，Recovery 可能再次执行该步骤，造成重复操作。



因此，仅依靠 Checkpoint 无法保证外部操作只执行一次。





&#x09;





\## 6. Experiment Summary



\- 本实验实现了什么：模拟 Agent 任务，进行数据收集：第一次遇到临时错误，Runtime 判断可以重试；第二次成功。→数据分析：执行过程中模拟 Runtime 意外中断。重新创建 Runtime 后，从 Checkpoint 恢复。→发布报告：遇到永久性错误，Runtime 判断不应该重试，终止执行。



\- 本实验验证了什么：已完成的数据收集不会因为恢复而重复执行。被中断的数据分析可以重新执行。永久性错误不会触发无意义的重试。



\- 本实验没有实现什么：没有实现生产级 Runtime 的完整故障处理能力，例如真实进程被终止后的恢复、复杂的持久化机制，以及外部副作用的可靠处理。本实验使用模拟异常和 JSON 文件展示基础机制。



\- 本实验与生产级 Runtime 的区别：本实验使用 Python 标准库和 JSON 文件，模拟 Runtime 的失败分类、重试、Checkpoint 保存和恢复过程。生产级 Runtime 需要进一步处理真实运行环境中的复杂故障、持久化一致性、外部副作用以及长期执行状态管理等问题。



\## 7. Key Takeaways



用自己的语言总结：



1\. Retry 解决当前步骤执行失败，再次尝试当前步骤

2\. 2. Checkpoint 负责保存某一时间点的 State 快照，为执行中断后的 Recovery 提供恢复依据。

3\. Recovery 解决执行过程发生中断加载 Checkpoint 并恢复执行

4\. 持久化时机决定了 Recovery 能够读取到的最新执行进度。只有成功保存到磁盘的状态，才能在程序中断后通过 Checkpoint 恢复。

5\. 内存中的执行进度，不等于已经持久化的执行进度。当程序在两次持久化之间崩溃时，恢复只能依据最后一次成功保存的状态，而不能依据已经丢失的内存状态。

