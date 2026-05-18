import pygame
import Constant


class OrderUI:
    """Visual UI for displaying customer order details + accept button + timer."""

    def __init__(self):
        self.order = None
        self.visible = False
        self.accepted = False

        self.x = 0
        self.y = 0

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

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False

    def set_timer_text(self, text: str) -> None:
        self.timer_text = text

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible or not self.order:
            return

        panel_w = Constant.ORDER_UI_WIDTH
        panel_h = Constant.ORDER_UI_HEIGHT

        shadow_rect = pygame.Rect(self.x + 4, self.y + 4, panel_w, panel_h)
        pygame.draw.rect(surface, (0, 0, 0, 60), shadow_rect, border_radius=14)

        panel_rect = pygame.Rect(self.x, self.y, panel_w, panel_h)
        pygame.draw.rect(surface, Constant.COLOR_WHITE, panel_rect, border_radius=14)
        pygame.draw.rect(surface, Constant.COLOR_WARM_BROWN, panel_rect, 3, border_radius=14)

        header_rect = pygame.Rect(self.x + 3, self.y + 3, panel_w - 6, 44)
        pygame.draw.rect(surface, Constant.COLOR_WARM_BROWN, header_rect,
                         border_top_left_radius=12, border_top_right_radius=12)

        title = self.font_title.render("Order", True, Constant.COLOR_WHITE)
        surface.blit(title, (self.x + 18, self.y + 8))

        if self.timer_text and self.accepted:
            timer_color = Constant.COLOR_WHITE
            if int(''.join(filter(str.isdigit, self.timer_text) or '99')) < 10:
                timer_color = (255, 100, 100)
            timer_surf = self.font_small.render(self.timer_text, True, timer_color)
            surface.blit(timer_surf, (self.x + panel_w - 95, self.y + 16))

        div_y = self.y + 50
        pygame.draw.line(surface, Constant.COLOR_LIGHT_BROWN,
                         (self.x + 15, div_y), (self.x + panel_w - 15, div_y), 1)

        if self.order.is_complete():
            icons = ["Flavor:", "Mold:", "Top:"]
            values = [
                self.order.flavor.value,
                self.order.mold.value,
                self.order.decoration.value,
            ]
            for i, (label, value) in enumerate(zip(icons, values)):
                row_y = self.y + 60 + i * 34

                label_surf = self.font_body.render(label, True, Constant.COLOR_LIGHT_BROWN)
                surface.blit(label_surf, (self.x + 20, row_y))

                value_surf = self.font_body.render(value, True, Constant.COLOR_DARK_BROWN)
                surface.blit(value_surf, (self.x + 110, row_y))

        btn_w, btn_h = 150, 42
        btn_x = self.x + (panel_w - btn_w) // 2
        btn_y = self.y + panel_h - btn_h - 14

        if not self.accepted:
            self._accept_btn_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)

            shadow = pygame.Rect(btn_x + 2, btn_y + 2, btn_w, btn_h)
            pygame.draw.rect(surface, (0, 0, 0, 40), shadow, border_radius=10)

            pygame.draw.rect(surface, Constant.COLOR_PINK_ACCENT,
                             self._accept_btn_rect, border_radius=10)
            pygame.draw.rect(surface, Constant.COLOR_DARK_BROWN,
                             self._accept_btn_rect, 2, border_radius=10)

            txt = self.font_body.render("Accept", True, Constant.COLOR_WHITE)
            surface.blit(txt, txt.get_rect(center=self._accept_btn_rect.center))
        else:
            badge_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
            pygame.draw.rect(surface, (80, 180, 80), badge_rect, border_radius=10)
            pygame.draw.rect(surface, Constant.COLOR_DARK_BROWN, badge_rect, 2, border_radius=10)

            txt = self.font_body.render("Accepted!", True, Constant.COLOR_WHITE)
            surface.blit(txt, txt.get_rect(center=badge_rect.center))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and not self.accepted
                and self.visible):
            if self._accept_btn_rect.collidepoint(event.pos):
                self.accepted = True
                print("[DEBUG OrderUI] Accept clicked!")
                return True
        return False