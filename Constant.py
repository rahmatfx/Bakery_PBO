import os

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS           = 60
GAME_TITLE    = "Cozy Bakery"

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
DATA_DIR   = os.path.join(BASE_DIR, "Data")
SAVE_FILE = os.path.join(DATA_DIR, "save.json")

# Backgrounds
MAINMENU_BG       = os.path.join(ASSETS_DIR, "background.png")
CASHIER_BG        = os.path.join(ASSETS_DIR, "cashier_bg.png")
BAKING_BG         = os.path.join(ASSETS_DIR, "BakingRoom.png")
DEKORASI_BG       = os.path.join(ASSETS_DIR, "dekorasi_bg.png")
DOUGH_BG          = os.path.join(ASSETS_DIR, "dough room.jpeg")

# Main Menu Buttons
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
BTN_Original_IMAGE = os.path.join(ASSETS_DIR, "original_button.png")
BTN_Coklat_IMAGE = os.path.join(ASSETS_DIR, "coklat_button.png")
BTN_Strawberry_IMAGE = os.path.join(ASSETS_DIR, "strawberry_button.png")

# Oven Images
OVEN_OPEN_IMAGE  = os.path.join(ASSETS_DIR, "OvenBuka.png")
OVEN_CLOSE_IMAGE = os.path.join(ASSETS_DIR, "OvenTutup.png")
OVEN_BAKE_IMAGE  = os.path.join(ASSETS_DIR, "OvenMemanggang.png")

# Navigation Bar 
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

# Colors 
COLOR_BG_CREAM      = (255, 248, 231)
COLOR_WARM_BROWN    = (139, 90, 43)
COLOR_LIGHT_BROWN   = (194, 143, 92)
COLOR_DARK_BROWN    = (80, 50, 20)
COLOR_PINK_ACCENT   = (255, 183, 165)
COLOR_WHITE         = (255, 255, 255)
COLOR_BLACK         = (0, 0, 0)
COLOR_HEART_RED     = (220, 60, 80)

# Fonts 
FONT_NAME          = None
FONT_TITLE_SIZE    = 56
FONT_HEADING_SIZE  = 36
FONT_BODY_SIZE     = 24
FONT_SMALL_SIZE    = 18

# Transitions
TRANSITION_SPEED   = 6

# Timer 
TIMER_DURATION = 60

# NPC (Fallback)
NPC_IMG            = os.path.join(ASSETS_DIR, "Mimosa.png")
NPC_EMOJI_HAPPY    = os.path.join(ASSETS_DIR, "emoji_happy.png")
NPC_EMOJI_ANGRY    = os.path.join(ASSETS_DIR, "emoji_angry.png")
HEART_IMG          = os.path.join(ASSETS_DIR, "heart.png")

NPC_X              = 50
NPC_Y              = NAV_BAR_HEIGHT + 80
NPC_WIDTH          = 300
NPC_HEIGHT         = 400
NPC_SLIDE_SPEED    = 8

EMOJI_WIDTH        = 80
EMOJI_HEIGHT       = 80
EMOJI_POPUP_SPEED  = 4

# Order UI 
ORDER_UI_WIDTH     = 320
ORDER_UI_HEIGHT    = 200
ORDER_UI_OFFSET_X  = 30
ORDER_UI_OFFSET_Y  = 20

# Dialogue Box
DIALOGUE_BOX_HEIGHT = 250
DIALOGUE_MARGIN_BOTTOM = 50
DIALOGUE_BOX_Y     = SCREEN_HEIGHT - DIALOGUE_BOX_HEIGHT - DIALOGUE_MARGIN_BOTTOM
DIALOGUE_MARGIN_X  = 30
DIALOGUE_PADDING   = 16
DIALOGUE_NAME_TAG_HEIGHT = 36
DIALOGUE_TEXT_AREA_HEIGHT = 100
DIALOGUE_TEXT_SIZE  = 22
DIALOGUE_CHOICE_SIZE = 20
DIALOGUE_BG_COLOR  = (255, 245, 230)
TYPEWRITER_SPEED   = 2

# Choice Center 
CHOICE_CENTER_WIDTH      = 600
CHOICE_CENTER_HEIGHT     = 55
CHOICE_CENTER_SPACING    = 14
CHOICE_CENTER_FONT_SIZE  = 24

# Cake Selection UI
CAKE_SELECT_CARD_WIDTH    = 200
CAKE_SELECT_CARD_HEIGHT   = 260
CAKE_SELECT_CARD_SPACING  = 20
CAKE_SELECT_CARD_RADIUS   = 12
CAKE_SELECT_TITLE_SIZE    = 32
CAKE_SELECT_TEXT_SIZE     = 20
CAKE_SELECT_LABEL_SIZE    = 16
CAKE_SELECT_OVERLAY_ALPHA = 160
CAKE_SELECT_TITLE_Y       = 120

# Affinity Display 
AFFINITY_HEART_SIZE = 50
AFFINITY_FONT_SIZE  = 20

# Debug 
DEBUG_NAV_UI       = False