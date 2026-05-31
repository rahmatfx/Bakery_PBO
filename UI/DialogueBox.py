import pygame
import Constant


class DialogueBox:

    def __init__(self):
        self.visible: bool = False

        # fonts
        self.font_name = pygame.font.SysFont(Constant.FONT_NAME,
                                              Constant.FONT_BODY_SIZE)
        self.font_text = pygame.font.SysFont(Constant.FONT_NAME,
                                              Constant.DIALOGUE_TEXT_SIZE)
        self.font_choice = pygame.font.SysFont(Constant.FONT_NAME,
                                                Constant.CHOICE_CENTER_FONT_SIZE)
        self.font_hint = pygame.font.SysFont(Constant.FONT_NAME,
                                              Constant.FONT_SMALL_SIZE)

        # panel
        self.panel_x = Constant.DIALOGUE_MARGIN_X
        self.panel_y = Constant.DIALOGUE_BOX_Y
        self.panel_w = Constant.SCREEN_WIDTH - (Constant.DIALOGUE_MARGIN_X * 2)
        self.panel_h = Constant.DIALOGUE_BOX_HEIGHT

        # typewriter
        self._full_text: str = ""
        self._displayed_chars: int = 0
        self._typewriter_done: bool = True

        # choices
        self._choices: list[dict] = []
        self._choice_rects: list[pygame.Rect] = []
        self._hovered_choice: int = -1
        self._show_choices: bool = False
 
        self._npc_name: str = ""

    # public

    def show(self) -> None:
        self.visible = True

    def hide(self) -> None:
        self.visible = False
        self._full_text = ""
        self._displayed_chars = 0
        self._typewriter_done = True
        self._choices = []
        self._choice_rects = []
        self._show_choices = False

    def set_name(self, name: str) -> None:
        self._npc_name = name

    def set_text(self, text: str) -> None:
        self._full_text = text
        self._displayed_chars = 0
        self._typewriter_done = False

    def set_choices(self, choices: list[dict]) -> None:
        self._choices = choices
        self._choice_rects = []
        self._hovered_choice = -1
        self._show_choices = False

        if not choices:
            return

        choice_w = Constant.CHOICE_CENTER_WIDTH
        choice_h = Constant.CHOICE_CENTER_HEIGHT
        spacing = Constant.CHOICE_CENTER_SPACING

        total_h = len(choices) * choice_h + (len(choices) - 1) * spacing
        start_y = (Constant.SCREEN_HEIGHT - total_h) // 2

        for i in range(len(choices)):
            x = (Constant.SCREEN_WIDTH - choice_w) // 2
            y = start_y + i * (choice_h + spacing)
            rect = pygame.Rect(x, y, choice_w, choice_h)
            self._choice_rects.append(rect)

    def is_typewriter_done(self) -> bool:
        return self._typewriter_done

    def skip_typewriter(self) -> None:
        self._displayed_chars = len(self._full_text)
        self._typewriter_done = True

    # update

    def update(self, delta_time: float = 0.0, audio=None) -> None:
        if not self.visible:
            return

        if not self._typewriter_done:
            prev_chars = int(self._displayed_chars)
            self._displayed_chars += Constant.TYPEWRITER_SPEED
            if self._displayed_chars >= len(self._full_text):
                self._displayed_chars = len(self._full_text)
                self._typewriter_done = True

            # typewriter sfx
            if audio and int(self._displayed_chars) > prev_chars:
                audio.play_type_tick(delta_time)

        mouse_pos = pygame.mouse.get_pos()
        self._hovered_choice = -1
        for i, rect in enumerate(self._choice_rects):
            if rect.collidepoint(mouse_pos):
                self._hovered_choice = i
                break

    # render

    def render(self, surface: pygame.Surface) -> None:
        if not self.visible:
            return

        # choices overlay
        if self._show_choices and self._choices:
            self._render_choices_overlay(surface)
            return

        # dialogue panel
        self._render_panel(surface)
        self._render_name_tag(surface)
        self._render_text(surface)

        if self._typewriter_done and not self._choices:
            hint = self.font_hint.render("Click to continue...",
                                          True, Constant.COLOR_LIGHT_BROWN)
            surface.blit(hint,
                         (self.panel_x + self.panel_w - Constant.DIALOGUE_HINT_OFFSET_X,
                          self.panel_y + self.panel_h - Constant.DIALOGUE_HINT_OFFSET_Y))

    def _render_panel(self, surface: pygame.Surface) -> None:
        panel_rect = pygame.Rect(self.panel_x, self.panel_y,
                                  self.panel_w, self.panel_h)

        shadow = panel_rect.move(Constant.DIALOGUE_SHADOW_OFFSET, Constant.DIALOGUE_SHADOW_OFFSET)
        pygame.draw.rect(surface, (0, 0, 0), shadow, border_radius=12)

        pygame.draw.rect(surface, Constant.DIALOGUE_BG_COLOR,
                          panel_rect, border_radius=12)
        pygame.draw.rect(surface, Constant.COLOR_WARM_BROWN,
                          panel_rect, 3, border_radius=12)

    def _render_name_tag(self, surface: pygame.Surface) -> None:
        if not self._npc_name:
            return

        name_surf = self.font_name.render(self._npc_name, True,
                                           Constant.COLOR_WHITE)
        tag_w = name_surf.get_width() + Constant.DIALOGUE_NAME_TAG_INNER_PAD
        tag_h = Constant.DIALOGUE_NAME_TAG_HEIGHT
        tag_x = self.panel_x + Constant.DIALOGUE_PADDING
        tag_y = self.panel_y + Constant.DIALOGUE_PADDING

        tag_rect = pygame.Rect(tag_x, tag_y, tag_w, tag_h)
        pygame.draw.rect(surface, Constant.COLOR_WARM_BROWN,
                          tag_rect,
                          border_top_left_radius=8,
                          border_top_right_radius=8)
        pygame.draw.rect(surface, Constant.COLOR_DARK_BROWN,
                          tag_rect, 2,
                          border_top_left_radius=8,
                          border_top_right_radius=8)

        surface.blit(name_surf, (tag_x + Constant.DIALOGUE_NAME_TAG_PADDING_X, tag_y + Constant.DIALOGUE_NAME_TAG_PADDING_Y))

    def _render_text(self, surface: pygame.Surface) -> None:
        if not self._full_text:
            return

        visible_text = self._full_text[:self._displayed_chars]
        text_x = self.panel_x + Constant.DIALOGUE_PADDING + Constant.DIALOGUE_TEXT_EXTRA_OFFSET
        text_y = self.panel_y + Constant.DIALOGUE_PADDING + \
                 Constant.DIALOGUE_NAME_TAG_HEIGHT + Constant.DIALOGUE_TEXT_EXTRA_OFFSET

        max_width = self.panel_w - Constant.DIALOGUE_PADDING * 2 - Constant.DIALOGUE_TEXT_WIDTH_MARGIN
        words = visible_text.split(" ")
        lines = []
        current_line = ""

        for word in words:
            test = current_line + (" " if current_line else "") + word
            if self.font_text.size(test)[0] <= max_width:
                current_line = test
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        line_height = self.font_text.get_height() + 4
        for i, line in enumerate(lines):
            text_surf = self.font_text.render(line, True,
                                               Constant.COLOR_DARK_BROWN)
            surface.blit(text_surf, (text_x, text_y + i * line_height))

    def _render_choices_overlay(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT),
                                  pygame.SRCALPHA)
        overlay.fill((0, 0, 0, Constant.DIALOGUE_CHOICE_OVERLAY_ALPHA))
        surface.blit(overlay, (0, 0))

        for i, choice in enumerate(self._choices):
            if i >= len(self._choice_rects):
                break

            rect = self._choice_rects[i]
            is_hovered = (i == self._hovered_choice)

            shadow = rect.move(Constant.DIALOGUE_SHADOW_OFFSET, Constant.DIALOGUE_SHADOW_OFFSET)
            pygame.draw.rect(surface, (0, 0, 0), shadow, border_radius=12)

            if is_hovered:
                bg_color = Constant.COLOR_PINK_ACCENT
                text_color = Constant.COLOR_WHITE
            else:
                bg_color = Constant.COLOR_BG_CREAM
                text_color = Constant.COLOR_DARK_BROWN

            pygame.draw.rect(surface, bg_color, rect, border_radius=12)
            pygame.draw.rect(surface, Constant.COLOR_WARM_BROWN,
                              rect, 3, border_radius=12)

            choice_text = choice.get("text", "...")
            text_surf = self.font_choice.render(choice_text, True, text_color)
            surface.blit(text_surf,
                         text_surf.get_rect(center=rect.center))

    # events

    def handle_event(self, event: pygame.event.Event) -> int:
        if not self.visible or event.type != pygame.MOUSEBUTTONDOWN:
            return -1
        if event.button != 1:
            return -1

        if not self._typewriter_done:
            self.skip_typewriter()
            return -1

        # show choices
        if self._choices and not self._show_choices:
            self._show_choices = True
            return -1 

        if self._show_choices and self._choices:
            for i, rect in enumerate(self._choice_rects):
                if rect.collidepoint(event.pos):
                    print(f"[DialogueBox] Choice {i} clicked")
                    return i
            return -1

        panel_rect = pygame.Rect(self.panel_x, self.panel_y,
                                  self.panel_w, self.panel_h)
        if panel_rect.collidepoint(event.pos):
            return -2

        return -1