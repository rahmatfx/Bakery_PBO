from __future__ import annotations
import math
import random
import pygame
import Constant


class KeepHappyMinigame:

    def __init__(self) -> None:
        # State 
        self._running: bool       = False   
        self._prompt_active: bool = False  

        # Timing 
        self._cooldown: float     = Constant.MG_PROMPT_COOLDOWN
        self._prompt_timer: float = 0.0     
        self._prompt_count: int   = 0       

        # Animasi 
        self._bob_time: float        = 0.0  
        self._success_flash: float   = 0.0  

        # Data prompt 
        self._prompt_type: str           = ""
        self._prompt_rect: pygame.Rect | None = None

        # Output untuk Cashier
        self.just_succeeded: bool = False   

        # Font 
        self._font_small: pygame.font.Font | None = None
        self._font_bold: pygame.font.Font | None  = None

    def start(self) -> None:
        self._running       = True
        self._prompt_active = False
        self._cooldown      = Constant.MG_PROMPT_COOLDOWN
        self._prompt_timer  = 0.0
        self._prompt_count  = 0
        self._bob_time      = 0.0
        self._success_flash = 0.0
        self.just_succeeded = False

    def stop(self) -> None:
        self._running       = False
        self._prompt_active = False
        self.just_succeeded = False

    def reset(self) -> None:
        self.stop()

    # ── Update ───────────────────────────────────────────────────────────

    def update(self, delta_time: float, npc_x: float) -> None:
        # Reset flag satu-frame
        self.just_succeeded = False

        if not self._running:
            return

        # Countdown flash sukses
        if self._success_flash > 0:
            self._success_flash -= delta_time

        if self._prompt_active:
            self._bob_time    += delta_time
            self._prompt_timer -= delta_time

            if self._prompt_timer <= 0:
                # Prompt terlewat – reset cooldown
                self._prompt_active = False
                self._cooldown      = Constant.MG_PROMPT_COOLDOWN
                print("[KeepHappyMG] Prompt terlewat!")
        else:
            if self._prompt_count < Constant.MG_MAX_PROMPTS:
                self._cooldown -= delta_time
                if self._cooldown <= 0:
                    self._spawn_prompt(npc_x)

    # Handle input 

    def handle_click(self, pos: tuple[int, int]) -> bool:
        if not self._prompt_active or self._prompt_rect is None:
            return False

        if self._prompt_rect.collidepoint(pos):
            self._on_success()
            return True
        return False

    # Render

    def render(self, screen: pygame.Surface, npc_x: float) -> None:
        """Render prompt dan flash sukses ke screen."""
        self._ensure_fonts()
        self._render_prompt(screen)
        self._render_success_flash(screen, npc_x)

    def _spawn_prompt(self, npc_x: float) -> None:
        self._prompt_type = random.choice(Constant.MG_PROMPT_OPTIONS)

        prompt_x = int(npc_x) + Constant.NPC_WIDTH // 2 - Constant.MG_PROMPT_WIDTH // 2
        prompt_y = Constant.NPC_Y -50
        self._prompt_rect = pygame.Rect(
            prompt_x, prompt_y,
            Constant.MG_PROMPT_WIDTH,
            Constant.MG_PROMPT_HEIGHT,
        )

        self._prompt_active = True
        self._prompt_timer  = Constant.MG_PROMPT_DURATION
        self._bob_time      = 0.0
        self._prompt_count += 1

        print(f"[KeepHappyMG] Prompt #{self._prompt_count}: '{self._prompt_type}'")

    def _on_success(self) -> None:
        self._prompt_active  = False
        self._cooldown       = Constant.MG_PROMPT_COOLDOWN
        self._success_flash  = 0.7
        self.just_succeeded  = True   # Cashier akan baca ini

    # Rendering helpers 

    def _render_prompt(self, screen: pygame.Surface) -> None:
        if not self._prompt_active or self._prompt_rect is None:
            return

        # Animasi bob
        bob_dy = int(math.sin(self._bob_time * 4.5) * 5)
        rect   = self._prompt_rect.move(0, bob_dy)

        progress = max(0.0, self._prompt_timer / Constant.MG_PROMPT_DURATION)

        # Shadow
        pygame.draw.rect(screen, (160, 140, 120), rect.move(3, 3), border_radius=14)

        # Background bubble
        pygame.draw.rect(screen, Constant.COLOR_BG_CREAM, rect, border_radius=14)

        # Border – warna sesuai urgensi
        border_color = self._urgency_color(progress)
        pygame.draw.rect(screen, border_color, rect, 2, border_radius=14)

        # Ekor bubble (panah ke bawah)
        self._render_bubble_tail(screen, rect, border_color)

        # Label kecil "Klik sekarang!"
        if self._font_small:
            label = self._font_small.render("Klik sekarang!", True,
                                             Constant.COLOR_LIGHT_BROWN)
            screen.blit(label, label.get_rect(centerx=rect.centerx, top=rect.top + 7))

        # Teks prompt utama
        if self._font_bold:
            prompt_surf = self._font_bold.render(self._prompt_type, True,
                                                  Constant.COLOR_DARK_BROWN)
            screen.blit(prompt_surf,
                        prompt_surf.get_rect(centerx=rect.centerx, centery=rect.centery + 5))

        # Timer bar horizontal
        self._render_timer_bar(screen, rect, progress)

    @staticmethod
    def _render_bubble_tail(screen: pygame.Surface,
                             rect: pygame.Rect,
                             border_color: tuple) -> None:
        cx  = rect.centerx
        top = rect.bottom
        pts = [(cx - 8, top), (cx + 8, top), (cx, top + 10)]
        pygame.draw.polygon(screen, Constant.COLOR_BG_CREAM, pts)
        pygame.draw.lines(screen, border_color, False,
                          [pts[0], pts[2], pts[1]], 2)

    @staticmethod
    def _render_timer_bar(screen: pygame.Surface,
                          rect: pygame.Rect,
                          progress: float) -> None:
        margin = 12
        bar_h  = 7
        bar_w  = rect.width - margin * 2
        bar_x  = rect.left + margin
        bar_y  = rect.bottom - bar_h - 9

        # Background bar
        pygame.draw.rect(screen, (210, 200, 188),
                         pygame.Rect(bar_x, bar_y, bar_w, bar_h),
                         border_radius=4)

        fill_w = max(0, int(bar_w * progress))
        if fill_w > 0:
            fill_color = KeepHappyMinigame._urgency_color(progress)
            pygame.draw.rect(screen, fill_color,
                             pygame.Rect(bar_x, bar_y, fill_w, bar_h),
                             border_radius=4)

    def _render_success_flash(self, screen: pygame.Surface, npc_x: float) -> None:
        if self._success_flash <= 0 or self._font_small is None:
            return

        alpha    = min(255, int(255 * (self._success_flash / 0.7)))
        surf     = pygame.Surface((120, 30), pygame.SRCALPHA)
        surf.fill((80, 200, 80, alpha))
        pygame.draw.rect(surf, (50, 160, 50, alpha),
                         surf.get_rect(), 2, border_radius=6)

        txt = self._font_small.render(
            f"+{Constant.MG_AFFINITY_BONUS} ♥  +{int(Constant.MG_TIMER_BONUS)}s ⏱",
            True, (255, 255, 255))
        txt.set_alpha(alpha)
        surf.blit(txt, txt.get_rect(center=surf.get_rect().center))

        fx = int(npc_x) + Constant.NPC_WIDTH - 125
        fy = Constant.NPC_Y + 5
        screen.blit(surf, (fx, fy))

    # Util

    @staticmethod
    def _urgency_color(progress: float) -> tuple[int, int, int]:
        if progress > 0.55:
            return (90, 195, 90)      # hijau
        if progress > 0.25:
            return (235, 175, 45)     # kuning-oranye
        return (210, 55, 55)          # merah

    def _ensure_fonts(self) -> None:
        if self._font_small is None:
            self._font_small = pygame.font.SysFont(Constant.FONT_NAME,
                                                    Constant.FONT_SMALL_SIZE)
        if self._font_bold is None:
            self._font_bold = pygame.font.SysFont(Constant.FONT_NAME,
                                                   Constant.FONT_BODY_SIZE, bold=True)