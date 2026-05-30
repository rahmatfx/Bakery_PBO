class DialogueManager:

    def __init__(self):
        self._entries: dict[str, dict] = {}    
        self._current_id: str | None = None
        self._finished: bool = False
        self._pending_affinity: int = 0       

    def start(self, entries: list[dict]) -> None:
        self._entries = {}
        for entry in entries:
            entry_id = entry.get("id")
            if entry_id:
                self._entries[entry_id] = entry

        self._current_id = entries[0]["id"] if entries else None
        self._finished = False
        self._pending_affinity = 0

        print(f"[DialogueManager] Started, entries: {len(self._entries)}, "
              f"first: {self._current_id}")

    def reset(self) -> None:
        self._entries = {}
        self._current_id = None
        self._finished = False
        self._pending_affinity = 0

    # Query 

    def get_current(self) -> dict | None:
        if not self._current_id:
            return None
        return self._entries.get(self._current_id)

    def get_current_text(self) -> str:
        entry = self.get_current()
        if not entry:
            return ""
        return entry.get("text", "")

    def get_current_choices(self) -> list[dict]:
        entry = self.get_current()
        if not entry:
            return []
        return entry.get("choices", [])

    def has_choices(self) -> bool:
        return len(self.get_current_choices()) > 0

    def is_finished(self) -> bool:
        return self._finished

    def is_active(self) -> bool:
        return self._current_id is not None and not self._finished

    def advance(self, choice_index: int = -1) -> int:
        if self._finished:
            return 0

        entry = self.get_current()
        if not entry:
            self._finished = True
            return 0

        choices = entry.get("choices", [])
        affinity_delta = 0
        next_id = None

        if choices and 0 <= choice_index < len(choices):
            # Branching: player pilih salah satu
            choice = choices[choice_index]
            affinity_delta = choice.get("affinity", 0)
            next_id = choice.get("next")
            print(f"[DialogueManager] Choice {choice_index}: "
                  f"affinity {'+' if affinity_delta >= 0 else ''}{affinity_delta}")
        else:
            # Linear: click to continue
            next_id = entry.get("next")
            print(f"[DialogueManager] Linear advance → {next_id}")

        # Pindah ke next atau selesai
        if next_id is None:
            self._finished = True
            self._current_id = None
            print("[DialogueManager] Dialogue finished")
        else:
            self._current_id = next_id

        self._pending_affinity = affinity_delta
        return affinity_delta

    def consume_affinity(self) -> int:
        delta = self._pending_affinity
        self._pending_affinity = 0
        return delta

    # Debug 

    def __str__(self) -> str:
        state = "finished" if self._finished else f"at {self._current_id}"
        return f"DialogueManager({state}, entries={len(self._entries)})"
