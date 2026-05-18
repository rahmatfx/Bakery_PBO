import pygame
import os


class Button:
   
    def __init__(
        self,
        x: int,
        y: int,
        image_path: str,
        hover_image_path: str = None,
        label: str = "",
        callback=None,
    ):
        self.label = label
        self.callback = callback
        self.is_hovered = False

        self.image = self._load_image(image_path, fallback_size=(220, 55))

        if hover_image_path and os.path.exists(hover_image_path):
            self.hover_image = self._load_image(hover_image_path, fallback_size=(220, 55))
        else:
            self.hover_image = self._create_hover_image(self.image)

        self.rect = self.image.get_rect(topleft=(x, y))

    def _load_image(self, path: str, fallback_size: tuple = (220, 55)) -> pygame.Surface:
        """
        Load gambar dari path. Kalau file belum ada,
        buat rectangle warna sebagai fallback supaya game tetap jalan.
        """
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            return img
        else:
            print(f"[DEBUG] Button image not found: {path} — using fallback rectangle")
            surf = pygame.Surface(fallback_size)
            surf.fill((139, 90, 43)) 
            return surf

    def _create_hover_image(self, base_image: pygame.Surface) -> pygame.Surface:
        """Buat versi hover: overlay putih semi-transparan di atas gambar normal."""
        hover = base_image.copy()
        overlay = pygame.Surface(hover.get_size(), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 60)) 
        hover.blit(overlay, (0, 0))
        return hover

    def update(self, mouse_pos: tuple) -> None:
        """Update hover state berdasarkan posisi mouse (collision detection)."""
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def render(self, surface: pygame.Surface) -> None:
        """Render gambar button (normal atau hover)."""
        img = self.hover_image if self.is_hovered else self.image
        surface.blit(img, self.rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Deteksi klik pada area button (collision)."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.callback:
                print(f"[DEBUG] Button clicked: {self.label}")
                self.callback()

    def set_position(self, x: int, y: int) -> None:
        """Pindahkan posisi button."""
        self.rect.topleft = (x, y)

    def get_rect(self) -> pygame.Rect:
        """Kembalikan rect button (untuk collision check dari luar)."""
        return self.rect
