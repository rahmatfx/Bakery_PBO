import json
import pygame
import Constant


class ExpressionSet:

    def __init__(self, config_path: str = Constant.EXPRESSION_CONFIG):
        self._surfaces: dict[str, pygame.Surface] = {}
        self._fallback: dict[str, tuple[str, tuple]] = {}
        self._expression_config: dict = {}
        self._emoji_paths: dict[str, str] = {}

        self._load_config(config_path)
        self._load_globals()

    # ── Config ──

    def _load_config(self, path: str) -> None:
        try:
            with open(path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except FileNotFoundError:
            print(f"[ExpressionSet] Config not found: {path}, using empty config")
            return

        self._expression_config = cfg.get("expressions", {})

        # Build fallback dict dari config
        for name, data in self._expression_config.items():
            text = data.get("fallback_text", "?")
            color = tuple(data.get("fallback_color", [200, 200, 200]))
            self._fallback[name] = (text, color)

        # Global emoji paths dari config
        self._emoji_paths = cfg.get("global_emojis", {})

    # ── Load ──

    def _load_globals(self) -> None:
        for name, path in self._emoji_paths.items():
            surface = self._load_and_scale(path)
            if surface:
                self._surfaces[name] = surface
                print(f"[ExpressionSet] Emoji global '{name}' loaded: {path}")
            else:
                print(f"[ExpressionSet] Emoji global '{name}' NOT found: {path}")

    # ── Query ──

    def get_surface(self, name: str) -> pygame.Surface | None:
        return self._surfaces.get(name)

    def get_fallback(self, name: str) -> tuple[str, tuple]:
        return self._fallback.get(name, ("?", (200, 200, 200)))

    def get_expression_config(self, name: str) -> dict:
        return self._expression_config.get(name, {})

    def get_animation(self, name: str) -> str | None:
        return self._expression_config.get(name, {}).get("animation")

    def get_sfx(self, name: str) -> str | None:
        return self._expression_config.get(name, {}).get("sfx")

    # ── Helper ──

    @staticmethod
    def _load_and_scale(path: str) -> pygame.Surface | None:
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(img, (Constant.EXPR_WIDTH, Constant.EXPR_HEIGHT))
        except Exception:
            return None