from dataclasses import dataclass, field


@dataclass
class NPCData:
    id: str
    name: str
    personality: str
    preferences: dict = field(default_factory=dict)
    dislikes: dict = field(default_factory=dict)
    dialogues: dict = field(default_factory=dict)
    affinity_thresholds: dict = field(default_factory=dict)
    assets: dict = field(default_factory=dict)

    # ── Preference helpers ──

    def get_preferred_flavors(self) -> list[str]:
        return self.preferences.get("flavors", [])

    def get_preferred_molds(self) -> list[str]:
        return self.preferences.get("molds", [])

    def get_preferred_decorations(self) -> list[str]:
        return self.preferences.get("decorations", [])

    def get_disliked_flavors(self) -> list[str]:
        return self.dislikes.get("flavors", [])

    def get_disliked_molds(self) -> list[str]:
        return self.dislikes.get("molds", [])

    def get_disliked_decorations(self) -> list[str]:
        return self.dislikes.get("decorations", [])

    # ── Sprite helpers (GENERIC — supports ANY expression) ──

    def get_sprite_path(self) -> str:
        return self.assets.get("sprite", "")

    def get_expression_sprite_path(self, expression: str) -> str:
        """Get sprite path for ANY expression — reads from assets.expressions dict."""
        expressions = self.assets.get("expressions", {})
        return expressions.get(expression, "")

    def get_all_expression_names(self) -> list[str]:
        """Return list of all expression names defined for this NPC."""
        return list(self.assets.get("expressions", {}).keys())

    # ── Dialogue helpers ──

    def get_moods_for_level(self, level: int) -> list[str]:
        level_data = self.dialogues.get(f"level_{level}")
        if level_data is None:
            return []
        if isinstance(level_data, list):
            return ["neutral"]
        if isinstance(level_data, dict):
            return list(level_data.keys())
        return []

    def get_variants_for_level_mood(self, level: int, mood: str) -> list[str]:
        level_data = self.dialogues.get(f"level_{level}")
        if level_data is None:
            return []
        if isinstance(level_data, list):
            return ["a"] if mood == "neutral" else []
        if isinstance(level_data, dict):
            mood_data = level_data.get(mood, {})
            if isinstance(mood_data, dict):
                return list(mood_data.keys())
            if isinstance(mood_data, list):
                return ["a"]
        return []

    def get_dialogue_entries(self, level: int, mood: str, variant: str) -> list[dict]:
        level_data = self.dialogues.get(f"level_{level}")
        if level_data is None:
            return []
        if isinstance(level_data, list):
            return level_data if mood == "neutral" and variant == "a" else []
        if isinstance(level_data, dict):
            mood_data = level_data.get(mood, {})
            if isinstance(mood_data, dict):
                return mood_data.get(variant, [])
            if isinstance(mood_data, list):
                return mood_data if variant == "a" else []
        return []

    def get_dialogues_for_level(self, level: int) -> list[dict]:
        return self.get_dialogue_entries(level, "neutral", "a")

    # ── Affinity thresholds ──

    def get_level_for_affinity(self, affinity: int) -> int:
        level = 0
        for key, threshold in self.affinity_thresholds.items():
            if key.startswith("level_"):
                try:
                    lvl = int(key.split("_")[1])
                    if affinity >= threshold and lvl > level:
                        level = lvl
                except (ValueError, IndexError):
                    continue
        return level

    def has_ending(self) -> bool:
        return "ending" in self.affinity_thresholds

    def get_ending_threshold(self) -> int:
        return self.affinity_thresholds.get("ending", -1)

    def __str__(self) -> str:
        return (f"NPCData(id={self.id}, name={self.name}, "
                f"personality={self.personality})")