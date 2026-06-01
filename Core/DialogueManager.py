from dataclasses import dataclass, field


@dataclass
class AdvanceResult:

    affinity_delta: int = 0
    expression: str | None = None
    emoji: str | None = None


class DialogueManager:

    def __init__(self):
        self._entries: dict[str, dict] = {}
        self._current_id: str | None = None
        self._finished: bool = False

    def start(self, entries: list[dict]) -> None:
        self._entries = {
            entry["id"]: entry
            for entry in entries
            if "id" in entry
        }
        self._current_id = entries[0]["id"] if entries else None
        self._finished = False

        print(f"[DialogueManager] Started, entries: {len(self._entries)}, "
              f"first: {self._current_id}")

    def reset(self) -> None:
        self._entries = {}
        self._current_id = None
        self._finished = False

    # Query

    def get_current(self) -> dict | None:
        if not self._current_id:
            return None
        return self._entries.get(self._current_id)

    def get_current_choices(self) -> list[dict]:
        entry = self.get_current()
        return entry.get("choices", []) if entry else []

    def is_finished(self) -> bool:
        return self._finished

    # Advance 

    def advance(self, choice_index: int = -1) -> AdvanceResult:

        if self._finished:
            return AdvanceResult()

        entry = self.get_current()
        if not entry:
            self._finished = True
            return AdvanceResult()

        choices = entry.get("choices", [])
        result = AdvanceResult()
        next_id: str | None = None

        if choices and 0 <= choice_index < len(choices):
            choice = choices[choice_index]
            result.affinity_delta = choice.get("affinity", 0)
            result.expression = choice.get("expression")
            result.emoji = choice.get("emoji")
            next_id = choice.get("next")

            print(f"[DialogueManager] Choice {choice_index}: "
                  f"affinity {'+' if result.affinity_delta >= 0 else ''}{result.affinity_delta}, "
                  f"expression={result.expression}, emoji={result.emoji}")
        else:
            next_id = entry.get("next")
            print(f"[DialogueManager] Linear advance → {next_id}")

        if next_id is None:
            self._finished = True
            self._current_id = None
            print("[DialogueManager] Dialogue finished")
        else:
            self._current_id = next_id

        return result

    # Debug

    def __str__(self) -> str:
        state = "finished" if self._finished else f"at {self._current_id}"
        return f"DialogueManager({state}, entries={len(self._entries)})"