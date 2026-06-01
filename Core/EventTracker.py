class EventTracker:
    """Tracks which date events have been triggered (once per NPC per level)."""

    def __init__(self):
        # key format: "npc_id:level"  contoh: "lucy:2"
        self._triggered: dict[str, bool] = {}

    def has_triggered(self, npc_id: str, level: int) -> bool:
        key = f"{npc_id}:{level}"
        return self._triggered.get(key, False)

    def mark_triggered(self, npc_id: str, level: int) -> None:
        key = f"{npc_id}:{level}"
        self._triggered[key] = True
        print(f"[DateEventTracker] Marked triggered: {key}")

    def get_save_data(self) -> dict:
        return dict(self._triggered)

    def load_save_data(self, data: dict) -> None:
        self._triggered = dict(data) if data else {}
        print(f"[DateEventTracker] Loaded {len(self._triggered)} triggered events")