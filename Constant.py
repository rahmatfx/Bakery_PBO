import os

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS           = 60
GAME_TITLE    = "Cozy Bakery"

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")

MAINMENU_BG       = os.path.join(ASSETS_DIR, "background.png")
CASHIER_BG       = os.path.join(ASSETS_DIR, "cashier_bg.png")
BAKING_BG       = os.path.join(ASSETS_DIR, "BakingRoom.png")
DEKORASI_BG      = os.path.join(ASSETS_DIR, "dekorasi_bg.png")
DOUGH_BG          = os.path.join(ASSETS_DIR, "dough room.jpeg")
BTN_PLAY          = os.path.join(ASSETS_DIR, "btn_play.png")
BTN_PLAY_HOVER    = os.path.join(ASSETS_DIR, "btn_ply_hover.png")
BTN_CREDIT        = os.path.join(ASSETS_DIR, "btn_credit.png")
BTN_CREDIT_HOVER  = os.path.join(ASSETS_DIR, "btn_crdit_hover.png")
BTN_EXIT          = os.path.join(ASSETS_DIR, "btn_exit.png")
BTN_EXIT_HOVER    = os.path.join(ASSETS_DIR, "btn_ext_hover.png")
Adonan_IMAGE = os.path.join(ASSETS_DIR, "Original_Dough.png")
Adonan_Coklat_IMAGE = os.path.join(ASSETS_DIR, "Coklat_Dough.PNG")
Adonan_Strawberry_IMAGE = os.path.join(ASSETS_DIR, "Strawberry_Dough.PNG")
Exhaust_Neck_IMAGE = os.path.join(ASSETS_DIR,"Exhaust_Leher.PNG")
Exhaust_Mouth_IMAGE = os.path.join(ASSETS_DIR,"Exhaust_Mulut.PNG")

OVEN_OPEN_IMAGE = os.path.join(ASSETS_DIR, "OvenBuka.png")
OVEN_CLOSE_IMAGE = os.path.join(ASSETS_DIR, "OvenTutup.png")
OVEN_BAKE_IMAGE = os.path.join(ASSETS_DIR, "OvenMemanggang.png")

NAV_BAR_BG       = os.path.join(ASSETS_DIR, "nav_br_bg.png")
NAV_BTN_NORMAL   = os.path.join(ASSETS_DIR, "nav_bn.png")
NAV_BTN_HOVER    = os.path.join(ASSETS_DIR, "nav_bn_hover.png")
NAV_BTN_ACTIVE   = os.path.join(ASSETS_DIR, "nav_bn_active.png")

NAV_BAR_X         = 0
NAV_BAR_Y         = 0
NAV_BAR_WIDTH     = SCREEN_WIDTH         
NAV_BAR_HEIGHT    = 70
NAV_BUTTON_WIDTH  = 160
NAV_BUTTON_HEIGHT = 40
NAV_BTN_SPACING   = 20

COLOR_BG_CREAM      = (255, 248, 231)
COLOR_WARM_BROWN    = (139, 90, 43)
COLOR_LIGHT_BROWN   = (194, 143, 92)
COLOR_DARK_BROWN    = (80, 50, 20)
COLOR_PINK_ACCENT   = (255, 183, 165)
COLOR_WHITE         = (255, 255, 255)
COLOR_BLACK         = (0, 0, 0)

FONT_NAME          = None
FONT_TITLE_SIZE    = 56
FONT_HEADING_SIZE  = 36
FONT_BODY_SIZE     = 24
FONT_SMALL_SIZE    = 18

TRANSITION_SPEED   = 6

DEBUG_NAV_UI       = False  

TIMER_DURATION = 60  

NPC_IMG            = os.path.join(ASSETS_DIR, "Mimosa.png")
NPC_EMOJI_HAPPY    = os.path.join(ASSETS_DIR, "emoji_happy.png")
NPC_EMOJI_ANGRY    = os.path.join(ASSETS_DIR, "emoji_angry.png")

NPC_X              = 50
NPC_Y              = NAV_BAR_HEIGHT + 80
NPC_WIDTH          = 300
NPC_HEIGHT         = 400
NPC_SLIDE_SPEED    = 8

EMOJI_WIDTH        = 80
EMOJI_HEIGHT       = 80
EMOJI_POPUP_SPEED  = 4

ORDER_UI_WIDTH     = 320
ORDER_UI_HEIGHT    = 200
ORDER_UI_OFFSET_X  = 30
ORDER_UI_OFFSET_Y  = 20