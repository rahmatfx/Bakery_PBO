from dataclasses import dataclass, field

@dataclass
class NPCData :

    id : str
    name : str
    personality : str
    preferences : dict = field(default_factory=dict)
    dislikes: dict = field(default_factory=dict)     
    dialogues : dict = field(default_factory=dict)
    affinity_thresholds : dict = field(default_factory=dict)
    assets : dict = field(default_factory=dict)

    def get_preferred_flavors(self) -> list[str] :
        return self.preferences.get("flavors", [])
    
    def get_preferred_molds(self) -> list[str] :
        return self.preferences.get("molds", [])
    
    def get_preferred_decorations(self) -> list[str] :
        return self.preferences.get("decorations", [])
    
    def get_disliked_flavors(self) -> list[str]:
        return self.dislikes.get("flavors", [])

    def get_disliked_molds(self) -> list[str]:
        return self.dislikes.get("molds", [])

    def get_disliked_decorations(self) -> list[str]:
        return self.dislikes.get("decorations", [])


    def get_dialogues_for_level(self, level: int) -> list[dict]:
        return self.dialogues.get(f"level_{level}",[])
    
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
    
    def get_sprite_path(self) -> str:
        return self.assets.get("sprite", "")
    
    def get_emoji_happy_path(self) -> str:
        return self.assets.get("emoji_happy", "")

    def get_emoji_angry_path(self) -> str:
        return self.assets.get("emoji_angry", "")


    def __str__(self) -> str:
        return (f"NPCData(id={self.id}, name={self.name}, "
                f"personality={self.personality})")
