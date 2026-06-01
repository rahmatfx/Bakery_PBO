import pygame, os, sys
from Room.Room import Room
from Constant import SCREEN_WIDTH, SCREEN_HEIGHT, BAKING_BG, COLOR_BG_CREAM, COLOR_DARK_BROWN, FONT_HEADING_SIZE, FONT_BODY_SIZE, FONT_NAME, OVEN_CLOSE_IMAGE, OVEN_OPEN_IMAGE, OVEN_BAKE_IMAGE, ADONAN_TEMPORARY, CAKE_TEMPORARY, NAMPAN_IMAGE
from Order.Cake import Cake

class BakingRoom(Room):
    def __init__(self):
        super().__init__(name="Baking")
        self._bg_image = None
        self._oven_image = None
        self._oven_image_opening = None
        self._oven_bake_image = None
        self._font_heading = pygame.font.SysFont(FONT_NAME, FONT_HEADING_SIZE)
        self._font_body = pygame.font.SysFont(FONT_NAME, FONT_BODY_SIZE)
        self._oven_rect = None
        self._oven_size = None
        self._adonan_rect = None
        self._adonan_image = None
        self._oven_isOpen = False
        self._button_bake_rect = None
        self._doughInOven = False
        self.bakeDough = False
        self.doughInFront = False
        self.isDragging = False
        self.isShowText = False
        self.text_surface = None
        self.game_font = None
        self.text_rect = None
        self.bake_start_time = pygame.time.get_ticks()
        self.elapsed = 0
        self.bake_start_time = 5
        self.bake_duration = 5
        self.rect_posAwalDough = None
        self.rect_posOvenDough = None
        self.isBaked = False
        self.cake_image = None
        self.isReadyToTake = False
        self.nampan_image = None
        self.isInNampan = False

        self.cake: Cake = None

    def enter(self):
        if os.path.exists(BAKING_BG):
            self._bg_image = pygame.transform.smoothscale(
                pygame.image.load(BAKING_BG).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        if os.path.exists(NAMPAN_IMAGE):
            img = pygame.image.load(NAMPAN_IMAGE).convert_alpha()
            original_width, original_height = img.get_size()
            new_width = 150
            new_height = int(original_height * (new_width / original_width))
            self.nampan_image = pygame.transform.smoothscale(img, (new_width, new_height))
            
        if os.path.exists(ADONAN_TEMPORARY):
            img = pygame.image.load(ADONAN_TEMPORARY).convert_alpha()
            original_width, original_height = img.get_size()
            new_width = 150
            new_height = int(original_height * (new_width / original_width))
            self._adonan_image = pygame.transform.smoothscale(img, (new_width, new_height))

        if os.path.exists(CAKE_TEMPORARY):
            img = pygame.image.load(CAKE_TEMPORARY).convert_alpha()
            original_width, original_height = img.get_size()
            new_width = 150
            new_height = int(original_height * (new_width / original_width))
            self.cake_image = pygame.transform.smoothscale(img, (new_width, new_height))
            
          # Load oven image
        if os.path.exists(OVEN_CLOSE_IMAGE):
            img = pygame.image.load(OVEN_CLOSE_IMAGE).convert_alpha()  # convert_alpha untuk transparency
            # Scale sesuai kebutuhan, misal jadi lebar 200px dengan aspect ratio tetap
            original_width, original_height = img.get_size()
            new_width = 520
            new_height = int(original_height * (new_width / original_width))
            self._oven_image = pygame.transform.smoothscale(img, (new_width, new_height))

            self._oven_size = self._oven_image.get_rect(
                centerx=SCREEN_WIDTH - 550,
                bottom=SCREEN_HEIGHT + 5
            )

            self._oven_rect = pygame.Rect(530, 420, 400, 270)

            #gambar oven buka
        if os.path.exists(OVEN_OPEN_IMAGE):
            img = pygame.image.load(OVEN_OPEN_IMAGE).convert_alpha()
            original_width, original_height = img.get_size()
            new_width = 520
            new_height = int(original_height * (new_width / original_width))
            self._oven_image_opening = pygame.transform.smoothscale(img, (new_width, new_height))

        if os.path.exists(OVEN_BAKE_IMAGE):
            img = pygame.image.load(OVEN_BAKE_IMAGE).convert_alpha()
            original_width, original_height = img.get_size()
            new_width = 520
            new_height = int(original_height * (new_width / original_width))
            self._oven_bake_image = pygame.transform.smoothscale(img, (new_width, new_height))
        
        #self.cake.mold

        if self._adonan_image:
            self._adonan_rect = self._adonan_image.get_rect(
                centerx=SCREEN_WIDTH - 1000,
                bottom=SCREEN_HEIGHT - 350
            )
        
        self._button_bake_rect = pygame.Rect(910, 340, 50, 50)

        self.rect_posAwalDough = pygame.Rect(250, 280, 50, 50)

        self.rect_posOvenDough = pygame.Rect(710, 600, 50, 50)


        YELLOW = (255, 255, 59)
        self.game_font = pygame.font.SysFont("Orbitron.ttf", 30, True)
        self.text_surface = self.game_font.render("Hello World!", True, YELLOW)
        self.text_rect = pygame.Rect(825, 355, 50, 50)

            
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                
                if self._oven_rect and self._oven_rect.collidepoint(mouse_pos):
                    if not self.bakeDough and (not self._doughInOven or self.isReadyToTake):
                        if self.isReadyToTake and not self._oven_isOpen:
                            self._oven_isOpen = True
                            self._doughInOven = False
                            self._adonan_rect.center = self.rect_posOvenDough.center

                        elif not self.isReadyToTake:
                            self._oven_isOpen = not self._oven_isOpen
                            if not self._oven_isOpen and self.doughInFront:
                                self._doughInOven = True
                
                if self._adonan_rect and self._adonan_rect.collidepoint(mouse_pos):
                    if not self._doughInOven or self.isReadyToTake:
                        self.isDragging = True

                if self._button_bake_rect and self._button_bake_rect.collidepoint(mouse_pos):
                    if not self._oven_isOpen and self._doughInOven and not self.bakeDough:
                        print("bake dough :  + {self.bakeDough} ")
                        self.bakeDough = True
                        self.isShowText = True  
                        self.bake_start_time = pygame.time.get_ticks()
                        print(self.isShowText)


        if event.type == pygame.MOUSEMOTION:
            if self.isDragging:
                self._adonan_rect.center = event.pos

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.isDragging = False
                if not (self._oven_isOpen and self._adonan_rect.colliderect(self._oven_rect)):
                    self._adonan_rect.center = self.rect_posAwalDough.center
                    if self.isReadyToTake:
                        self.isInNampan = True
                        print("Kue Masuk Nampan") 
                        if self.isInNampan:
                            self.doughInFront = False
                            self._doughInOven = False
                            self.bakeDough = False
                            self.isReadyToTake = False
                if (self._oven_isOpen and self._adonan_rect.colliderect(self._oven_rect)):
                    self._adonan_rect.center = self.rect_posOvenDough.center 
        

    def mekanik(self):
        if self._adonan_rect and self._adonan_rect.colliderect(self._oven_rect):
            if  self._oven_isOpen and not self.isDragging:
                self.doughInFront = True
                print("Adonan berhasil masuk")
            
            

    def update(self):
        self.mekanik()
        if self.bakeDough:
            self.elapsed = (pygame.time.get_ticks() - self.bake_start_time) // 1000
            self.elapsed = self.bake_duration - self.elapsed
            if self.elapsed <= 0: 
                print("Kue matang!")
                self.bakeDough = False
                self.isBaked = True
                self.isReadyToTake = True
                

    def render(self):
        if not self.screen: return
        if self._bg_image:
            self.screen.blit(self._bg_image, (0, 0))
        else:
            self.screen.fill(COLOR_BG_CREAM)
            t = self._font_heading.render("~ Cashier ~", True, COLOR_DARK_BROWN)
            self.screen.blit(t, t.get_rect(centerx=SCREEN_WIDTH//2, centery=SCREEN_HEIGHT//3))

        if self._oven_size:
            if self._oven_isOpen and self._oven_image_opening:
                self.screen.blit(self._oven_image_opening, self._oven_size)
            elif self._oven_image:
                self.screen.blit(self._oven_image, self._oven_size)

        if self._oven_bake_image and self.bakeDough:
            self.screen.blit(self._oven_bake_image, self._oven_size)
        
        if self.nampan_image:
            self.nampan_image = pygame.transform.scale(self.nampan_image, (300,410))
            self.screen.blit(self.nampan_image, (120,120))

        if not self._doughInOven and self.isBaked and self.cake_image:
            self.screen.blit(self.cake_image, self._adonan_rect)
        elif not self._doughInOven and not self.isBaked and self._adonan_image:
            self.screen.blit(self._adonan_image, self._adonan_rect)

        if self._oven_rect:
            pygame.draw.rect(self.screen, (255, 0, 0), self._oven_rect, 2)  # Kotak merah

        if self._button_bake_rect:
            pygame.draw.rect(self.screen, (25, 52, 224), self._button_bake_rect, 2)  

        if self._adonan_rect:
            pygame.draw.rect(self.screen, (25, 52, 224), self._adonan_rect, 2)
        
        if self.rect_posAwalDough:
            pygame.draw.rect(self.screen, (25, 52, 224), self.rect_posAwalDough, 2)

        if self.rect_posOvenDough:
            pygame.draw.rect(self.screen, (25, 52, 224), self.rect_posOvenDough, 2)

        
        if self.isShowText:
            if self.bakeDough:
                self.text_surface = self.game_font.render(f"{self.elapsed}", True, (255, 255, 59))
                self.screen.blit(self.text_surface, self.text_rect)

    # def handle_event(self, event): pass