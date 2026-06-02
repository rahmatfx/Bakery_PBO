import pygame, os
from Room.Room import Room
from Constant import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BAKING_BG, COLOR_BG_CREAM, COLOR_DARK_BROWN,
    FONT_HEADING_SIZE, FONT_BODY_SIZE, FONT_NAME,
    OVEN_CLOSE_IMAGE, OVEN_OPEN_IMAGE, OVEN_BAKE_IMAGE,
    ADONAN_TEMPORARY, CAKE_TEMPORARY, NAMPAN_IMAGE
)
from Order.Cake import Cake, CakeStep
from Enum.BakeryEnum import Flavor, Mold
import Constant


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

BAKED_CAKE = {
    (Flavor.STRAWBERRY, Mold.ROUND): Constant.CAKE_STRAWBERRY_BUNDAR,
    (Flavor.STRAWBERRY, Mold.STAR):  Constant.CAKE_STRAWBERRY_STAR,
    (Flavor.STRAWBERRY, Mold.HEART): Constant.CAKE_STRAWBERRY_LOVE,
    (Flavor.ORIGINAL,   Mold.ROUND): Constant.CAKE_ORIGINAL_BUNDAR,
    (Flavor.ORIGINAL,   Mold.HEART): Constant.CAKE_ORIGINAL_LOVE,
    (Flavor.ORIGINAL,   Mold.STAR):  Constant.CAKE_ORIGINAL_STAR,
    (Flavor.CHOCOLATE,  Mold.ROUND): Constant.CAKE_CHOCOLATE_BUNDAR,
    (Flavor.CHOCOLATE,  Mold.HEART): Constant.CAKE_CHOCOLATE_LOVE,
    (Flavor.CHOCOLATE,  Mold.STAR):  Constant.CAKE_CHOCOLATE_STAR,
}


class BakingRoom(Room):
    def __init__(self):
        super().__init__(name="Baking")

        self._bg_image           = None
        self._oven_image         = None
        self._oven_image_opening = None
        self._oven_bake_image    = None
        self._font_heading       = pygame.font.SysFont(FONT_NAME, FONT_HEADING_SIZE)
        self._font_body          = pygame.font.SysFont(FONT_NAME, FONT_BODY_SIZE)

        self._oven_rect        = None
        self._oven_size        = None
        self._adonan_rect      = None
        self._adonan_image     = None
        self.cake_image        = None
        self.nampan_image      = None

        self._oven_isOpen      = False
        self._button_bake_rect = None
        self._doughInOven      = False
        self.bakeDough         = False
        self.doughInFront      = False
        self.isDragging        = False
        self.isShowText        = False
        self.isReadyToTake     = False
        self.isInNampan        = False

        self.bake_start_time   = pygame.time.get_ticks()
        self.elapsed           = 0
        self.bake_duration     = 15

        self.rect_posAwalDough = None
        self.rect_posOvenDough = None

        self.game_font    = None
        self.text_surface = None
        self.text_rect    = None

        self.cake: Cake = None
        
        self.audio = None

    @property
    def isBaked(self) -> bool:
        return self.cake is not None and self.cake.step >= CakeStep.BAKED

    def enter(self):
        self._reset_visual()
        self._load_assets()
        self._sync_from_cake()

    def exit(self) -> None:
        pass

    def _reset_visual(self):
        self._doughInOven  = False
        self.bakeDough     = False
        self.doughInFront  = False
        self.isDragging    = False
        self.isShowText    = False
        self.isReadyToTake = False
        self.isInNampan    = False
        self._oven_isOpen  = False
        self.elapsed       = 0
        self._adonan_image = None
        self.cake_image    = None

    def _load_assets(self):

        # Background
        if os.path.exists(BAKING_BG):
            self._bg_image = pygame.transform.smoothscale(
                pygame.image.load(BAKING_BG).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))

        # Nampan
        if os.path.exists(NAMPAN_IMAGE):
            img = pygame.image.load(NAMPAN_IMAGE).convert_alpha()
            w, h = img.get_size()
            nw = 150
            self.nampan_image = pygame.transform.smoothscale(img, (nw, int(h * nw / w)))

        # Adonan mentah
        if self.cake and self.cake.flavor and self.cake.mold:
            path = RAW_CAKE.get((self.cake.flavor, self.cake.mold))
            if path and os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                w, h = img.get_size()
                nw = 150
                self._adonan_image = pygame.transform.smoothscale(img, (nw, int(h * nw / w)))

        # Kue matang
        if self.cake and self.cake.flavor and self.cake.mold:
            path = BAKED_CAKE.get((self.cake.flavor, self.cake.mold))
            if path and os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                w, h = img.get_size()
                nw = 130
                self.cake_image = pygame.transform.smoothscale(img, (nw, int(h * nw / w)))

        # Oven images (close, open, baking)
        oven_assets = [
            ("_oven_image",         OVEN_CLOSE_IMAGE),
            ("_oven_image_opening", OVEN_OPEN_IMAGE),
            ("_oven_bake_image",    OVEN_BAKE_IMAGE),
        ]
        for attr, path in oven_assets:
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                w, h = img.get_size()
                nw = 520
                setattr(self, attr, pygame.transform.smoothscale(img, (nw, int(h * nw / w))))

        if self._oven_image:
            self._oven_size = self._oven_image.get_rect(
                centerx=SCREEN_WIDTH - 550, bottom=SCREEN_HEIGHT + 5)

        # Rects
        self._oven_rect        = pygame.Rect(530, 420, 400, 270)
        self._button_bake_rect = pygame.Rect(910, 340, 50, 50)
        self.rect_posAwalDough = pygame.Rect(250, 280, 50, 50)
        self.rect_posOvenDough = pygame.Rect(710, 600, 50, 50)

        if self._adonan_image:
            self._adonan_rect = self._adonan_image.get_rect(
                centerx=SCREEN_WIDTH - 1000, bottom=SCREEN_HEIGHT - 350)

        # Font countdown
        self.game_font    = pygame.font.SysFont("Orbitron.ttf", 30, True)
        self.text_surface = self.game_font.render("", True, (255, 255, 59))
        self.text_rect    = pygame.Rect(825, 355, 50, 50)

    def _sync_from_cake(self):
        if not self.cake:
            return

        if self.isBaked:
            self.isReadyToTake = True
            self._oven_isOpen = True
            if self._adonan_rect and self.rect_posOvenDough:
                self._adonan_rect.center = self.rect_posOvenDough.center
            print("[DEBUG Baking] Sync: cake already baked")

        elif self.cake.is_baking:
            # Sedang baking — cek apakah udah selesai
            now = pygame.time.get_ticks()
            elapsed_sec = (now - self.cake.bake_start_time) // 1000
            remaining = self.bake_duration - elapsed_sec
            if remaining <= 0:
                # Selesai pas di ruangan lain
                self.cake.set_baked()
                self.cake.is_baking = False
                self.cake.bake_start_time = None
                self.isReadyToTake = True
                self._oven_isOpen = True
                print("[DEBUG Baking] Sync: baking completed while away")
            else:
                # Masih baking
                self.bakeDough = True
                self.isShowText = True
                self._doughInOven = True
                self._oven_isOpen = False
                self.bake_start_time = self.cake.bake_start_time
                self.elapsed = remaining
                print(f"[DEBUG Baking] Sync: baking resumed, {remaining}s left")

        elif self.cake.flavor and self.cake.mold:
            # Dough ada tapi belum masuk oven
            self._oven_isOpen = False
            print("[DEBUG Baking] Sync: dough ready, not in oven yet")

    def mekanik(self):
        if self._adonan_rect and self._adonan_rect.colliderect(self._oven_rect):
            if self._oven_isOpen and not self.isDragging:
                self.doughInFront = True
                print("Adonan berhasil masuk")

    def update(self):
        self.mekanik()

        if self.bakeDough:
            self.elapsed = self.bake_duration - (pygame.time.get_ticks() - self.bake_start_time) // 1000
            if self.elapsed <= 0:
                print("[DEBUG Baking] Kue matang!")
                self.bakeDough     = False
                self.cake.set_baked()  
                self.cake.is_baking = False        
                self.cake.bake_start_time = None 
                self.isReadyToTake = True


    def render(self):
        if not self.screen:
            return

        # Background
        if self._bg_image:
            self.screen.blit(self._bg_image, (0, 0))
        else:
            self.screen.fill(COLOR_BG_CREAM)
            t = self._font_heading.render("~ Baking Room ~", True, COLOR_DARK_BROWN)
            self.screen.blit(t, t.get_rect(centerx=SCREEN_WIDTH // 2, centery=SCREEN_HEIGHT // 3))

        # Oven
        if self._oven_size:
            if self._oven_bake_image and self.bakeDough:
                self.screen.blit(self._oven_bake_image, self._oven_size)
            elif self._oven_isOpen and self._oven_image_opening:
                self.screen.blit(self._oven_image_opening, self._oven_size)
            elif self._oven_image:
                self.screen.blit(self._oven_image, self._oven_size)

        # Nampan
        if self.nampan_image:
            nampan = pygame.transform.scale(self.nampan_image, (300, 410))
            self.screen.blit(nampan, (120, 120))

        # Adonan / kue — hanya tampil kalau tidak ada di dalam oven
        if self._adonan_rect and not self._doughInOven:
            if self.isBaked and self.cake_image:
                # Kue matang
                self.screen.blit(self.cake_image, self._adonan_rect)
            elif not self.isBaked and self._adonan_image:
                # Masih mentah
                self.screen.blit(self._adonan_image, self._adonan_rect)

        # Debug rects
        if self._oven_rect:
            pygame.draw.rect(self.screen, (255, 0, 0), self._oven_rect, 2)
        if self._button_bake_rect:
            pygame.draw.rect(self.screen, (25, 52, 224), self._button_bake_rect, 2)
        if self._adonan_rect:
            pygame.draw.rect(self.screen, (25, 52, 224), self._adonan_rect, 2)
        if self.rect_posAwalDough:
            pygame.draw.rect(self.screen, (25, 52, 224), self.rect_posAwalDough, 2)
        if self.rect_posOvenDough:
            pygame.draw.rect(self.screen, (25, 52, 224), self.rect_posOvenDough, 2)

        # Countdown timer
        if self.isShowText and self.bakeDough:
            self.text_surface = self.game_font.render(f"{max(0, self.elapsed)}", True, (255, 255, 59))
            self.screen.blit(self.text_surface, self.text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos

            # Klik oven
            if self._oven_rect and self._oven_rect.collidepoint(mouse_pos):
                if not self.bakeDough and (not self._doughInOven or self.isReadyToTake):
                    if self.isReadyToTake and not self._oven_isOpen:
                        # Buka oven untuk ambil kue
                        self._oven_isOpen = True
                        self._doughInOven = False
                        if self._adonan_rect and self.rect_posOvenDough:
                            self._adonan_rect.center = self.rect_posOvenDough.center
                    elif not self.isReadyToTake:
                        # Toggle buka/tutup oven
                        self._oven_isOpen = not self._oven_isOpen
                        if not self._oven_isOpen and self.doughInFront:
                            self._doughInOven = True

            # Klik adonan untuk drag
            if self._adonan_rect and self._adonan_rect.collidepoint(mouse_pos):
                if not self._doughInOven or self.isReadyToTake:
                    self.isDragging = True

            # Tombol panggang
            if (self._button_bake_rect
                    and self._button_bake_rect.collidepoint(mouse_pos)
                    and not self._oven_isOpen
                    and self._doughInOven
                    and not self.bakeDough):
                self.bakeDough       = True
                self.isShowText      = True
                self.bake_start_time = pygame.time.get_ticks()
                self.cake.is_baking = True                     # NEW
                self.cake.bake_start_time = self.bake_start_time 
                print("[DEBUG Baking] Baking started")

        if event.type == pygame.MOUSEMOTION and self.isDragging:
            if self._adonan_rect:
                self._adonan_rect.center = event.pos

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.isDragging = False
            if self._adonan_rect:
                in_oven = self._oven_isOpen and self._adonan_rect.colliderect(self._oven_rect)
                if not in_oven:
                    # Kue dilepas di luar oven
                    self._adonan_rect.center = self.rect_posAwalDough.center
                    if self.isReadyToTake:
                        # Kue matang diambil ke nampan
                        self.isInNampan    = True
                        self.doughInFront  = False
                        self._doughInOven  = False
                        self.bakeDough     = False
                        self.isReadyToTake = False
                        print("[DEBUG Baking] Kue masuk nampan")
                else:
                    # Dilepas di dalam oven
                    self._adonan_rect.center = self.rect_posOvenDough.center