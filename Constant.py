import os

SCREEN_WIDTH  = 1280
SCREEN_HEIGHT = 720
FPS           = 60
GAME_TITLE    = "Cozy Bakery"

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "Assets")
DATA_DIR   = os.path.join(BASE_DIR, "Data")
SAVE_FILE = os.path.join(DATA_DIR, "save.json")

# Audio
AUDIO_DIR = os.path.join(ASSETS_DIR, "Audio")
BGM_DIR   = os.path.join(AUDIO_DIR, "BGM")
SFX_DIR   = os.path.join(AUDIO_DIR, "SFX")

BGM_VOLUME = 0.5
SFX_VOLUME = 0.7
TYPEWRITER_SFX_COOLDOWN = 0.06

# BGM files
BGM_MAIN_MENU  = os.path.join(BGM_DIR, "main_menu.mp3")
BGM_CASHIER    = os.path.join(BGM_DIR, "cashier.ogg")
BGM_DOUGH      = os.path.join(BGM_DIR, "dough.ogg")
BGM_BAKING     = os.path.join(BGM_DIR, "baking.ogg")
BGM_DECORATION = os.path.join(BGM_DIR, "decoration.ogg")

# SFX files
SFX_DIALOGUE_TYPE  = os.path.join(SFX_DIR, "dialogue_type.ogg")
SFX_DIALOGUE_CLICK = os.path.join(SFX_DIR, "dialogue_click.ogg")
SFX_EMOJI_POPUP    = os.path.join(SFX_DIR, "emoji_popup.ogg")
SFX_ORDER_NEW      = os.path.join(SFX_DIR, "order_new.ogg")
SFX_ORDER_CORRECT  = os.path.join(SFX_DIR, "order_correct.ogg")
SFX_ORDER_WRONG    = os.path.join(SFX_DIR, "order_wrong.ogg")
SFX_NAV_CLICK      = os.path.join(SFX_DIR, "nav_click.ogg")
SFX_AFFINITY_UP    = os.path.join(SFX_DIR, "affinity_up.ogg")
SFX_TIMER_URGENT   = os.path.join(SFX_DIR, "timer_urgent.ogg")

# Animation
ANIM_SHAKE_INTENSITY = 6
ANIM_SHAKE_DURATION  = 0.3
ANIM_SHAKE_FREQUENCY = 40.0

ANIM_POP_DURATION    = 0.25

ANIM_BOUNCE_HEIGHT   = 10
ANIM_BOUNCE_DURATION = 0.4
ANIM_BOUNCE_FREQUENCY = 12.0

ANIM_SLIDE_DURATION  = 0.5

# Backgrounds
MAINMENU_BG       = os.path.join(ASSETS_DIR, "background.png")
CASHIER_BG        = os.path.join(ASSETS_DIR, "cashier_bg.png")
BAKING_BG         = os.path.join(ASSETS_DIR, "BakingRoom.png")
DEKORASI_BG       = os.path.join(ASSETS_DIR, "dekorasi_bg.png")
DOUGH_BG          = os.path.join(ASSETS_DIR, "dough room.jpeg")

# Main Menu Buttons
BTN_PLAY          = os.path.join(ASSETS_DIR, "btn_play.png")
BTN_PLAY_HOVER    = os.path.join(ASSETS_DIR, "btn_play_hover.png")
BTN_CREDIT        = os.path.join(ASSETS_DIR, "btn_credit.png")
BTN_CREDIT_HOVER  = os.path.join(ASSETS_DIR, "btn_credit_hover.png")
BTN_EXIT          = os.path.join(ASSETS_DIR, "btn_exit.png")
BTN_EXIT_HOVER    = os.path.join(ASSETS_DIR, "btn_exit_hover.png")

Adonan_IMAGE = os.path.join(ASSETS_DIR, "Original_Dough.png")
Adonan_Coklat_IMAGE = os.path.join(ASSETS_DIR, "Coklat_Dough.PNG")
Adonan_Strawberry_IMAGE = os.path.join(ASSETS_DIR, "Strawberry_Dough.PNG")
Exhaust_Neck_IMAGE = os.path.join(ASSETS_DIR,"Exhaust_Leher.PNG")
Exhaust_Mouth_IMAGE = os.path.join(ASSETS_DIR,"Exhaust_Mulut.PNG")
BTN_Original_IMAGE = os.path.join(ASSETS_DIR, "original_button.png")
BTN_Coklat_IMAGE = os.path.join(ASSETS_DIR, "coklat_button.png")
BTN_Strawberry_IMAGE = os.path.join(ASSETS_DIR, "strawberry_button.png")

# Decoration Room Images
berries_decor_IMAGE = os.path.join(ASSETS_DIR, "berriesBowl.png")
berries_hover_IMAGE = os.path.join(ASSETS_DIR, "berriesHover.png")
chocochip_decor_IMAGE = os.path.join(ASSETS_DIR, "chocochipsBowl.png")
chocochip_hover_IMAGE = os.path.join(ASSETS_DIR, "chocochipsHover.png")
cream_decor_IMAGE = os.path.join(ASSETS_DIR, "creamBowl.png")
cream_hover_IMAGE = os.path.join(ASSETS_DIR, "creamHover.png")
oreo_decor_IMAGE = os.path.join(ASSETS_DIR, "oreoBowl.png")
oreo_hover_IMAGE = os.path.join(ASSETS_DIR, "oreoHover.png")
sprinkles_decor_IMAGE = os.path.join(ASSETS_DIR, "sprinklesBottle.png")
sprinkles_hover_IMAGE = os.path.join(ASSETS_DIR, "sprinklesHover.png")
berriesTop = os.path.join(ASSETS_DIR, "berriesTop.png")
creamTop = os.path.join(ASSETS_DIR, "creamTop.png")
oreoTop = os.path.join(ASSETS_DIR, "oreoTop.png")
sprinklesHeart = os.path.join(ASSETS_DIR, "sprinklesHeart.png")
sprinklesStar = os.path.join(ASSETS_DIR, "sprinklesStar.png")
sprinklesRound = os.path.join(ASSETS_DIR, "sprinklesRound.png")
chocoHeart = os.path.join(ASSETS_DIR, "chocoHeart.png")
chocoStar = os.path.join(ASSETS_DIR, "chocoStar.png")
chocoRound = os.path.join(ASSETS_DIR, "chocoRound.png")

# Oven Images
OVEN_OPEN_IMAGE  = os.path.join(ASSETS_DIR, "OvenBuka.png")
OVEN_CLOSE_IMAGE = os.path.join(ASSETS_DIR, "OvenTutup.png")
OVEN_BAKE_IMAGE  = os.path.join(ASSETS_DIR, "OvenMemanggang.png")
ADONAN_TEMPORARY = os.path.join(ASSETS_DIR, "AdonanTemp.png")
CAKE_TEMPORARY = os.path.join(ASSETS_DIR, "Cake.png")
NAMPAN_IMAGE = os.path.join(ASSETS_DIR, "Nampan.png")

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
HEART_IMG          = os.path.join(ASSETS_DIR, "heart.png")

# NPC Position
NPC_X              = 50
NPC_Y              = NAV_BAR_HEIGHT + 80
NPC_WIDTH          = 300
NPC_HEIGHT         = 400
NPC_SLIDE_SPEED    = 8

# Expression Images (fallback)
NPC_EMOJI_HAPPY    = os.path.join(ASSETS_DIR, "emoji_happy.png")
NPC_EMOJI_ANGRY    = os.path.join(ASSETS_DIR, "emoji_angry.png")

# Expression Size
EXPR_WIDTH         = 80
EXPR_HEIGHT        = 80

# Expression Fallback Colors
COLOR_EXPR_HAPPY_FALLBACK   = (0, 180, 0)
COLOR_EXPR_ANGRY_FALLBACK   = (220, 50, 50)
COLOR_EXPR_NEUTRAL_FALLBACK = (180, 180, 180)

# Emoji Popup
EMOJI_POPUP_SPEED  = 4
EMOJI_POPUP_OFFSET_Y = 20

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
AFFINITY_BAR_OFFSET_X = 10
AFFINITY_BAR_OFFSET_Y = 12
AFFINITY_TEXT_GAP = 8
AFFINITY_PANEL_PADDING = 8
AFFINITY_SHADOW_OFFSET = 2

# NPC Expression Colors (fallback rect)
COLOR_NPC_HAPPY   = (100, 200, 100)
COLOR_NPC_ANGRY   = (220, 80, 80)

# NPC Shadow
SHADOW_OFFSET     = 4
NPC_FALLBACK_SHADOW_OFFSET = 4

# Cashier Reaction
REWARD_CORRECT_CAKE = 1
PENALTY_WRONG_CAKE  = -2
PENALTY_TIMER_EXPIRED = -2
PREF_SCORE_GREAT = 2
PREF_SCORE_GOOD  = 1
PREF_SCORE_LIKED = 1
PREF_SCORE_DISLIKED = -1

# Cake Options
CAKE_OPTION_RANDOM_COUNT = 3

# Cashier Render
COLOR_CASHIER_FALLBACK_BG = (255, 235, 210)
HINT_CLICK_OFFSET_Y = 20

# DialogueBox Render
DIALOGUE_SHADOW_OFFSET = 3
DIALOGUE_NAME_TAG_PADDING_X = 12
DIALOGUE_NAME_TAG_PADDING_Y = 4
DIALOGUE_NAME_TAG_INNER_PAD = 24
DIALOGUE_TEXT_EXTRA_OFFSET = 10
DIALOGUE_TEXT_WIDTH_MARGIN = 20
DIALOGUE_HINT_OFFSET_X = 180
DIALOGUE_HINT_OFFSET_Y = 28
DIALOGUE_CHOICE_OVERLAY_ALPHA = 120

# OrderUI Render
ORDER_UI_SHADOW_OFFSET = 4
ORDER_UI_SHADOW_ALPHA  = 60
ORDER_UI_HEADER_HEIGHT = 44
ORDER_UI_HEADER_INSET  = 3
ORDER_UI_TITLE_OFFSET_X = 18
ORDER_UI_TITLE_OFFSET_Y = 8
ORDER_UI_DIVIDER_Y_OFFSET = 50
ORDER_UI_DIVIDER_PADDING_X = 15
ORDER_UI_NAME_OFFSET_X = 20
ORDER_UI_NAME_OFFSET_Y = 60
ORDER_UI_PERSONALITY_OFFSET_Y = 90
ORDER_UI_PERSONALITY_LINE_HEIGHT = 20
ORDER_UI_PERSONALITY_MAX_LINES = 3
ORDER_UI_PERSONALITY_PADDING = 40
ORDER_UI_BTN_WIDTH  = 150
ORDER_UI_BTN_HEIGHT = 42
ORDER_UI_BTN_BOTTOM_PADDING = 14
ORDER_UI_BTN_SHADOW_OFFSET = 2
ORDER_UI_BTN_SHADOW_ALPHA  = 40
ORDER_UI_ACCEPTED_COLOR = (80, 180, 80)
ORDER_UI_TIMER_URGENT_COLOR = (255, 100, 100)
ORDER_UI_TIMER_URGENT_THRESHOLD = 10
ORDER_UI_DETAIL_ROW_START_Y = 60
ORDER_UI_DETAIL_ROW_SPACING = 34
ORDER_UI_DETAIL_LABEL_X = 20
ORDER_UI_DETAIL_VALUE_X = 110
ORDER_UI_DETAIL_LABELS = ["Flavor:", "Mold:", "Top:"]
ORDER_UI_TIMER_OFFSET_X = 95
ORDER_UI_TIMER_OFFSET_Y = 16

# Debug 
DEBUG_NAV_UI       = False