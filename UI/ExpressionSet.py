import pygame
import Constant


class ExpressionSet:

    # fallback text & color per expression
    _FALLBACK: dict[str, tuple[str, tuple]] = {
        "happy":   ("HAPPY", Constant.COLOR_EXPR_HAPPY_FALLBACK),
        "angry":   ("ANGRY", Constant.COLOR_EXPR_ANGRY_FALLBACK),
        "neutral": ("...",   Constant.COLOR_EXPR_NEUTRAL_FALLBACK),
    }

    # default image paths (shared fallback assets)
    _DEFAULT_PATHS: dict[str, str] = {
        "happy": Constant.NPC_EMOJI_HAPPY,
        "angry": Constant.NPC_EMOJI_ANGRY,
    }

    def __init__(self):
        self._defaults: dict[str, pygame.Surface] = {}
        self._expressions: dict[str, pygame.Surface] = {}
        self._cache: dict[str, dict[str, pygame.Surface]] = {}
        self._load_defaults()

    # ── Load ──

    def _load_defaults(self) -> None:
        for name, path in self._DEFAULT_PATHS.items():
            surface = self._load_and_scale(path)
            if surface:
                self._defaults[name] = surface
        self._expressions = dict(self._defaults)

    def load_from_assets(self, assets: dict, npc_id: str = "") -> None:
        # cache hit
        if npc_id and npc_id in self._cache:
            self._expressions = dict(self._cache[npc_id])
            return

        # start from defaults, overlay npc-specific
        self._expressions = dict(self._defaults)

        for key, path in assets.items():
            if not key.startswith("emoji_"):
                continue
            expr_name = key.replace("emoji_", "")
            surface = self._load_and_scale(path)
            if surface:
                self._expressions[expr_name] = surface

        # cache for this npc
        if npc_id:
            self._cache[npc_id] = dict(self._expressions)

    # ── Query ──

    def get_surface(self, name: str) -> pygame.Surface | None:
        return self._expressions.get(name)

    def get_fallback(self, name: str) -> tuple[str, tuple]:
        return self._FALLBACK.get(name, ("?", (200, 200, 200)))

    # ── Helper ──

    @staticmethod
    def _load_and_scale(path: str) -> pygame.Surface | None:
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (Constant.EXPR_WIDTH,
                                                  Constant.EXPR_HEIGHT))
        except Exception:
            return None
