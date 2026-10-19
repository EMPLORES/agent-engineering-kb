
class AgentState:
    def __init__(self):
        # 当前任务
        self.current_task = None

        # 当前任务结果
        self.result = None


class Memory:
    def __init__(self):
        # 跨任务保留的信息
        self.user_preferences = {}


# ===== 第一次任务 =====

state1 = AgentState()
memory = Memory()

state1.current_task = "帮我规划周末活动"
state1.result = "正在分析用户的活动偏好"

# 将用户的长期偏好保存到 Memory
memory.user_preferences["activity"] = "户外活动"

print("=== 第一次任务 ===")
print("任务：", state1.current_task)
print("结果：", state1.result)
print("Memory：", memory.user_preferences)


# ===== 第二次任务 =====

state2 = AgentState()
state2.current_task = "推荐一个周末活动"

# 新任务读取之前保存的偏好
preference = memory.user_preferences.get("activity")

if preference == "户外活动":
    recommendation = "推荐徒步或骑行等户外活动"
else:
    recommendation = "需要进一步了解用户偏好"

state2.result = recommendation

print("\n=== 第二次任务 ===")
print("任务：", state2.current_task)
print("State：", state2.__dict__)
print("读取到的偏好：", preference)
print("推荐依据：", state2.result)
