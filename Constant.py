import os

SCREEN_WIDTH  = 1024
SCREEN_HEIGHT = 768
FPS           = 60
GAME_TITLE    = "Cozy Bakery"

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

MAINMENU_BG       = os.path.join(ASSETS_DIR, "background.png")
BTN_PLAY          = os.path.join(ASSETS_DIR, "btn_play.png")
BTN_PLAY_HOVER    = os.path.join(ASSETS_DIR, "btn_play_hover.png")
BTN_CREDIT        = os.path.join(ASSETS_DIR, "btn_credit.png")
BTN_CREDIT_HOVER  = os.path.join(ASSETS_DIR, "btn_credit_hover.png")
BTN_EXIT          = os.path.join(ASSETS_DIR, "btn_exit.png")
BTN_EXIT_HOVER    = os.path.join(ASSETS_DIR, "btn_exit_hover.png")

COLOR_BG_CREAM      = (255, 248, 231)
COLOR_WARM_BROWN    = (139, 90, 43)
COLOR_LIGHT_BROWN   = (194, 143, 92)
COLOR_DARK_BROWN    = (80, 50, 20)
COLOR_PINK_ACCENT   = (255, 183, 165)
COLOR_WHITE         = (255, 255, 255)
COLOR_BLACK         = (0, 0, 0)

FONT_NAME          = None
FONT_TITLE_SIZE    = 56
FONT_BODY_SIZE     = 24
FONT_SMALL_SIZE    = 18

NAV_BAR_HEIGHT     = 50
NAV_BUTTON_WIDTH   = 160
NAV_BUTTON_HEIGHT  = 40

TRANSITION_SPEED   = 6

DEBUG_NAV_UI       = True   
