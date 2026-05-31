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

        # ── auto-hide ──
        self._display_duration: float = Constant.EMOJI_POPUP_DURATION  # detik
        self._display_timer: float = 0.0
        self._phase: str = "idle"  # "idle" | "floating" | "displaying" | "fading"

        # ── fade out ──
        self._fade_duration: float = Constant.EMOJI_POPUP_FADE_DURATION
        self._fade_timer: float = 0.0
        self._alpha: int = 255

        # font cache
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
        self._phase = "floating"
        self._display_timer = 0.0
        self._fade_timer = 0.0
        self._alpha = 255

    def update(self, delta_time: float) -> None:
        if not self._active:
            return

        if self._phase == "floating":
            self._y -= self._float_speed * delta_time * 60  # frame-rate independent
            if self._y <= self._target_y:
                self._y = float(self._target_y)
                self._phase = "displaying"
                self._display_timer = 0.0

        elif self._phase == "displaying":
            self._display_timer += delta_time
            if self._display_timer >= self._display_duration:
                self._phase = "fading"
                self._fade_timer = 0.0

        elif self._phase == "fading":
            self._fade_timer += delta_time
            progress = min(1.0, self._fade_timer / self._fade_duration)
            self._alpha = max(0, int(255 * (1.0 - progress)))
            if self._alpha <= 0:
                self.hide()

    def render(self, screen: pygame.Surface, scale: float = 1.0) -> None:
        if not self._active:
            return

        if self._surface:
            self._render_surface(screen, scale)
        else:
            self._render_fallback(screen, scale)

    def is_done(self) -> bool:
        return self._done

    def is_visible(self) -> bool:
        return self._active

    def hide(self) -> None:
        self._active = False
        self._done = True
        self._surface = None
        self._alpha = 255
        self._phase = "idle"

    # ── Render ──

    def _render_surface(self, screen: pygame.Surface, scale: float) -> None:
        w = max(1, int(self._width * scale))
        h = max(1, int(self._height * scale))

        scaled = pygame.transform.scale(self._surface, (w, h))

        # Apply alpha (fade out)
        if self._alpha < 255:
            scaled.set_alpha(self._alpha)

        offset_x = (self._width - w) // 2
        offset_y = (self._height - h) // 2
        screen.blit(scaled, (self._x + offset_x,
                              int(self._y) + offset_y))

    def _render_fallback(self, screen: pygame.Surface, scale: float) -> None:
        w = max(1, int(self._width * scale))
        h = max(1, int(self._height * scale))
        if w <= 0 or h <= 0:
            return

        # Buat surface terpisah untuk alpha support
        fallback_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        alpha_color = (*self._fallback_color, self._alpha)
        rect = pygame.Rect(0, 0, w, h)
        pygame.draw.rect(fallback_surf, alpha_color, rect, border_radius=50)

        font = self._get_font(max(10, min(w, h) // 3))
        text_surf = font.render(self._fallback_text, True, Constant.COLOR_WHITE)
        if self._alpha < 255:
            text_surf.set_alpha(self._alpha)
        fallback_surf.blit(text_surf, text_surf.get_rect(center=rect.center))

        screen.blit(fallback_surf, (self._x, int(self._y)))

    # ── Font Cache ──

    def _get_font(self, size: int) -> pygame.font.Font:
        if size not in self._font_cache:
            self._font_cache[size] = pygame.font.SysFont(
                Constant.FONT_NAME, size)
        return self._font_cache[size]