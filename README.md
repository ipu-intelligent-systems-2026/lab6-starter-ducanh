# Lab 6: Stateful Agent Orchestration & Graph Workflows
# 課題6：状態遷移グラフによるエージェントオーケストレーション

## [EN] Assignment Overview
In this lab, you will implement a cyclic **Planner $\rightarrow$ Drafter $\leftrightarrow$ Critic** `StateGraph` with persistent checkpointing:
1. **Task 1 (`src/state.py`):** Implement `SQLiteCheckpointer.save()` and `SQLiteCheckpointer.load()` to persist `GraphState` snapshots by `thread_id`.
2. **Task 2.1 (`src/graph.py`):** Implement `route_after_critic()` to route approved drafts or max-iteration-exceeded runs to `"END"`, and unapproved drafts back to `"drafter"`.
3. **Task 2.2 (`src/graph.py`):** Implement `run_reflection_graph()` to execute the cyclic graph loop, save checkpoints after each node, and set terminal status (`"completed"` vs. `"needs_attention"`).

### Local Testing & Verification
```bash
pip install -r requirements.txt
pytest -v tests/test_lab6.py
```

---

## [JA] 課題概要
本演習では、状態永続化（チェックポイント）を備えた循環型 **Planner $\rightarrow$ Drafter $\leftrightarrow$ Critic** の `StateGraph` を実装します：
1. **タスク 1 (`src/state.py`):** `thread_id` ごとに `GraphState` スナップショットをSQLiteへ保存・復元する `SQLiteCheckpointer.save()` と `load()` を実装。
2. **タスク 2.1 (`src/graph.py`):** 批評後の条件付きルーティング関数 `route_after_critic()` を実装し、承認済みまたは最大反復回数到達時は `"END"` へ、未承認時は `"drafter"` へ遷移させる。
3. **タスク 2.2 (`src/graph.py`):** 循環グラフを実行し、各ノード遷移後にチェックポイントを保存し、最終ステータス（`"completed"` または `"needs_attention"`）を設定する `run_reflection_graph()` を実装。

### ローカル実行・テスト手順
```bash
pip install -r requirements.txt
pytest -v tests/test_lab6.py
```
