from __future__ import annotations
import pygame
import Constant
from Enum.CashierState import CashierState


class CashierRenderContext:
    __slots__ = (
        "state",
        "npc",
        "npc_x",
        "npc_offset",        
        "npc_sprite",        
        "emoji_scale",
        "background",        
        "heart_img",          
        "cake",
        "emoji_popup_done",
    )

    def __init__(self) -> None:
        self.state      = CashierState.HIDDEN
        self.npc        = None
        self.npc_x      = 0.0
        self.npc_offset = (0.0, 0.0, 1.0)
        self.npc_sprite = None
        self.emoji_scale = 1.0
        self.background = None
        self.heart_img  = None
        self.cake       = None
        self.emoji_popup_done = False 


class CashierRenderer:

    def __init__(self) -> None:
        self._font: pygame.font.Font | None          = None
        self._font_affinity: pygame.font.Font | None = None
        self._text_cache: dict[str, pygame.Surface]  = {}
        self._submit_btn_rect: pygame.Rect | None    = None


    def init_fonts(self) -> None:
        self._font          = pygame.font.SysFont(Constant.FONT_NAME, Constant.FONT_BODY_SIZE)
        self._font_affinity = pygame.font.SysFont(Constant.FONT_NAME,
                                                   Constant.AFFINITY_FONT_SIZE, bold=True)
        self._text_cache.clear()

    def clear_text_cache(self) -> None:
        self._text_cache.clear()


    def render(self,
               screen: pygame.Surface,
               ctx: CashierRenderContext,
               order_ui,
               dialogue_box,
               cake_selection_ui,
               minigame) -> None:
        
        self._render_background(screen, ctx.background)
        self._render_npc(screen, ctx)
        order_ui.render(screen)
        self._render_affinity(screen, ctx)

        if ctx.state == CashierState.DIALOGUE:
            dialogue_box.render(screen)

        if ctx.state == CashierState.CAKE_SELECT:
            cake_selection_ui.render(screen)

        if ctx.state == CashierState.ORDER_ACTIVE:
            minigame.render(screen, ctx.npc_x)

            if ctx.cake and ctx.cake.is_complete():
                self._render_cake_preview(screen, ctx.cake)


        if ctx.state == CashierState.REACTING and ctx.emoji_popup_done:
            self._render_hint(screen, "Click to continue...",
                              Constant.NPC_Y + Constant.NPC_HEIGHT + Constant.HINT_CLICK_OFFSET_Y)

    def _render_cake_preview(self, screen: pygame.Surface, cake) -> None:
        cake_center = (Constant.SCREEN_WIDTH - 1000, Constant.SCREEN_HEIGHT - 150)
        cake.render_cake(screen, center=cake_center)

        btn_rect = pygame.Rect(0, 0, 200, 50)
        btn_rect.centerx = cake_center[0]
        btn_rect.top = cake_center[1] + 100

        pygame.draw.rect(screen, (80, 180, 80), btn_rect, border_radius=10)
        if self._font:
            label = self._font.render("Submit Cake!", True, (255, 255, 255))
            screen.blit(label, label.get_rect(center=btn_rect.center))

        self._submit_btn_rect = btn_rect

    # Background 

    def _render_background(self,
                            screen: pygame.Surface,
                            background: pygame.Surface | None) -> None:
        if background:
            screen.blit(background, (0, 0))
        else:
            content = pygame.Rect(0, Constant.NAV_BAR_HEIGHT,
                                  Constant.SCREEN_WIDTH,
                                  Constant.SCREEN_HEIGHT - Constant.NAV_BAR_HEIGHT)
            pygame.draw.rect(screen, Constant.COLOR_CASHIER_FALLBACK_BG, content)

    # NPC sprite

    def _render_npc(self,
                    screen: pygame.Surface,
                    ctx: CashierRenderContext) -> None:
        if not ctx.npc or ctx.state == CashierState.HIDDEN:
            return

        dx, dy, scale = ctx.npc_offset
        npc_x = int(ctx.npc_x + dx)
        npc_y = int(Constant.NPC_Y + dy)

        sprite = ctx.npc_sprite
        if sprite:
            if scale != 1.0:
                w = max(1, int(Constant.NPC_WIDTH  * scale))
                h = max(1, int(Constant.NPC_HEIGHT * scale))
                scaled = pygame.transform.scale(sprite, (w, h))
                ox = (Constant.NPC_WIDTH  - w) // 2
                oy = (Constant.NPC_HEIGHT - h) // 2
                screen.blit(scaled, (npc_x + ox, npc_y + oy))
            else:
                screen.blit(sprite, (npc_x, npc_y))
        else:
            self._render_npc_fallback(screen, ctx, npc_x, npc_y)

    def _render_npc_fallback(self,
                              screen: pygame.Surface,
                              ctx: CashierRenderContext,
                              npc_x: int,
                              npc_y: int) -> None:
        npc_rect = pygame.Rect(npc_x, npc_y, Constant.NPC_WIDTH, Constant.NPC_HEIGHT)
        shadow   = npc_rect.move(Constant.SHADOW_OFFSET, Constant.SHADOW_OFFSET)
        pygame.draw.rect(screen, (0, 0, 0), shadow, border_radius=12)
        pygame.draw.rect(screen, Constant.COLOR_WARM_BROWN, npc_rect, border_radius=12)
        pygame.draw.rect(screen, Constant.COLOR_DARK_BROWN, npc_rect, 2, border_radius=12)

        if ctx.npc and self._font:
            name_surf = self._cached_text(ctx.npc.name, Constant.COLOR_WHITE)
            screen.blit(name_surf,
                        name_surf.get_rect(centerx=npc_rect.centerx, y=npc_y + 10))
            expr_surf = self._cached_text(f"[{ctx.npc.expression}]",
                                          Constant.COLOR_WHITE)
            screen.blit(expr_surf,
                        expr_surf.get_rect(centerx=npc_rect.centerx, y=npc_y + 50))

    # Affinity panel 

    def _render_affinity(self,
                          screen: pygame.Surface,
                          ctx: CashierRenderContext) -> None:
        if not ctx.npc or ctx.state == CashierState.HIDDEN:
            return

        bar_x = int(ctx.npc_x) + Constant.AFFINITY_BAR_OFFSET_X
        bar_y = (Constant.NPC_Y
                 - Constant.AFFINITY_HEART_SIZE
                 - Constant.AFFINITY_BAR_OFFSET_Y)

        heart_size = Constant.AFFINITY_HEART_SIZE
        padding    = Constant.AFFINITY_PANEL_PADDING

        affinity_surf = None
        if self._font_affinity:
            affinity_surf = self._font_affinity.render(
                str(ctx.npc.affinity), True, Constant.COLOR_DARK_BROWN)

        text_w  = affinity_surf.get_width() if affinity_surf else 30
        panel_w = heart_size + Constant.AFFINITY_TEXT_GAP + text_w + padding * 2
        panel_h = heart_size + padding * 2

        panel_rect  = pygame.Rect(bar_x - padding, bar_y - padding, panel_w, panel_h)
        shadow_rect = panel_rect.move(Constant.AFFINITY_SHADOW_OFFSET,
                                       Constant.AFFINITY_SHADOW_OFFSET)

        pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=8)
        pygame.draw.rect(screen, Constant.COLOR_BG_CREAM, panel_rect, border_radius=8)
        pygame.draw.rect(screen, Constant.COLOR_WARM_BROWN, panel_rect, 2,
                          border_radius=8)

        if ctx.heart_img:
            screen.blit(ctx.heart_img, (bar_x, bar_y))
        else:
            r = pygame.Rect(
                bar_x + Constant.AFFINITY_SHADOW_OFFSET,
                bar_y + Constant.AFFINITY_SHADOW_OFFSET,
                heart_size - Constant.SHADOW_OFFSET,
                heart_size - Constant.SHADOW_OFFSET,
            )
            pygame.draw.circle(screen, Constant.COLOR_HEART_RED,
                               r.center,
                               heart_size // 2 - Constant.AFFINITY_SHADOW_OFFSET)

        if affinity_surf:
            screen.blit(affinity_surf,
                        (bar_x + heart_size + Constant.AFFINITY_TEXT_GAP,
                         bar_y + (heart_size - affinity_surf.get_height()) // 2))

    # Hint text 

    def _render_hint(self,
                     screen: pygame.Surface,
                     text: str,
                     y: int) -> None:
        if not self._font:
            return
        surf = self._cached_text(text, Constant.COLOR_DARK_BROWN)
        screen.blit(surf, (Constant.NPC_X, y))

    # Util

    def _cached_text(self, text: str, color: tuple) -> pygame.Surface:
        key = f"{text}_{color}"
        if key not in self._text_cache and self._font:
            self._text_cache[key] = self._font.render(text, True, color)
        return self._text_cache.get(key, pygame.Surface((0, 0)))