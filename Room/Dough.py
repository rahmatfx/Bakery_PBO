import pygame
from Enum.BakeryEnum import Flavor, Mold
import os
import Constant
from Order.Cake import Cake
from Order.Order import Order
from Room.Room import Room
from Constant import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    DOUGH_BG,
    COLOR_BG_CREAM,
    COLOR_DARK_BROWN,
    FONT_HEADING_SIZE,
    FONT_BODY_SIZE,
    FONT_NAME
)
from UI.Button import Button


RAW_CAKE = {
    (Flavor.ORIGINAL,   Mold.ROUND): Constant.Raw_Ori_Round_Image,
    (Flavor.ORIGINAL,   Mold.HEART): Constant.Raw_Ori_Love_Image,
    (Flavor.ORIGINAL,   Mold.STAR):  Constant.Raw_Ori_Star_Image,
    (Flavor.CHOCOLATE,  Mold.ROUND): Constant.Raw_Coklat_Round_Image,
    (Flavor.CHOCOLATE,  Mold.HEART): Constant.Raw_Coklat_Love_Image,
    (Flavor.CHOCOLATE,  Mold.STAR):  Constant.Raw_Coklat_Star_Image,
    (Flavor.STRAWBERRY, Mold.ROUND): Constant.Raw_Strawberry_Round_Image,
    (Flavor.STRAWBERRY, Mold.HEART): Constant.Raw_Strawberry_Love_Image,
    (Flavor.STRAWBERRY, Mold.STAR):  Constant.Raw_Strawberry_Star_Image,
}

# Lookup tabel buat gambar adonan per flavor
FLAVOR_DOUGH_IMAGE = {
    Flavor.ORIGINAL:   Constant.Adonan_IMAGE,
    Flavor.CHOCOLATE:  Constant.Adonan_Coklat_IMAGE,
    Flavor.STRAWBERRY: Constant.Adonan_Strawberry_IMAGE,
}

# Lookup tabel gambar cetakan per mold
MOLD_IMAGE = {
    Mold.ROUND: Constant.Cetakan_Round_IMAGE,
    Mold.HEART: Constant.Cetakan_Love_IMAGE,
    Mold.STAR:  Constant.Cetakan_Star_IMAGE,
}


class Dough(Room):
    def __init__(self):
        super().__init__(name="Dough")
        self.cake: Cake         = None
        self.current_order: Order = None

        self._bg_image      = None
        self._exhaust_neck  = None
        self._exhaust_mouth = None
        self._font_heading  = pygame.font.SysFont(FONT_NAME, FONT_HEADING_SIZE)
        self._font_body     = pygame.font.SysFont(FONT_NAME, FONT_BODY_SIZE)

        # Dough visual state
        self._dough_image   = None
        self._dough_entered = False
        self._dough_x       = SCREEN_WIDTH // 2 - 125
        self._dough_y       = -200
        self._target_y      = 400
        self._dough_speed   = 15

        # Mold drag state
        self._mold_image  = None
        self._Dragging    = False
        self._Dough_Cut   = False
        self._offset_x    = 0
        self._offset_y    = 0
        self._mold_rect   = pygame.Rect(SCREEN_WIDTH // 2 - 100, 120, 100, 100)
        self._cut_Area    = pygame.Rect(590, 450, 100, 80)

        # Hitbox cetakan di sidebar
        self._Cetakan_Star  = pygame.Rect(1120, 70,  100, 80)
        self._Cetakan_Love  = pygame.Rect(1120, 155, 100, 68)
        self._Cetakan_Round = pygame.Rect(1120, 225, 100, 80)

        # Flavor buttons
        self._Btn_Original = Button(
            x=-110, y=-5,
            image_path=Constant.BTN_Original_IMAGE,
            hover_image_path=Constant.BTN_Original_IMAGE,
            callback=self.spawn_original
        )
        self._Btn_Coklat = Button(
            x=-125, y=270,
            image_path=Constant.BTN_Coklat_IMAGE,
            hover_image_path=Constant.BTN_Coklat_IMAGE,
            callback=self.spawn_coklat
        )
        self._Btn_Strawberry = Button(
            x=-125, y=122,
            image_path=Constant.BTN_Strawberry_IMAGE,
            hover_image_path=Constant.BTN_Strawberry_IMAGE,
            callback=self.spawn_strawberry
        )

        self._Btn_Original.image         = pygame.transform.smoothscale(self._Btn_Original.image,         (450, 300))
        self._Btn_Original.hover_image   = pygame.transform.smoothscale(self._Btn_Original.hover_image,   (450, 300))
        self._Btn_Coklat.image           = pygame.transform.smoothscale(self._Btn_Coklat.image,           (450, 300))
        self._Btn_Coklat.hover_image     = pygame.transform.smoothscale(self._Btn_Coklat.hover_image,     (450, 300))
        self._Btn_Strawberry.image       = pygame.transform.smoothscale(self._Btn_Strawberry.image,       (450, 310))
        self._Btn_Strawberry.hover_image = pygame.transform.smoothscale(self._Btn_Strawberry.hover_image, (450, 310))

        self._Btn_Original.hitbox   = pygame.Rect(0, 70,  230, 135)
        self._Btn_Coklat.hitbox     = pygame.Rect(0, 349, 230, 140)
        self._Btn_Strawberry.hitbox = pygame.Rect(0, 208, 230, 140)

    # ------------------------------------------------------------------ #
    #  ENTER / EXIT                                                        #
    # ------------------------------------------------------------------ #

    def enter(self):
        print("[DEBUG Dough] Enter room")
        self._reset_visual()
        self._load_bg()
        self._sync_from_cake()   # <-- rebuild visual dari data cake

    def exit(self):
        print("[DEBUG Dough] Exit room")

    # ------------------------------------------------------------------ #
    #  VISUAL HELPERS                                                      #
    # ------------------------------------------------------------------ #

    def _reset_visual(self):
        """Reset semua visual state ke kondisi kosong."""
        self._dough_image    = None
        self._dough_entered  = False
        self._dough_y        = -200
        self._mold_image     = None
        self._Dough_Cut      = False
        self._Dragging       = False
        self._mold_rect.topleft = (SCREEN_WIDTH // 2 - 100, 120)

    def _load_bg(self):
        """Load background dan gambar exhaust."""
        if os.path.exists(DOUGH_BG):
            self._bg_image = pygame.transform.smoothscale(
                pygame.image.load(DOUGH_BG).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT - Constant.NAV_BAR_HEIGHT)
            )
            print("[DEBUG Dough] Background loaded")
        else:
            self._bg_image = None
            print("[DEBUG Dough] Background not found")

        if os.path.exists(Constant.Exhaust_Neck_IMAGE):
            self._exhaust_neck = pygame.transform.smoothscale(
                pygame.image.load(Constant.Exhaust_Neck_IMAGE).convert_alpha(), (1000, 400))
        if os.path.exists(Constant.Exhaust_Mouth_IMAGE):
            self._exhaust_mouth = pygame.transform.smoothscale(
                pygame.image.load(Constant.Exhaust_Mouth_IMAGE).convert_alpha(), (950, 350))

    def _sync_from_cake(self):
        """
        Rebuild visual state dari cake object — dipanggil setiap enter().
        Ini yang bikin state selalu benar meskipun user bolak-balik room.
        """
        if not self.cake:
            return

        # Kalau flavor sudah dipilih, tampilkan adonan langsung (skip animasi)
        if self.cake.flavor:
            self._load_flavor_image(self.cake.flavor)
            self._dough_y       = self._target_y
            self._dough_entered = True
            print(f"[DEBUG Dough] Sync: flavor={self.cake.flavor.value}")

        # Kalau mold sudah dipilih, berarti sudah dipotong — tampilkan raw cake
        if self.cake.mold:
            path = RAW_CAKE.get((self.cake.flavor, self.cake.mold))
            if path and os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                self._dough_image = pygame.transform.smoothscale(img, (250, 175))
            self._Dough_Cut  = True
            self._mold_image = None
            print(f"[DEBUG Dough] Sync: mold={self.cake.mold.value}, sudah dipotong")

    def _load_flavor_image(self, flavor: Flavor):
        """Load gambar adonan sesuai flavor."""
        path = FLAVOR_DOUGH_IMAGE.get(flavor)
        if path and os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            self._dough_image = pygame.transform.smoothscale(img, (250, 175))

    # ------------------------------------------------------------------ #
    #  SPAWN DOUGH                                                         #
    # ------------------------------------------------------------------ #

    def spawn_original(self):
        if self.cake.flavor is not None:
            return
        self.cake.set_flavor(Flavor.ORIGINAL)
        self._load_flavor_image(Flavor.ORIGINAL)
        self._dough_entered = True
        self._dough_y = -200
        print("[DEBUG Dough] Spawn original dough")

    def spawn_coklat(self):
        if self.cake.flavor is not None:
            return
        self.cake.set_flavor(Flavor.CHOCOLATE)
        self._load_flavor_image(Flavor.CHOCOLATE)
        self._dough_entered = True
        self._dough_y = -300
        print("[DEBUG Dough] Spawn chocolate dough")

    def spawn_strawberry(self):
        if self.cake.flavor is not None:
            return
        self.cake.set_flavor(Flavor.STRAWBERRY)
        self._load_flavor_image(Flavor.STRAWBERRY)
        self._dough_entered = True
        self._dough_y = -300
        print("[DEBUG Dough] Spawn strawberry dough")

    # ------------------------------------------------------------------ #
    #  MOLD SELECTION                                                      #
    # ------------------------------------------------------------------ #

    def _select_mold(self, mold: Mold):
        """Satu method untuk semua mold — hilangkan duplikasi."""
        if self.cake.flavor is None or self.cake.mold is not None:
            return
        self.cake.set_mold(mold)
        path = MOLD_IMAGE.get(mold)
        if path and os.path.exists(path):
            self._mold_image = pygame.transform.smoothscale(
                pygame.image.load(path).convert_alpha(), (200, 200))
        self._mold_rect.topleft = (SCREEN_WIDTH // 2 - 100, 120)
        print(f"[DEBUG Dough] {mold.value} mold selected")

    def _select_round(self): self._select_mold(Mold.ROUND)
    def _select_heart(self): self._select_mold(Mold.HEART)
    def _select_star(self):  self._select_mold(Mold.STAR)

    # ------------------------------------------------------------------ #
    #  CUT DOUGH                                                           #
    # ------------------------------------------------------------------ #

    def cut_dough(self):
        """Ubah gambar adonan jadi bentuk sesuai cetakan."""
        path = RAW_CAKE.get((self.cake.flavor, self.cake.mold))
        if path and os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            self._dough_image = pygame.transform.smoothscale(img, (250, 175))

    # ------------------------------------------------------------------ #
    #  UPDATE                                                              #
    # ------------------------------------------------------------------ #

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self._Btn_Original.is_hovered   = self._Btn_Original.hitbox.collidepoint(mouse_pos)
        self._Btn_Coklat.is_hovered     = self._Btn_Coklat.hitbox.collidepoint(mouse_pos)
        self._Btn_Strawberry.is_hovered = self._Btn_Strawberry.hitbox.collidepoint(mouse_pos)

        if self._dough_entered and self._dough_y < self._target_y:
            self._dough_y += self._dough_speed
            if self._dough_y >= self._target_y:
                self._dough_y = self._target_y
                if self.cake and self.cake.flavor:
                    print(f"[DEBUG Dough] {self.cake.flavor.value} dough fully entered")

    # ------------------------------------------------------------------ #
    #  RENDER                                                              #
    # ------------------------------------------------------------------ #

    def render(self):
        if not self.screen:
            return

        if self._bg_image:
            self.screen.blit(self._bg_image, (0, Constant.NAV_BAR_HEIGHT))

            if self._dough_image and self._dough_entered:
                self.screen.blit(self._dough_image, (self._dough_x, self._dough_y))

            if self._exhaust_neck:
                self.screen.blit(self._exhaust_neck,
                                 (SCREEN_WIDTH // 2 - 488, Constant.NAV_BAR_HEIGHT - 300))
            if self._exhaust_mouth:
                self.screen.blit(self._exhaust_mouth,
                                 (SCREEN_WIDTH // 2 - 475, Constant.NAV_BAR_HEIGHT - 40))

            self._Btn_Original.render(self.screen)
            self._Btn_Coklat.render(self.screen)
            self._Btn_Strawberry.render(self.screen)

        else:
            self.screen.fill(COLOR_BG_CREAM)
            title = self._font_heading.render("~ Dough Room ~", True, COLOR_DARK_BROWN)
            self.screen.blit(title, title.get_rect(
                centerx=SCREEN_WIDTH // 2,
                top=Constant.NAV_BAR_HEIGHT + 130
            ))

        if self.current_order:
            self._render_order_box()

        if self._mold_image:
            img_rect = self._mold_image.get_rect(center=self._mold_rect.center)
            self.screen.blit(self._mold_image, img_rect.topleft)

        if self._Btn_Original.is_hovered:
            self._draw_hover(self._Btn_Original.hitbox)
        if self._Btn_Coklat.is_hovered:
            self._draw_hover(self._Btn_Coklat.hitbox)
        if self._Btn_Strawberry.is_hovered:
            self._draw_hover(self._Btn_Strawberry.hitbox)

    def _render_order_box(self):
        """Render kotak info order di atas layar."""
        box_w, box_h = 600, 100
        box_x = (SCREEN_WIDTH - box_w) // 2
        box_y = Constant.NAV_BAR_HEIGHT + 15

        order_box = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        order_box.fill((255, 255, 255, 200))
        self.screen.blit(order_box, (box_x, box_y))
        pygame.draw.rect(self.screen, COLOR_DARK_BROWN,
                         (box_x, box_y, box_w, box_h), 2, border_radius=8)

        flavor_text = self.current_order.flavor.value     if self.current_order.flavor     else "None"
        mold_text   = self.current_order.mold.value       if self.current_order.mold       else "None"
        deco_text   = self.current_order.decoration.value if self.current_order.decoration else "None"

        title_surf   = self._font_body.render("Current Order:", True, COLOR_DARK_BROWN)
        details_surf = self._font_body.render(
            f"Flavor: {flavor_text} | Mold: {mold_text} | Decoration: {deco_text}",
            True, COLOR_DARK_BROWN)
        self.screen.blit(title_surf,   title_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=box_y + 10))
        self.screen.blit(details_surf, details_surf.get_rect(centerx=SCREEN_WIDTH // 2, top=box_y + 40))

    def _draw_hover(self, rect):
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 100))
        self.screen.blit(overlay, rect.topleft)

    # Alias lama biar tidak ada yang patah kalau masih dipanggil di luar
    def draw_Hover(self, rect): self._draw_hover(rect)

    # ------------------------------------------------------------------ #
    #  EVENTS                                                              #
    # ------------------------------------------------------------------ #

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Flavor buttons
            if self._Btn_Original.hitbox.collidepoint(event.pos):
                self.spawn_original()
            if self._Btn_Coklat.hitbox.collidepoint(event.pos):
                self.spawn_coklat()
            if self._Btn_Strawberry.hitbox.collidepoint(event.pos):
                self.spawn_strawberry()

            # Mold selection
            if self._Cetakan_Star.collidepoint(event.pos):
                self._select_star()
            if self._Cetakan_Love.collidepoint(event.pos):
                self._select_heart()
            if self._Cetakan_Round.collidepoint(event.pos):
                self._select_round()

            # Mulai drag mold
            if self._mold_image and self._mold_rect.collidepoint(event.pos):
                self._Dragging = True
                self._offset_x = self._mold_rect.x - event.pos[0]
                self._offset_y = self._mold_rect.y - event.pos[1]

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._Dragging = False

        if event.type == pygame.MOUSEMOTION and self._Dragging:
            self._mold_rect.x = event.pos[0] + self._offset_x
            self._mold_rect.y = event.pos[1] + self._offset_y

            if self._mold_rect.colliderect(self._cut_Area) and not self._Dough_Cut:
                print("[DEBUG Dough] Dough cut!")
                self.cut_dough()
                self._mold_image = None
                self._Dragging   = False
                self._Dough_Cut  = True
                self._dough_y    = self._target_y  # FIX: pastikan dough kelihatan setelah dipotong
                print("[DEBUG Dough] Cake ready, transitioning to Baking")
                if hasattr(self, "_scene_manager"):
                    self._scene_manager.transition_to("RoomBaking")