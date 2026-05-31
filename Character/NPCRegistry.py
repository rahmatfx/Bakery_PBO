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

        # Cycling state
        self._recently_seen: list[str] = []     
        self._max_recent: int = 3              

        self._load_all()

    # Load

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

    # Query 

    def get(self, npc_id: str) -> NPCData | None:
        return self.npcs.get(npc_id)

    def random(self) -> NPCData:
        if not self.npcs:
            raise RuntimeError("[NPCRegistry] No NPCs loaded!")

        # Kalau cuma 1 NPC, gak ada pilihan
        if len(self.npcs) == 1:
            npc_id = list(self.npcs.keys())[0]
            self._mark_seen(npc_id)
            return self.npcs[npc_id]

        # Filter out recently seen
        available = {
            nid: npc for nid, npc in self.npcs.items()
            if nid not in self._recently_seen
        }

        # Kalau semua sudah recently seen, reset dan pakai semua
        if not available:
            print("[NPCRegistry] All NPCs recently seen, resetting cycle")
            available = dict(self.npcs)

        # Weighted random
        # Weight = max_affinity - current_affinity + 1
        # Jadi affinity 0 → weight tinggi, affinity 50 → weight rendah
        # +1 supaya yang affinity tinggi tetap bisa muncul
        weights = []
        npc_list = list(available.values())

        for npc in npc_list:
            affinity = self._affinity.get(npc.id, 0)
            # Semakin rendah affinity, semakin besar weight
            weight = max(1, 50 - affinity)
            weights.append(weight)

        # random.choices dengan weights
        chosen = random.choices(npc_list, weights=weights, k=1)[0]

        self._mark_seen(chosen.id)
        print(f"[NPCRegistry] Selected: {chosen.id} (affinity: "
              f"{self._affinity.get(chosen.id, 0)}, "
              f"recently_seen: {self._recently_seen})")

        return chosen

    def _mark_seen(self, npc_id: str) -> None:
        """Tandai NPC sebagai baru muncul."""
        if npc_id in self._recently_seen:
            self._recently_seen.remove(npc_id)
        self._recently_seen.append(npc_id)

        if len(self._recently_seen) > self._max_recent:
            self._recently_seen = self._recently_seen[-self._max_recent:]

    def all_ids(self) -> list[str]:
        return list(self.npcs.keys())

    def count(self) -> int:
        return len(self.npcs)

    # Affinity

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

    # Load

    def get_all_affinity(self) -> dict[str, int]:
        return dict(self._affinity)

    def load_affinity(self, affinity_data: dict[str, int]) -> None:
        self._affinity = dict(affinity_data)
        print(f"[NPCRegistry] Loaded affinity for {len(self._affinity)} NPCs")