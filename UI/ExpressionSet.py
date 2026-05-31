import pygame
import Constant


class ExpressionSet:

    # Fallback kalau file gambar tidak ditemukan
    _FALLBACK: dict[str, tuple[str, tuple]] = {
        "happy":   ("HAPPY", Constant.COLOR_EXPR_HAPPY_FALLBACK),
        "angry":   ("ANGRY", Constant.COLOR_EXPR_ANGRY_FALLBACK),
        "neutral": ("...",   Constant.COLOR_EXPR_NEUTRAL_FALLBACK),
    }

    # Path gambar emoji global — diambil dari Constant.py
    _GLOBAL_EMOJI_PATHS: dict[str, str] = {
        "happy": Constant.NPC_EMOJI_HAPPY,   # Assets/emoji_happy.png
        "angry": Constant.NPC_EMOJI_ANGRY,   # Assets/emoji_angry.png
    }

    def __init__(self):
        self._surfaces: dict[str, pygame.Surface] = {}
        self._load_globals()

    # ── Load ──

    def _load_globals(self) -> None:
        """Load global emoji images — shared across all NPCs."""
        for name, path in self._GLOBAL_EMOJI_PATHS.items():
            surface = self._load_and_scale(path)
            if surface:
                self._surfaces[name] = surface
                print(f"[ExpressionSet] Emoji global '{name}' loaded: {path}")
            else:
                print(f"[ExpressionSet] Emoji global '{name}' NOT found: {path} (will use fallback)")

    # ── Query ──

    def get_surface(self, name: str) -> pygame.Surface | None:
        return self._surfaces.get(name)

    def get_fallback(self, name: str) -> tuple[str, tuple]:
        return self._FALLBACK.get(name, ("?", (200, 200, 200)))

    # ── Helper ──

    @staticmethod
    def _load_and_scale(path: str) -> pygame.Surface | None:
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (Constant.EXPR_WIDTH, Constant.EXPR_HEIGHT))
        except Exception:
            return None