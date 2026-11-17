"""
Week 6: Shared State Schema & Checkpointer
第6週：共有状態スキーマとチェックポインタ（状態永続化）
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
import sqlite3
import os

class GraphState(BaseModel):
    """
    Central state ledger passed across graph nodes.
    グラフ内の全ノード間で共有・更新される状態台帳
    """
    # Re-validate on every assignment, so `state.revision_count = -1` fails immediately.
    # 代入のたびに検証し、不正な値をその場で検出する
    model_config = ConfigDict(validate_assignment=True)

    thread_id: str = Field(default="default", description="Session identifier for isolation")
    topic: str = Field(description="Research or drafting topic")
    plan: List[str] = Field(default_factory=list, description="Rubric criteria produced by Planner")
    current_draft: str = Field(default="", description="Latest draft produced by Drafter")
    critique_notes: List[str] = Field(default_factory=list, description="Actionable feedback from Critic")
    revision_count: int = Field(default=0, ge=0, description="Number of draft revisions executed")
    max_iterations: int = Field(default=3, ge=1, description="Hard ceiling on revision cycles")
    is_approved: bool = Field(default=False, description="True if Critic approves the draft")
    status: str = Field(default="in_progress", description="'in_progress', 'completed', or 'needs_attention'")
    execution_trace: List[str] = Field(default_factory=list, description="Ordered log of visited nodes")

class SQLiteCheckpointer:
    """
    Persists GraphState snapshots per thread_id to survive restarts.
    スレッドIDごとにGraphStateのスナップショットをSQLiteへ永続化
    """
    def __init__(self, db_path: str = "data/checkpoints.sqlite3"):
        self.db_path = db_path
        db_dir = os.path.dirname(db_path)
        if db_dir:  # a bare filename like "cp.sqlite3" has no directory to create
            os.makedirs(db_dir, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS checkpoints (
                thread_id TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def save(self, state: GraphState) -> None:
        """
        TODO [Task 1.1]: Persist serialized GraphState into SQLite by thread_id.
        - Serialize `state` using `state.model_dump_json()`.
        - Insert or update row in `checkpoints` keyed on `state.thread_id`.
        """
        raise NotImplementedError("TODO [Task 1.1]: Implement SQLiteCheckpointer.save")

    def load(self, thread_id: str) -> Optional[GraphState]:
        """
        TODO [Task 1.2]: Restore GraphState from SQLite for the given thread_id.
        - Query `state_json` for `thread_id`.
        - Return `GraphState.model_validate_json(row[0])` if found, else `None`.
        """
        raise NotImplementedError("TODO [Task 1.2]: Implement SQLiteCheckpointer.load")
