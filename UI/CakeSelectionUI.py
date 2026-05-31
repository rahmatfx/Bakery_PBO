import pygame
import Constant


class CakeSelectionUI:

    def __init__(self):
        self._options: list = []        
        self._visible: bool = False
        self._hovered: int = -1         
        self._selected: int = -1       
        self._callback = None           

        self._font_title = None
        self._font_text = None
        self._font_label = None
        self._card_rects: list[pygame.Rect] = []

    # Setup 

    def set_options(self, options: list, callback=None) -> None:
        self._options = options
        self._callback = callback
        self._hovered = -1
        self._selected = -1
        self._build_card_rects()

    def show(self) -> None:
        self._visible = True
        self._hovered = -1
        self._selected = -1

        # Init fonts
        self._font_title = pygame.font.SysFont(
            Constant.FONT_NAME, Constant.CAKE_SELECT_TITLE_SIZE, bold=True)
        self._font_text = pygame.font.SysFont(
            Constant.FONT_NAME, Constant.CAKE_SELECT_TEXT_SIZE)
        self._font_label = pygame.font.SysFont(
            Constant.FONT_NAME, Constant.CAKE_SELECT_LABEL_SIZE)

    def hide(self) -> None:
        self._visible = False
        self._options = []
        self._card_rects = []

    @property
    def visible(self) -> bool:
        return self._visible

    # Card layout

    def _build_card_rects(self) -> None:
        self._card_rects = []

        total_cards = len(self._options)
        if total_cards == 0:
            return

        card_w = Constant.CAKE_SELECT_CARD_WIDTH
        card_h = Constant.CAKE_SELECT_CARD_HEIGHT
        spacing = Constant.CAKE_SELECT_CARD_SPACING

        total_w = total_cards * card_w + (total_cards - 1) * spacing
        start_x = (Constant.SCREEN_WIDTH - total_w) // 2
        start_y = (Constant.SCREEN_HEIGHT - card_h) // 2 + 30

        for i in range(total_cards):
            x = start_x + i * (card_w + spacing)
            rect = pygame.Rect(x, start_y, card_w, card_h)
            self._card_rects.append(rect)

    # Event 

    def handle_event(self, event) -> int:

        if not self._visible or self._selected >= 0:
            return -1

        if event.type == pygame.MOUSEMOTION:
            self._hovered = self._get_card_at(event.pos)

        if (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1):
            idx = self._get_card_at(event.pos)
            if idx >= 0:
                self._selected = idx
                print(f"[CakeSelection] Selected option {idx}")

                # Panggil callback kalau ada
                if self._callback:
                    self._callback(idx)

                return idx

        return -1

    def _get_card_at(self, pos: tuple) -> int:
        for i, rect in enumerate(self._card_rects):
            if rect.collidepoint(pos):
                return i
        return -1

    # Render

    def render(self, screen: pygame.Surface) -> None:
        if not self._visible or not self._options:
            return
        
        if not self._font_title:
            self._font_title = pygame.font.SysFont(
                Constant.FONT_NAME, Constant.CAKE_SELECT_TITLE_SIZE, bold=True)
            self._font_text = pygame.font.SysFont(
                Constant.FONT_NAME, Constant.CAKE_SELECT_TEXT_SIZE)
            self._font_label = pygame.font.SysFont(
                Constant.FONT_NAME, Constant.CAKE_SELECT_LABEL_SIZE)
        # Dark overlay
        overlay = pygame.Surface(
            (Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, Constant.CAKE_SELECT_OVERLAY_ALPHA))
        screen.blit(overlay, (0, 0))

        # Title
        title_surf = self._font_title.render(
            "Pilih Kue", True, Constant.COLOR_WHITE)
        title_x = (Constant.SCREEN_WIDTH - title_surf.get_width()) // 2
        screen.blit(title_surf, (title_x, Constant.CAKE_SELECT_TITLE_Y))

        # Cards 
        for i, rect in enumerate(self._card_rects):
            if i >= len(self._options):
                break

            order = self._options[i]
            is_hovered = (i == self._hovered)
            is_selected = (i == self._selected)

            self._render_card(screen, rect, order, is_hovered, is_selected)

    def _render_card(self, screen: pygame.Surface, rect: pygame.Rect,
                     order, hovered: bool, selected: bool) -> None:

        # Shadow
        shadow = rect.move(4, 4)
        pygame.draw.rect(screen, (0, 0, 0, 80), shadow,
                         border_radius=Constant.CAKE_SELECT_CARD_RADIUS)

        # Background 
        bg_color = Constant.COLOR_BG_CREAM
        if selected:
            bg_color = (200, 255, 200)    
        elif hovered:
            bg_color = (255, 240, 230)     

        pygame.draw.rect(screen, bg_color, rect,
                         border_radius=Constant.CAKE_SELECT_CARD_RADIUS)

        # Border
        if selected:
            border_color = (80, 180, 80)
            border_w = 3
        elif hovered:
            border_color = Constant.COLOR_PINK_ACCENT
            border_w = 3
        else:
            border_color = Constant.COLOR_WARM_BROWN
            border_w = 2

        pygame.draw.rect(screen, border_color, rect, border_w,
                         border_radius=Constant.CAKE_SELECT_CARD_RADIUS)

        # Content
        cx = rect.centerx
        y = rect.y + 20

        label = self._font_label.render("Kue", True, Constant.COLOR_LIGHT_BROWN)
        screen.blit(label, (cx - label.get_width() // 2, y))
        y += 30

        # Garis pemisah
        line_y = y
        pygame.draw.line(screen, Constant.COLOR_LIGHT_BROWN,
                         (rect.x + 16, line_y), (rect.right - 16, line_y), 1)
        y += 12

        # Flavor
        y = self._render_attribute(
            screen, cx, y, "Flavor", order.flavor, (255, 130, 150))

        # Mold
        y = self._render_attribute(
            screen, cx, y, "Mold", order.mold, (180, 220, 130))

        # Decoration
        y = self._render_attribute(
            screen, cx, y, "Deco", order.decoration, (150, 180, 255))

    def _render_attribute(self, screen: pygame.Surface, cx: int, y: int,
                          label: str, value: str, dot_color: tuple) -> int:

        # Guard: pastikan font ada 
        if not self._font_label or not self._font_text:
            return y + 58

        # Label
        label_surf = self._font_label.render(
            label, True, Constant.COLOR_LIGHT_BROWN)
        screen.blit(label_surf, (cx - label_surf.get_width() // 2, y))
        y += 22

        # Dot warna
        dot_x = cx - 60
        dot_y = y + 8
        pygame.draw.circle(screen, dot_color, (dot_x, dot_y), 6)

        # Value text
        if value is None:
            value_text = "???"
        elif hasattr(value, 'value'):
            value_text = value.value     
        else:
            value_text = str(value) 
        value_surf = self._font_text.render(
            value_text, True, Constant.COLOR_DARK_BROWN)
        screen.blit(value_surf, (dot_x + 14, y))
        y += 36

        return y

    def reset(self) -> None:
        self._options = []
        self._hovered = -1
        self._selected = -1
        self._visible = False
        self._card_rects = []
        self._callback = None