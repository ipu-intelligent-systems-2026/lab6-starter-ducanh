"""
Week 6: Cyclic StateGraph Execution Engine (Planner -> Drafter <-> Critic)
第6週：循環型StateGraph実行エンジン（計画・執筆・批評ループ）
"""
from typing import Callable, Optional
from src.state import GraphState, SQLiteCheckpointer

def planner_node(state: GraphState) -> GraphState:
    """Decomposes the topic into evaluation criteria."""
    state.plan = [
        f"Clear explanation of {state.topic}",
        "Concrete technical example included",
        "Concise structure without fluff"
    ]
    state.execution_trace.append("planner")
    return state

def drafter_node(state: GraphState, generator_fn: Optional[Callable[[GraphState], str]] = None) -> GraphState:
    """
    Produces or revises current_draft and increments revision_count.
    """
    state.revision_count += 1
    if generator_fn is not None:
        state.current_draft = generator_fn(state)
    else:
        feedback = f" (Addressed: {', '.join(state.critique_notes)})" if state.critique_notes else ""
        state.current_draft = f"Draft v{state.revision_count} on {state.topic}{feedback}"
    state.execution_trace.append("drafter")
    return state

def critic_node(state: GraphState, evaluator_fn: Optional[Callable[[GraphState], tuple[bool, list[str]]]] = None) -> GraphState:
    """
    Evaluates current_draft against state.plan.
    """
    if evaluator_fn is not None:
        approved, notes = evaluator_fn(state)
        state.is_approved = approved
        state.critique_notes = notes
    else:
        # Default deterministic stub: approves once revision_count >= 2
        if state.revision_count >= 2:
            state.is_approved = True
            state.critique_notes = []
        else:
            state.is_approved = False
            state.critique_notes = ["Add concrete technical example"]
    state.execution_trace.append("critic")
    return state

def route_after_critic(state: GraphState) -> str:
    """
    Conditional Routing Edge after Critic.
    """
    if state.is_approved:
        return "END"
    if state.revision_count >= state.max_iterations:
        return "END"
    return "drafter"

def run_reflection_graph(
    initial_state: GraphState,
    checkpointer: Optional[SQLiteCheckpointer] = None,
    generator_fn: Optional[Callable[[GraphState], str]] = None,
    evaluator_fn: Optional[Callable[[GraphState], tuple[bool, list[str]]]] = None
) -> GraphState:
    """
    Execute the Cyclic StateGraph Loop:
    Planner -> (Drafter <-> Critic) loop -> terminal status.
    """
    state = initial_state

    # 1. Run planner
    state = planner_node(state)
    if checkpointer is not None:
        checkpointer.save(state)

    # 2. Loop: drafter -> critic -> route
    while True:
        state = drafter_node(state, generator_fn)
        if checkpointer is not None:
            checkpointer.save(state)

        state = critic_node(state, evaluator_fn)
        if checkpointer is not None:
            checkpointer.save(state)

        next_step = route_after_critic(state)
        if next_step == "END":
            state.status = "completed" if state.is_approved else "needs_attention"
            if checkpointer is not None:
                checkpointer.save(state)
            break

    return state
