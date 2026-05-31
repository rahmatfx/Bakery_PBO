import pygame
import Constant


class EmojiPopup:

    def __init__(self):
        self._active: bool = False
        self._done: bool = False

        # display
        self._surface: pygame.Surface | None = None
        self._fallback_text: str = ""
        self._fallback_color: tuple = (200, 200, 200)

        # position
        self._x: int = 0
        self._y: float = 0.0
        self._target_y: int = 0
        self._float_speed: float = Constant.EMOJI_POPUP_SPEED

        # size
        self._width: int = Constant.EXPR_WIDTH
        self._height: int = Constant.EXPR_HEIGHT

        # font cache for fallback rendering
        self._font_cache: dict[int, pygame.font.Font] = {}

    # ── Public ──

    def show(self, surface: pygame.Surface | None,
             fallback_text: str, fallback_color: tuple,
             center_x: int, anchor_y: int) -> None:
        self._surface = surface
        self._fallback_text = fallback_text
        self._fallback_color = fallback_color

        self._x = center_x - self._width // 2
        self._target_y = anchor_y - self._height - Constant.EMOJI_POPUP_OFFSET_Y
        self._y = float(anchor_y + Constant.EMOJI_POPUP_OFFSET_Y)

        self._active = True
        self._done = False

    def update(self, delta_time: float) -> None:
        if not self._active or self._done:
            return

        self._y -= self._float_speed
        if self._y <= self._target_y:
            self._y = float(self._target_y)
            self._done = True

    def render(self, screen: pygame.Surface, scale: float = 1.0) -> None:
        if not self._active:
            return

        if self._surface:
            self._render_surface(screen, scale)
        else:
            self._render_fallback(screen, scale)

    def is_done(self) -> bool:
        return self._done

    def hide(self) -> None:
        self._active = False
        self._done = False
        self._surface = None

    # ── Render ──

    def _render_surface(self, screen: pygame.Surface, scale: float) -> None:
        if scale != 1.0:
            w = max(1, int(self._width * scale))
            h = max(1, int(self._height * scale))
            scaled = pygame.transform.scale(self._surface, (w, h))
            offset_x = (self._width - w) // 2
            offset_y = (self._height - h) // 2
            screen.blit(scaled, (self._x + offset_x,
                                  int(self._y) + offset_y))
        else:
            screen.blit(self._surface, (self._x, int(self._y)))

    def _render_fallback(self, screen: pygame.Surface, scale: float) -> None:
        w = max(1, int(self._width * scale))
        h = max(1, int(self._height * scale))
        if w <= 0 or h <= 0:
            return

        rect = pygame.Rect(self._x, int(self._y), w, h)
        pygame.draw.rect(screen, self._fallback_color, rect,
                          border_radius=50)

        font = self._get_font(max(10, min(w, h) // 3))
        text_surf = font.render(self._fallback_text, True,
                                 Constant.COLOR_WHITE)
        screen.blit(text_surf, text_surf.get_rect(center=rect.center))

    # ── Font Cache ──

    def _get_font(self, size: int) -> pygame.font.Font:
        if size not in self._font_cache:
            self._font_cache[size] = pygame.font.SysFont(
                Constant.FONT_NAME, size)
        return self._font_cache[size]
