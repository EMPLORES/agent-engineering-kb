

\# Idempotency \& Safe Retry



\## 1. Why Idempotency Matters

解决外部业务操作已经成功执行，但 Runtime 尚未保存 Checkpoint，导致恢复执行时重复执行外部操作的问题。
Runtime 已经成功执行某个步骤，但在保存 Checkpoint 之前发生中断。恢复执行时，Runtime 读取上一次成功保存的 Checkpoint，由于其中没有记录该步骤已经完成，因此可能再次执行这个步骤。





\## 2. What Is Idempotency?


幂等性（Idempotency）是指同一个操作执行一次或多次，最终产生的业务效果保持一致。



重复请求不一定意味着重复业务操作。通过幂等机制，系统可以识别重复请求，并返回之前的处理结果，而不是再次执行实际业务操作。


本次实验使用本地 JSON 文件模拟支付系统的持久化记录，并通过创建新的 Runtime 对象模拟重启。Runtime 再次发起支付请求时，PaymentGateway 通过检测 Idempotency Key 判断请求是否重复，并在识别到重复请求后返回之前的支付结果。



\## 3. Idempotency Key

Idempotency Key 用于标识一次业务操作。PaymentGateway 通过检查 Key 是否已经存在，判断当前请求是否属于之前已经处理过的业务操作。





同一个幂等键必须对应同一个业务操作，不能被不同的支付请求混用。如果请求参数不一致，程序会抛出 IdempotencyConflict 异常，而不是返回之前的支付结果或再次执行支付。

PaymentGateway 首先检查 Idempotency Key 是否存在。如果存在，则进一步检查 order\_id 和 amount 是否一致。参数一致时返回之前的支付结果；参数不一致时抛出 IdempotencyConflict 异常。








\## 4. Runtime Checkpoint vs Payment Ledger

Checkpoint 保存 Runtime 某一时间点的 State 快照，其中包含已完成步骤和对应的执行结果。



\- Ledger 保存支付系统已经处理的请求及支付结果。



两者保存的内容不同，负责的任务也不同，不能互相替代。




本次实验中，Checkpoint 保存某一时间点的 State 快照，用于记录 Runtime 的执行进度；Ledger 保存支付系统已经处理的请求及支付结果，用于识别重复请求，避免重复扣款。



\## 5. Safe Retry

Runtime 中断后，新的 Runtime 加载上一次成功保存的 Checkpoint。由于其中没有记录支付步骤已经完成，因此会再次执行支付操作。




由于第一次支付请求的记录已经被 PaymentGateway 保存到 Ledger 中，第二次请求使用相同的 Idempotency Key 时，PaymentGateway 能够识别重复请求，并返回之前的支付结果，而不会再次扣款。Runtime 获取结果后更新 State 并保存 Checkpoint，从而完成本次执行。

Runtime 负责整体任务执行、步骤调度以及 State 和 Checkpoint 的管理；外部支付系统负责实际支付操作和支付记录管理。Runtime 通过调用支付接口与外部支付系统交互，两者具有不同的职责边界。



\## 6. Limitations

用本地 JSON 文件模拟支付系统的持久化记录，用新的 Runtime 对象模拟重启。它不是生产级支付接口，也不代表已经解决所有分布式系统中的一致性问题。

当前实验没有实现生产级支付系统，也不能保证真实生产环境中的支付操作绝对只执行一次。实际系统还需要考虑网络故障、持久化可靠性以及分布式一致性等问题。



\- Idempotency 不等于 Exactly-once



\- 网络故障与分布式一致性仍然存在其他问题



\## 7. Experiment Summary

实验使用本地 JSON 文件模拟支付系统的持久化记录，并通过创建新的 Runtime 对象模拟重启，验证了利用 Idempotency Key 识别重复请求、返回之前的支付结果以及避免重复扣款的过程。


验证了 Runtime 在 Checkpoint 未记录步骤完成的情况下重新发起请求时，PaymentGateway 如何通过 Ledger 和 Idempotency Key 避免重复扣款。


没有实现 Exactly-once。





\## 8. Key Takeaways

\- Idempotency（幂等性）用于避免同一个业务操作被重复执行时产生重复的业务效果。

\- Idempotency Key 用于标识业务操作，帮助外部系统识别重复请求。

\- PaymentGateway 通过检查 Idempotency Key 和业务参数识别重复请求。

\- Payment Ledger 保存之前已经处理的支付记录和结果。

\- Runtime Checkpoint 保存执行进度，两者不能互相替代。

\- Safe Retry 通过结合 Runtime 的执行恢复机制与外部系统的幂等处理，降低重复执行外部操作的风险。



