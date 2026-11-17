"""
Autograding test suite for Lab 6.
Lab 6 自動採点用テストスイート
"""
import pytest
import os
import tempfile
from src.state import GraphState, SQLiteCheckpointer
from src.graph import route_after_critic, run_reflection_graph

def test_route_after_critic_approved():
    st = GraphState(topic="StateGraphs", revision_count=1, max_iterations=3, is_approved=True)
    assert route_after_critic(st) == "END"

def test_route_after_critic_continue():
    st = GraphState(topic="StateGraphs", revision_count=1, max_iterations=3, is_approved=False)
    assert route_after_critic(st) == "drafter"

def test_route_after_critic_max_ceiling():
    st = GraphState(topic="StateGraphs", revision_count=3, max_iterations=3, is_approved=False)
    assert route_after_critic(st) == "END"

def test_graph_normal_convergence():
    state = GraphState(topic="Cyclic Reflection", max_iterations=3)
    final_state = run_reflection_graph(state)
    assert final_state.is_approved is True
    assert final_state.status == "completed"
    assert final_state.revision_count == 2
    assert final_state.execution_trace == ["planner", "drafter", "critic", "drafter", "critic"]

def test_graph_hard_ceiling_needs_attention():
    # Critic always rejects
    always_reject = lambda st: (False, ["Still needs improvement"])
    state = GraphState(topic="Strict Topic", max_iterations=3)
    final_state = run_reflection_graph(state, evaluator_fn=always_reject)
    assert final_state.is_approved is False
    assert final_state.status == "needs_attention"
    assert final_state.revision_count == 3

def test_sqlite_checkpointer_persistence():
    with tempfile.NamedTemporaryFile(suffix=".sqlite3", delete=False) as tmp:
        db_path = tmp.name

    try:
        cp = SQLiteCheckpointer(db_path=db_path)
        state = GraphState(thread_id="session_42", topic="Checkpointing", max_iterations=2)
        final_state = run_reflection_graph(state, checkpointer=cp)

        restored = cp.load("session_42")
        assert restored is not None
        assert restored.thread_id == "session_42"
        assert restored.status == final_state.status
        assert restored.revision_count == final_state.revision_count
        assert cp.load("nonexistent_thread") is None
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)


class RecordingCheckpointer(SQLiteCheckpointer):
    """Records every saved snapshot so the test can check *when* checkpoints happen."""
    def __init__(self, db_path):
        super().__init__(db_path=db_path)
        self.saved = []

    def save(self, state):
        self.saved.append(list(state.execution_trace))
        super().save(state)

def test_checkpoint_saved_after_every_node():
    with tempfile.TemporaryDirectory() as tmp:
        cp = RecordingCheckpointer(db_path=os.path.join(tmp, "cp.sqlite3"))
        final_state = run_reflection_graph(GraphState(thread_id="t1", topic="Checkpoints"), checkpointer=cp)
        # one save after each node, plus the final save with the terminal status
        assert cp.saved[:5] == [
            ["planner"],
            ["planner", "drafter"],
            ["planner", "drafter", "critic"],
            ["planner", "drafter", "critic", "drafter"],
            ["planner", "drafter", "critic", "drafter", "critic"],
        ]
        assert cp.load("t1").status == final_state.status == "completed"

def test_thread_isolation():
    with tempfile.TemporaryDirectory() as tmp:
        cp = SQLiteCheckpointer(db_path=os.path.join(tmp, "cp.sqlite3"))
        run_reflection_graph(GraphState(thread_id="student_a", topic="Topic A"), checkpointer=cp)
        run_reflection_graph(GraphState(thread_id="student_b", topic="Topic B", max_iterations=1),
                             checkpointer=cp, evaluator_fn=lambda st: (False, ["Revise"]))
        a, b = cp.load("student_a"), cp.load("student_b")
        assert (a.topic, a.status) == ("Topic A", "completed")
        assert (b.topic, b.status) == ("Topic B", "needs_attention")
