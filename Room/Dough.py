import pygame
from Enum.BakeryEnum import Flavor, Mold
import os
import Constant
from Order.Cake import Cake
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
    (Flavor.ORIGINAL, Mold.ROUND): Constant.Raw_Ori_Round_Image,
    (Flavor.ORIGINAL, Mold.HEART): Constant.Raw_Ori_Love_Image,
    (Flavor.ORIGINAL, Mold.STAR): Constant.Raw_Ori_Star_Image,
    (Flavor.CHOCOLATE, Mold.ROUND): Constant.Raw_Coklat_Round_Image,
    (Flavor.CHOCOLATE, Mold.HEART): Constant.Raw_Coklat_Love_Image,
    (Flavor.CHOCOLATE, Mold.STAR): Constant.Raw_Coklat_Star_Image,
    (Flavor.STRAWBERRY, Mold.ROUND): Constant.Raw_Strawberry_Round_Image,
    (Flavor.STRAWBERRY, Mold.HEART): Constant.Raw_Strawberry_Love_Image,
    (Flavor.STRAWBERRY, Mold.STAR): Constant.Raw_Strawberry_Star_Image,
}

class Dough(Room):
    def __init__(self):
        super().__init__(name="Dough")
        self.cake = Cake()
        self._bg_image = None
        self._font_heading = pygame.font.SysFont(FONT_NAME, FONT_HEADING_SIZE)
        self._font_body = pygame.font.SysFont(FONT_NAME, FONT_BODY_SIZE)
        self._dough_image = None
        self._exhaust_neck = None
        self._exhaust_mouth = None
        self._Dragging = False
        self._Dough_Cut = False
        self._mold_image = None
        self._offset_x = 0
        self._offset_y = 0
        self._mold_x = SCREEN_WIDTH // 2 - 100
        self._mold_y = 120
        self._mold_rect = pygame.Rect(self._mold_x, self._mold_y, 100, 100)
        self._cut_Area = pygame.Rect(590, 450, 100, 80)
        self._dough_entered = False
        self._dough_x = SCREEN_WIDTH // 2 - 125
        self._dough_y = -200
        self._target_y = 400
        self._dough_speed = 15
        

        self._Btn_Original = Button(
            x=-110,
            y=-5,
            image_path=Constant.BTN_Original_IMAGE,
            hover_image_path=Constant.BTN_Original_IMAGE,
            callback=self.spawn_original
        )

        self._Btn_Coklat = Button(
            x=-125,
            y=270,
            image_path=Constant.BTN_Coklat_IMAGE,
            hover_image_path=Constant.BTN_Coklat_IMAGE,
            callback=self.spawn_coklat
        )

        self._Btn_Strawberry = Button(
            x=-125,
            y=122,
            image_path=Constant.BTN_Strawberry_IMAGE,
            hover_image_path=Constant.BTN_Strawberry_IMAGE,
            callback=self.spawn_strawberry
        )

        self._Btn_Original.image = pygame.transform.smoothscale(self._Btn_Original.image, (450, 300))
        self._Btn_Original.hover_image = pygame.transform.smoothscale(self._Btn_Original.hover_image, (450, 300))

        self._Btn_Coklat.image = pygame.transform.smoothscale(self._Btn_Coklat.image, (450, 300))
        self._Btn_Coklat.hover_image = pygame.transform.smoothscale(self._Btn_Coklat.hover_image, (450, 300))

        self._Btn_Strawberry.image = pygame.transform.smoothscale(self._Btn_Strawberry.image, (450, 310))
        self._Btn_Strawberry.hover_image = pygame.transform.smoothscale(self._Btn_Strawberry.hover_image, (450, 310))

        self._Btn_Original.hitbox = pygame.Rect(0, 70, 230, 135)
        self._Btn_Coklat.hitbox = pygame.Rect(0, 349, 230, 140)
        self._Btn_Strawberry.hitbox = pygame.Rect(0, 208, 230, 140)

        self._Cetakan_Star = pygame.Rect(1120, 70, 100, 80)
        self._Cetakan_Love = pygame.Rect(1120, 155, 100, 68)
        self._Cetakan_Round = pygame.Rect(1120, 225, 100, 80)

    def enter(self):
        print("[DEBUG Dough] Enter room")

        if os.path.exists(DOUGH_BG):
            self._bg_image = pygame.transform.smoothscale(
                pygame.image.load(DOUGH_BG).convert(),
                (SCREEN_WIDTH, SCREEN_HEIGHT - Constant.NAV_BAR_HEIGHT)
            )
            print("[DEBUG Dough] Background loaded")
            if os.path.exists(Constant.Exhaust_Neck_IMAGE):
                self._exhaust_neck = pygame.image.load(Constant.Exhaust_Neck_IMAGE).convert_alpha()

                self._exhaust_neck = pygame.transform.smoothscale(self._exhaust_neck,(1000, 400))
                print("[DEBUG Dough] Exhaust neck loaded")
            if os.path.exists(Constant.Exhaust_Mouth_IMAGE):
                self._exhaust_mouth = pygame.image.load(Constant.Exhaust_Mouth_IMAGE).convert_alpha()

                self._exhaust_mouth = pygame.transform.smoothscale(self._exhaust_mouth,(950, 350))
                print("[DEBUG Dough] Exhaust mouth loaded")
        else:
            print("[DEBUG Dough] Background not found")

    def update(self):
        mouse_pos = pygame.mouse.get_pos()

        self._Btn_Original.is_hovered = self._Btn_Original.hitbox.collidepoint(mouse_pos)
        self._Btn_Coklat.is_hovered = self._Btn_Coklat.hitbox.collidepoint(mouse_pos)
        self._Btn_Strawberry.is_hovered = self._Btn_Strawberry.hitbox.collidepoint(mouse_pos)

        if self._dough_entered and self._dough_y < self._target_y:
            self._dough_y += self._dough_speed
            if self._dough_y >= self._target_y:
                self._dough_y = self._target_y
                if self.cake and self.cake.flavor:
                    print(f"[DEBUG Dough] {self.cake.flavor.value} dough has fully entered the room")

    def exit(self):
        print("[DEBUG Dough] Exit room")

    def spawn_original(self):
        if self.cake.flavor is not None:
            return
        
        self.cake.set_flavor(Flavor.ORIGINAL)
        self._dough_image = pygame.image.load(Constant.Adonan_IMAGE).convert_alpha()
        self._dough_image = pygame.transform.smoothscale(
            self._dough_image, 
            (250,175))
        self._dough_entered = True
        self._dough_y = -200
        print("[DEBUG Dough] Spawn original dough")


    def spawn_coklat(self):
        if self.cake.flavor is not None:
            return
        print("[DEBUG Dough] Spawn chocolate dough")
        self.cake.set_flavor(Flavor.CHOCOLATE)
        self._dough_image = pygame.image.load(Constant.Adonan_Coklat_IMAGE).convert_alpha()
        self._dough_image = pygame.transform.smoothscale(
            self._dough_image,
            (250,175)
        )
        self._dough_entered = True
        self._dough_y = -300

    def spawn_strawberry(self):
        if self.cake.flavor is not None:
            return
        self.cake.set_flavor(Flavor.STRAWBERRY)
        print("[DEBUG Dough] Spawn strawberry dough")
        self._dough_image = pygame.image.load(Constant.Adonan_Strawberry_IMAGE).convert_alpha()
        self._dough_image = pygame.transform.smoothscale(
            self._dough_image,
            (250,175)
        )
        self._dough_entered = True
        self._dough_y = -300

    def _select_round(self):
        if self.cake.flavor is None:
            return
        if self.cake.mold is not None:
            return
        self.cake.set_mold(Mold.ROUND)
        self._mold_image = pygame.image.load(Constant.Cetakan_Round_IMAGE).convert_alpha()
        self._mold_image = pygame.transform.smoothscale(self._mold_image, (200, 200))
        self._mold_rect.topleft = (SCREEN_WIDTH // 2 - 100, 120)
        print("[DEBUG Dough] Round mold selected")

    def _select_heart(self):
        if self.cake.flavor is None:
            return
        if self.cake.mold is not None:
            return
        self.cake.set_mold(Mold.HEART)
        self._mold_image = pygame.image.load(Constant.Cetakan_Love_IMAGE).convert_alpha()
        self._mold_image = pygame.transform.smoothscale(self._mold_image, (200, 200))
        self._mold_rect.topleft = (SCREEN_WIDTH // 2 - 100, 120)
        print("[DEBUG Dough] Heart mold selected")

    def _select_star(self):
        if self.cake.flavor is None:
            return
        if self.cake.mold is not None:
            return
        self.cake.set_mold(Mold.STAR)
        self._mold_image = pygame.image.load(Constant.Cetakan_Star_IMAGE).convert_alpha()
        self._mold_image = pygame.transform.smoothscale(self._mold_image, (200, 200))
        self._mold_rect.topleft = (SCREEN_WIDTH // 2 - 100, 120)
        print("[DEBUG Dough] Star mold selected")

    def draw_Hover(self,rect):
        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, 100))
        self.screen.blit(overlay, rect.topleft)

    def render(self):
        if not self.screen:
            return

        if self._bg_image:
            self.screen.blit(self._bg_image, (0, Constant.NAV_BAR_HEIGHT))
            if self._dough_image and self._dough_entered:
                self.screen.blit(self._dough_image, (self._dough_x, self._dough_y))
            if self._exhaust_neck:
                self.screen.blit(self._exhaust_neck,(SCREEN_WIDTH // 2 - 488,Constant.NAV_BAR_HEIGHT - 300))

            if self._exhaust_mouth:
                self.screen.blit(self._exhaust_mouth,(SCREEN_WIDTH // 2 - 475,Constant.NAV_BAR_HEIGHT - 40))

            self._Btn_Original.render(self.screen)
            self._Btn_Coklat.render(self.screen)
            self._Btn_Strawberry.render(self.screen)

        else:
            self.screen.fill(COLOR_BG_CREAM)

            title = self._font_heading.render(
                "~ Dough Room ~",
                True,
                COLOR_DARK_BROWN
            )
            self.screen.blit(
                title,
                title.get_rect(
                    centerx=SCREEN_WIDTH // 2,
                    centery=SCREEN_HEIGHT // 2
                )
            )
        if self._mold_image:
            img_rect = self._mold_image.get_rect(center=self._mold_rect.center)
            self.screen.blit(self._mold_image, img_rect.topleft)

        if self._Btn_Original.is_hovered:
            self.draw_Hover(self._Btn_Original.hitbox)
        if self._Btn_Coklat.is_hovered:
            self.draw_Hover(self._Btn_Coklat.hitbox)
        if self._Btn_Strawberry.is_hovered:
            self.draw_Hover(self._Btn_Strawberry.hitbox)

    def cut_dough(self):
        path = RAW_CAKE.get((self.cake.flavor, self.cake.mold))
        if path:
            self._dough_image = pygame.image.load(path).convert_alpha()
            self._dough_image = pygame.transform.smoothscale(self._dough_image, (250, 175))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if self._Btn_Original.hitbox.collidepoint(event.pos):
                self.spawn_original()
            if self._Btn_Coklat.hitbox.collidepoint(event.pos):
                self.spawn_coklat()
            if self._Btn_Strawberry.hitbox.collidepoint(event.pos):
                self.spawn_strawberry()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

            if self._Cetakan_Star.collidepoint(event.pos):
                print("STAR HIBOX")
                self._select_star()
                print("[DEBUG Dough] Star mold selected")

            if self._Cetakan_Love.collidepoint(event.pos):
                print("HEART HIBOX")
                self._select_heart()
                print("[DEBUG Dough] Heart mold selected")

            if self._Cetakan_Round.collidepoint(event.pos):
                print("ROUND HIBOX")
                self._select_round()
                print("[DEBUG Dough] Round mold selected")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self._mold_image and self._mold_rect.collidepoint(event.pos):
                self._Dragging = True
                self._offset_x = self._mold_rect.x - event.pos[0]
                self._offset_y = self._mold_rect.y - event.pos[1]
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._Dragging = False

        if event.type == pygame.MOUSEMOTION:
            if self._Dragging:
                self._mold_rect.x = event.pos[0] + self._offset_x
                self._mold_rect.y = event.pos[1] + self._offset_y

                if self._mold_rect.colliderect(self._cut_Area) and not self._Dough_Cut:
                    print("[DEBUG Dough] Dough cut!")
                    self.cut_dough()
                    self._mold_image = None
                    self._Dragging = False
                    self._Dough_Cut = True
                    print("[DEBUG Dough] Cake is now cut and ready for the next step")
                    if hasattr(self, "_scene_manager"):
                        self._scene_manager.transition_to("RoomBaking")