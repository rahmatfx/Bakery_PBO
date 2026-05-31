class DialogueTracker:

    def __init__(self):
        self._next_dialogue: dict[str, str] = {}   # npc_id → "level_X.mood.variant"
        self._current_mood: dict[str, str] = {}     # npc_id → mood
        self._seen_variants: dict[str, set] = {}    # "npc_level_mood" → set of seen variants

    def set_next(self, npc_id: str, path: str) -> None:
        self._next_dialogue[npc_id] = path

    def set_mood(self, npc_id: str, mood: str) -> None:
        self._current_mood[npc_id] = mood

    def get_mood(self, npc_id: str) -> str:
        return self._current_mood.get(npc_id, "neutral")

    def resolve_next(self, npc_id: str, level: int,
                     available_moods: list[str],
                     get_variants_fn) -> tuple[str, str]:
        # 1. Kalau ada set_next dari dialogue choice sebelumnya
        if npc_id in self._next_dialogue:
            path = self._next_dialogue.pop(npc_id)
            parts = path.split(".")
            if len(parts) == 3:
                mood = parts[1]
                variant = parts[2]
                self._mark_seen(npc_id, level, mood, variant)
                return mood, variant

        # 2. Persist mood + cycle variant
        current_mood = self._current_mood.get(npc_id, "neutral")
        if current_mood not in available_moods and available_moods:
            current_mood = available_moods[0]

        variants = get_variants_fn(current_mood) if current_mood in available_moods else []
        if not variants and available_moods:
            current_mood = available_moods[0]
            variants = get_variants_fn(current_mood)
        if not variants:
            return "neutral", "a"

        # Cari variant yang belum dilihat
        key = f"{npc_id}_{level}_{current_mood}"
        seen = self._seen_variants.get(key, set())
        unseen = [v for v in variants if v not in seen]

        if unseen:
            variant = unseen[0]
        else:
            # Semua udah dilihat, reset cycling
            self._seen_variants[key] = set()
            variant = variants[0]

        self._mark_seen(npc_id, level, current_mood, variant)
        return current_mood, variant

    def _mark_seen(self, npc_id: str, level: int, mood: str, variant: str) -> None:
        key = f"{npc_id}_{level}_{mood}"
        if key not in self._seen_variants:
            self._seen_variants[key] = set()
        self._seen_variants[key].add(variant)

    # Save/Load

    def get_save_data(self) -> dict:
        return {
            "next_dialogue": dict(self._next_dialogue),
            "current_mood": dict(self._current_mood),
            "seen_variants": {k: list(v) for k, v in self._seen_variants.items()}
        }

    def load_save_data(self, data: dict) -> None:
        self._next_dialogue = data.get("next_dialogue", {})
        self._current_mood = data.get("current_mood", {})
        self._seen_variants = {
            k: set(v) for k, v in data.get("seen_variants", {}).items()
        }