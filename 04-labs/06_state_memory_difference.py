class AgentState:

    def __init__(self):
        # 当前任务的信息
        self.current_task = None
        
        # 当前任务执行产生的信息
        self.tool_result = None



class Memory:

    def __init__(self):
        # 长期保存的信息
        self.user_preferences = {}



# 当前一次 Agent 运行

state = AgentState()

memory = Memory()



# 用户当前任务

state.current_task = "Find weather in Beijing"



# 当前任务执行结果

state.tool_result = "Sunny"



# 长期用户信息

memory.user_preferences[
    "activity"
] = "User likes outdoor activities"



print("State:")
print(vars(state))


print("\nMemory:")
print(memory.user_preferences)