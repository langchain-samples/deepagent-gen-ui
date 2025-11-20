from langchain.agents.middleware import AgentMiddleware
from langgraph.runtime import Runtime
from typing import Any, Annotated, Sequence, TypedDict
from langgraph.graph.ui import push_ui_message, AnyUIMessage, ui_message_reducer
from langchain.agents.middleware import AgentState

class UIState(AgentState):
    ui: Annotated[Sequence[AnyUIMessage], ui_message_reducer]

class ToolGenUI(TypedDict):
    component_name: str


# NOTE: Push the UI Message in after_model with empty props
class GenUIMiddleware(AgentMiddleware):
    state_schema = UIState

    def __init__(self, tool_to_genui_map: dict[str, ToolGenUI]):
        self.tool_to_genui_map = tool_to_genui_map
        
    def after_model(self, state: UIState, runtime: Runtime) -> dict[str, Any] | None:
        last_message = state["messages"][-1]
        if last_message.type != "ai":
            return
        if last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                if tool_call["name"] in self.tool_to_genui_map:
                    component_name = self.tool_to_genui_map[tool_call["name"]]["component_name"]
                    push_ui_message(
                        component_name,
                        {},
                        metadata={
                            "tool_call_id": tool_call["id"],
                            "message_id": last_message.id
                        },
                        message=last_message
                    )