import pygame
import os
import Constant


class AudioManager:

    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2,
                              buffer=512)

        self._bgm_registry: dict[str, str] = {}
        self._sfx_registry: dict[str, str] = {}
        self._sfx_cache: dict[str, pygame.mixer.Sound] = {}

        self._current_bgm_key: str = ""
        self._bgm_volume: float = Constant.BGM_VOLUME
        self._sfx_volume: float = Constant.SFX_VOLUME

        # typewriter cooldown
        self._type_cooldown: float = 0.0
        self._type_cooldown_max: float = Constant.TYPEWRITER_SFX_COOLDOWN

        pygame.mixer.music.set_volume(self._bgm_volume)

    # Register

    def register_bgm(self, key: str, filepath: str) -> None:
        self._bgm_registry[key] = filepath

    def register_sfx(self, key: str, filepath: str) -> None:
        self._sfx_registry[key] = filepath
        if os.path.exists(filepath):
            try:
                self._sfx_cache[key] = pygame.mixer.Sound(filepath)
                self._sfx_cache[key].set_volume(self._sfx_volume)
            except pygame.error as e:
                print(f"[AudioManager] Gagal load SFX '{key}': {e}")
        else:
            print(f"[AudioManager] SFX file tidak ditemukan: {filepath}")

    def register_defaults(self) -> None:
        self.register_bgm("main_menu", Constant.BGM_MAIN_MENU)
        self.register_bgm("cashier", Constant.BGM_CASHIER)
        self.register_bgm("dough", Constant.BGM_DOUGH)
        self.register_bgm("baking", Constant.BGM_BAKING)
        self.register_bgm("decoration", Constant.BGM_DECORATION)

        self.register_sfx("dialogue_type", Constant.SFX_DIALOGUE_TYPE)
        self.register_sfx("dialogue_click", Constant.SFX_DIALOGUE_CLICK)
        self.register_sfx("emoji_popup", Constant.SFX_EMOJI_POPUP)
        self.register_sfx("order_new", Constant.SFX_ORDER_NEW)
        self.register_sfx("order_correct", Constant.SFX_ORDER_CORRECT)
        self.register_sfx("order_wrong", Constant.SFX_ORDER_WRONG)
        self.register_sfx("nav_click", Constant.SFX_NAV_CLICK)
        self.register_sfx("affinity_up", Constant.SFX_AFFINITY_UP)
        self.register_sfx("timer_urgent", Constant.SFX_TIMER_URGENT)
        self.register_sfx("happy_sfx", Constant.HAPPY_SFX)
        self.register_sfx("sad_sfx", Constant.SAD_SFX)
        self.register_sfx("angry_sfx", Constant.ANGRY_SFX)
        self.register_sfx("baka", Constant.BAKA)

    # BGM

    def play_bgm(self, key: str, loops: int = -1) -> None:
        if key == self._current_bgm_key and pygame.mixer.music.get_busy():
            return

        filepath = self._bgm_registry.get(key)
        if not filepath:
            print(f"[AudioManager] BGM key '{key}' tidak terdaftar")
            return

        if not os.path.exists(filepath):
            print(f"[AudioManager] BGM file tidak ditemukan: {filepath}")
            return

        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.set_volume(self._bgm_volume)
            pygame.mixer.music.play(loops)
            self._current_bgm_key = key
        except pygame.error as e:
            print(f"[AudioManager] Gagal play BGM '{key}': {e}")

    def stop_bgm(self) -> None:
        pygame.mixer.music.stop()
        self._current_bgm_key = ""

    def fade_bgm(self, fade_ms: int = 1000) -> None:
        pygame.mixer.music.fadeout(fade_ms)
        self._current_bgm_key = ""

    def set_bgm_volume(self, volume: float) -> None:
        self._bgm_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self._bgm_volume)

    # SFX

    def play_sfx(self, key: str) -> None:
        sound = self._sfx_cache.get(key)
        if sound:
            sound.play()
            return

        # lazy load
        filepath = self._sfx_registry.get(key)
        if filepath and os.path.exists(filepath):
            try:
                sound = pygame.mixer.Sound(filepath)
                sound.set_volume(self._sfx_volume)
                self._sfx_cache[key] = sound
                sound.play()
            except pygame.error as e:
                print(f"[AudioManager] Gagal load & play SFX '{key}': {e}")

    def set_sfx_volume(self, volume: float) -> None:
        self._sfx_volume = max(0.0, min(1.0, volume))
        for sound in self._sfx_cache.values():
            sound.set_volume(self._sfx_volume)

    # Typewriter

    def play_type_tick(self, delta_time: float) -> None:
        self._type_cooldown -= delta_time
        if self._type_cooldown <= 0:
            self.play_sfx("dialogue_type")
            self._type_cooldown = self._type_cooldown_max

    def reset_type_cooldown(self) -> None:
        self._type_cooldown = 0.0

    # Update

    def update(self, delta_time: float) -> None:
        pass

    # Room BGM

    def play_bgm_for_room(self, room_name: str) -> None:
        key = room_name.lower().replace(" ", "_")
        if key in self._bgm_registry:
            self.play_bgm(key)
        else:
            self.fade_bgm(500)