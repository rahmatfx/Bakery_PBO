import pygame
import Constant


class OrderUI:

    def __init__(self):
        self.order = None
        self.visible = False
        self.accepted = False

        self.x = 0
        self.y = 0

        # NPC Info
        self.npc_name: str = ""
        self.npc_personality: str = ""

        self._mode: str = "npc_info"

        # Fonts
        self.font_title = pygame.font.SysFont(Constant.FONT_NAME, Constant.FONT_HEADING_SIZE)
        self.font_body = pygame.font.SysFont(Constant.FONT_NAME, Constant.FONT_BODY_SIZE)
        self.font_small = pygame.font.SysFont(Constant.FONT_NAME, Constant.FONT_SMALL_SIZE)

        self._accept_btn_rect = pygame.Rect(0, 0, 140, 40)

        self.timer_text = ""

    def set_position(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

    def set_order(self, order) -> None:
        self.order = order
        self.accepted = False

    def set_npc_info(self, name: str, personality: str) -> None:
        self.npc_name = name
        self.npc_personality = personality

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def show_npc_info(self) -> None:
        self._mode = "npc_info"
        self.visible = True

    def show_order_details(self) -> None:
        self._mode = "order_details"
        self.visible = True

    def set_timer_text(self, text: str) -> None:
        self.timer_text = text

    # Render helpers

    def _render_panel_base(self, surface: pygame.Surface, panel_w: int, panel_h: int) -> pygame.Rect:
        # Shared shadow + panel + border
        shadow_rect = pygame.Rect(
            self.x + Constant.ORDER_UI_SHADOW_OFFSET,
            self.y + Constant.ORDER_UI_SHADOW_OFFSET,
            panel_w, panel_h)
        pygame.draw.rect(surface, (0, 0, 0, Constant.ORDER_UI_SHADOW_ALPHA),
                         shadow_rect, border_radius=14)

        panel_rect = pygame.Rect(self.x, self.y, panel_w, panel_h)
        pygame.draw.rect(surface, Constant.COLOR_WHITE, panel_rect, border_radius=14)
        pygame.draw.rect(surface, Constant.COLOR_WARM_BROWN, panel_rect, 3, border_radius=14)

        header_rect = pygame.Rect(
            self.x + Constant.ORDER_UI_HEADER_INSET,
            self.y + Constant.ORDER_UI_HEADER_INSET,
            panel_w - Constant.ORDER_UI_HEADER_INSET * 2,
            Constant.ORDER_UI_HEADER_HEIGHT)
        pygame.draw.rect(surface, Constant.COLOR_WARM_BROWN, header_rect,
                         border_top_left_radius=12, border_top_right_radius=12)

        return panel_rect

    def _render_divider(self, surface: pygame.Surface, panel_w: int) -> None:
        div_y = self.y + Constant.ORDER_UI_DIVIDER_Y_OFFSET
        pygame.draw.line(surface, Constant.COLOR_LIGHT_BROWN,
                         (self.x + Constant.ORDER_UI_DIVIDER_PADDING_X, div_y),
                         (self.x + panel_w - Constant.ORDER_UI_DIVIDER_PADDING_X, div_y), 1)

    def _render_button_area(self, surface: pygame.Surface, panel_w: int, panel_h: int) -> None:
        btn_w = Constant.ORDER_UI_BTN_WIDTH
        btn_h = Constant.ORDER_UI_BTN_HEIGHT
        btn_x = self.x + (panel_w - btn_w) // 2
        btn_y = self.y + panel_h - btn_h - Constant.ORDER_UI_BTN_BOTTOM_PADDING

        if not self.accepted:
            self._accept_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

            shadow = pygame.Rect(
                btn_x + Constant.ORDER_UI_BTN_SHADOW_OFFSET,
                btn_y + Constant.ORDER_UI_BTN_SHADOW_OFFSET,
                btn_w, btn_h)
            pygame.draw.rect(surface, (0, 0, 0, Constant.ORDER_UI_BTN_SHADOW_ALPHA),
                             shadow, border_radius=10)

            pygame.draw.rect(surface, Constant.COLOR_PINK_ACCENT,
                             self._accept_btn_rect, border_radius=10)
            pygame.draw.rect(surface, Constant.COLOR_DARK_BROWN,
                             self._accept_btn_rect, 2, border_radius=10)

            txt = self.font_body.render("Accept", True, Constant.COLOR_WHITE)
            surface.blit(txt, txt.get_rect(center=self._accept_btn_rect.center))
        else:
            badge_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            pygame.draw.rect(surface, Constant.ORDER_UI_ACCEPTED_COLOR,
                             badge_rect, border_radius=10)
            pygame.draw.rect(surface, Constant.COLOR_DARK_BROWN,
                             badge_rect, 2, border_radius=10)

            txt = self.font_body.render("Accepted!", True, Constant.COLOR_WHITE)
            surface.blit(txt, txt.get_rect(center=badge_rect.center))

    # Render modes

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        if self._mode == "npc_info":
            self._render_npc_info(surface)
        else:
            self._render_order_details(surface)

    def _render_npc_info(self, surface: pygame.Surface) -> None:
        panel_w = Constant.ORDER_UI_WIDTH
        panel_h = Constant.ORDER_UI_HEIGHT

        self._render_panel_base(surface, panel_w, panel_h)

        title = self.font_title.render("Customer", True, Constant.COLOR_WHITE)
        surface.blit(title, (self.x + Constant.ORDER_UI_TITLE_OFFSET_X,
                             self.y + Constant.ORDER_UI_TITLE_OFFSET_Y))

        self._render_divider(surface, panel_w)

        # NPC Name
        name_surf = self.font_body.render(self.npc_name, True, Constant.COLOR_DARK_BROWN)
        surface.blit(name_surf, (self.x + Constant.ORDER_UI_NAME_OFFSET_X,
                                 self.y + Constant.ORDER_UI_NAME_OFFSET_Y))

        # NPC Personality (word-wrap)
        if self.npc_personality:
            words = self.npc_personality.split()
            lines = []
            current_line = ""
            max_width = panel_w - Constant.ORDER_UI_PERSONALITY_PADDING

            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                test_surf = self.font_small.render(test_line, True, Constant.COLOR_DARK_BROWN)
                if test_surf.get_width() > max_width and current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line
            if current_line:
                lines.append(current_line)

            for i, line in enumerate(lines[:Constant.ORDER_UI_PERSONALITY_MAX_LINES]):
                line_surf = self.font_small.render(line, True, Constant.COLOR_LIGHT_BROWN)
                surface.blit(line_surf, (
                    self.x + Constant.ORDER_UI_NAME_OFFSET_X,
                    self.y + Constant.ORDER_UI_PERSONALITY_OFFSET_Y + i * Constant.ORDER_UI_PERSONALITY_LINE_HEIGHT))

        self._render_button_area(surface, panel_w, panel_h)

    def _render_order_details(self, surface: pygame.Surface) -> None:
        if not self.order:
            return

        panel_w = Constant.ORDER_UI_WIDTH
        panel_h = Constant.ORDER_UI_HEIGHT

        self._render_panel_base(surface, panel_w, panel_h)

        title = self.font_title.render("Order", True, Constant.COLOR_WHITE)
        surface.blit(title, (self.x + Constant.ORDER_UI_TITLE_OFFSET_X,
                             self.y + Constant.ORDER_UI_TITLE_OFFSET_Y))

        # Timer
        if self.timer_text:
            timer_color = Constant.COLOR_WHITE
            try:
                secs = int(''.join(filter(str.isdigit, self.timer_text) or '99'))
                if secs < Constant.ORDER_UI_TIMER_URGENT_THRESHOLD:
                    timer_color = Constant.ORDER_UI_TIMER_URGENT_COLOR
            except ValueError:
                pass
            timer_surf = self.font_small.render(self.timer_text, True, timer_color)
            surface.blit(timer_surf, (
                self.x + panel_w - Constant.ORDER_UI_TIMER_OFFSET_X,
                self.y + Constant.ORDER_UI_TIMER_OFFSET_Y))

        self._render_divider(surface, panel_w)

        # Order details rows
        if self.order.is_complete():
            icons = Constant.ORDER_UI_DETAIL_LABELS
            values = [
                self.order.flavor.value if hasattr(self.order.flavor, 'value') else str(self.order.flavor),
                self.order.mold.value if hasattr(self.order.mold, 'value') else str(self.order.mold),
                self.order.decoration.value if hasattr(self.order.decoration, 'value') else str(self.order.decoration),
            ]
            for i, (label, value) in enumerate(zip(icons, values)):
                row_y = self.y + Constant.ORDER_UI_DETAIL_ROW_START_Y + i * Constant.ORDER_UI_DETAIL_ROW_SPACING

                label_surf = self.font_body.render(label, True, Constant.COLOR_LIGHT_BROWN)
                surface.blit(label_surf, (self.x + Constant.ORDER_UI_DETAIL_LABEL_X, row_y))

                value_surf = self.font_body.render(value, True, Constant.COLOR_DARK_BROWN)
                surface.blit(value_surf, (self.x + Constant.ORDER_UI_DETAIL_VALUE_X, row_y))

        self._render_button_area(surface, panel_w, panel_h)

    # Event

    def handle_event(self, event: pygame.event.Event) -> bool:
        if (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not self.accepted
                and self.visible
                and self._mode == "npc_info"):
            if self._accept_btn_rect.collidepoint(event.pos):
                self.accepted = True
                print("[DEBUG OrderUI] Accept clicked!")
                return True
        return False
