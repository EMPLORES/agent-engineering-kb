from typing import TypedDict

from langgraph.graph import StateGraph, END


class State(TypedDict):
    number: int
    result: str



def check_number(state):

    print("Check number")

    if state["number"] > 10:
        return {
            "result":"large"
        }

    else:
        return {
            "result":"small"
        }



def decide_next(state):

    if state["result"]=="large":
        return "large_node"

    return "small_node"



def large_node(state):

    print("Large Node")

    return {
        "result":
        "number is large"
    }



def small_node(state):

    print("Small Node")

    return {
        "result":
        "number is small"
    }



graph = StateGraph(State)


graph.add_node(
    "check",
    check_number
)


graph.add_node(
    "large_node",
    large_node
)


graph.add_node(
    "small_node",
    small_node
)


graph.set_entry_point(
    "check"
)


graph.add_conditional_edges(
    "check",
    decide_next,
    {
        "large_node":"large_node",
        "small_node":"small_node"
    }
)


graph.add_edge(
    "large_node",
    END
)


graph.add_edge(
    "small_node",
    END
)


app=graph.compile()


print(
    app.invoke(
        {
            "number":20,
            "result":""
        }
    )
)