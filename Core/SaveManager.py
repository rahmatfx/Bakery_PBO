import json
import os


class SaveManager:

    def __init__(self, save_path: str):
        self.save_path: str = save_path

    def load(self) -> dict:
        if not os.path.exists(self.save_path):
            print(f"[SaveManager] No save file found: {self.save_path}")
            return {}

        try:
            with open(self.save_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            affinity = data.get("affinity", {})
            print(f"[SaveManager] Loaded save: {len(affinity)} NPC affinities")
            return data

        except (json.JSONDecodeError, IOError) as e:
            print(f"[SaveManager] ERROR loading save: {e}")
            return {}

    def load_affinity(self) -> dict[str, int]:
        data = self.load()
        return data.get("affinity", {})

    def save(self, data: dict) -> None:
        save_dir = os.path.dirname(self.save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)

        try:
            with open(self.save_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            affinity = data.get("affinity", {})
            print(f"[SaveManager] Saved: {len(affinity)} NPC affinities")

        except IOError as e:
            print(f"[SaveManager] ERROR saving: {e}")

    def save_affinity(self, affinity: dict[str, int]) -> None:
        self.save({"affinity": affinity})

    # Dialogue tracker save/load

    def save_dialogue_tracker(self, tracker_data: dict) -> None:
        data = self.load()
        if not data:
            data = {}
        data["dialogue_tracker"] = tracker_data
        self.save(data)

    def load_dialogue_tracker(self) -> dict:
        data = self.load()
        return data.get("dialogue_tracker", {})

    def has_save(self) -> bool:
        return os.path.exists(self.save_path)

    def delete_save(self) -> None:
        if os.path.exists(self.save_path):
            os.remove(self.save_path)
            print("[SaveManager] Save file deleted")