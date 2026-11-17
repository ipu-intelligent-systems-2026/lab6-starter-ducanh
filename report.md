# Lab 6 Report: Stateful Agent Orchestration & Graph Workflows

##  Implementation Report

### Overview
This lab implements a cyclic **Planner → Drafter ↔ Critic** `StateGraph` with persistent SQLite checkpointing. The graph models an iterative reflection loop where a draft is repeatedly revised based on critic feedback until approval or a hard iteration ceiling.

---

### Task 1: SQLiteCheckpointer (`src/state.py`)

#### Task 1.1 — `save()`
Serializes `GraphState` to JSON via `model_dump_json()` and upserts it into the `checkpoints` table keyed on `thread_id` using `INSERT ... ON CONFLICT DO UPDATE`.

#### Task 1.2 — `load()`
Queries the `checkpoints` table by `thread_id`. Returns `GraphState.model_validate_json(row[0])` if found, otherwise `None`.

**Key design decisions:**
- Used SQLite's `ON CONFLICT` (UPSERT) syntax for atomic insert-or-update in a single statement.
- Each `save()`/`load()` opens and closes its own connection for simplicity and thread safety.

---

### Task 2: Cyclic StateGraph (`src/graph.py`)

#### Task 2.1 — `route_after_critic()`
Conditional routing logic after the critic node:
- Returns `"END"` if `state.is_approved` is `True`.
- Returns `"END"` if `state.revision_count >= state.max_iterations` (hard ceiling).
- Returns `"drafter"` otherwise (loop back for another revision).

#### Task 2.2 — `run_reflection_graph()`
Executes the full graph loop:
1. Runs `planner_node()` → saves checkpoint.
2. Enters loop: `drafter_node()` → save → `critic_node()` → save → `route_after_critic()`.
3. On `"END"`: sets `status` to `"completed"` (if approved) or `"needs_attention"` (if ceiling hit without approval), saves final checkpoint, and breaks.

**Execution flow (normal convergence with default stub):**
```
planner → drafter → critic (reject, rev=1) → drafter → critic (approve, rev=2) → END
Trace: ["planner", "drafter", "critic", "drafter", "critic"]
```

---

### Test Results

```
tests/test_lab6.py::test_route_after_critic_approved        PASSED  [ 12%]
tests/test_lab6.py::test_route_after_critic_continue         PASSED  [ 25%]
tests/test_lab6.py::test_route_after_critic_max_ceiling      PASSED  [ 37%]
tests/test_lab6.py::test_graph_normal_convergence            PASSED  [ 50%]
tests/test_lab6.py::test_graph_hard_ceiling_needs_attention  PASSED  [ 62%]
tests/test_lab6.py::test_sqlite_checkpointer_persistence    PASSED  [ 75%]
tests/test_lab6.py::test_checkpoint_saved_after_every_node   PASSED  [ 87%]
tests/test_lab6.py::test_thread_isolation                    PASSED  [100%]

============================== 8 passed in 0.16s ===============================
```

**All 8 tests passed.** ✅
