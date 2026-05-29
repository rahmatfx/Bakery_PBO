import json
import glob 
import os
import random
from Character.NPCData import NPCData


class NPCRegistry:
    def __init__(self, data_dir: str):
        self.data_dir: str = data_dir
        self.npcs: dict[str, NPCData] = {}
        self._affinity: dict[str, int] = {}
        self._load_all()



    def _load_all(self) -> None:
        pattern = os.path.join(self.data_dir, "npc_*.json")
        files = glob.glob(pattern)

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    raw = json.load(f)

                npc = NPCData(
                    id=raw["id"],
                    name=raw["name"],
                    personality=raw.get("personality", ""),
                    preferences=raw.get("preferences", {}),
                    dislikes=raw.get("dislikes", {}),
                    dialogues=raw.get("dialogues", {}),
                    affinity_thresholds=raw.get("affinity_thresholds", {}),
                    assets=raw.get("assets", {}),
                )

                self.npcs[npc.id] = npc
                print(f"[NPCRegistry] Loaded: {npc.id} ({npc.name})")

            except (json.JSONDecodeError, KeyError) as e:
                print(f"[NPCRegistry] ERROR loading {file_path}: {e}")

        print(f"[NPCRegistry] Total NPCs loaded: {len(self.npcs)}")


    # / query for npc
    def get(self, npc_id: str) -> NPCData | None:
        return self.npcs.get(npc_id)

    def random(self) -> NPCData:
        if not self.npcs:
            raise RuntimeError("[NPCRegistry] No NPCs loaded!")
        return random.choice(list(self.npcs.values()))

    def all_ids(self) -> list[str]:
        return list(self.npcs.keys())

    def count(self) -> int:
        return len(self.npcs)
    

    # for affinity
    def get_affinity(self, npc_id: str) -> int:
        return self._affinity.get(npc_id, 0)

    def set_affinity(self, npc_id: str, value: int) -> None:
        self._affinity[npc_id] = value
        print(f"[NPCRegistry] {npc_id} affinity set to {value}")

    def change_affinity(self, npc_id: str, delta: int) -> int:
        new_value = self._affinity.get(npc_id, 0) + delta
        self._affinity[npc_id] = new_value
        print(f"[NPCRegistry] {npc_id} affinity: {new_value} "
              f"({'+' if delta >= 0 else ''}{delta})")
        return new_value

    def get_affinity_level(self, npc_id: str) -> int:
        npc = self.npcs.get(npc_id)
        if not npc:
            return 0
        return npc.get_level_for_affinity(self.get_affinity(npc_id))
    
    # for 

    def get_all_affinity(self) -> dict[str, int]:
        return dict(self._affinity)

    def load_affinity(self, affinity_data: dict[str, int]) -> None:
        self._affinity = dict(affinity_data)
        print(f"[NPCRegistry] Loaded affinity for {len(self._affinity)} NPCs")

