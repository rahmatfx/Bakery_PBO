from enum import IntEnum
import pygame
import Constant
from Room.Room import Room
from Observer import Observer
from UI.NavUI import NavigationUI


class TransitionState(IntEnum):
    IDLE     = 0
    FADE_OUT = 1
    FADE_IN  = 2


class SceneManager(Observer):

    def __init__(self, screen: pygame.Surface, audio=None):
        self.screen = screen
        self.audio  = audio
        self.current_room: Room = None
        
        self.active_orders = None
        self.active_cakes = None

        self._rooms: dict[str, Room]        = {}
        self._hidden_rooms: dict[str, Room] = {}

        self.navigation_ui = NavigationUI(audio)
        self.navigation_ui.add_observer(self)
        self._nav_visible = False

        self._state       = TransitionState.IDLE
        self._fade_alpha  = 0
        self._next_room: Room = None
        self._pending_room: Room = None

        self._fade_surface = pygame.Surface(
            (Constant.SCREEN_WIDTH, Constant.SCREEN_HEIGHT)
        )
        self._fade_surface.fill((0, 0, 0))

        self._timer_active    = False
        self._timer_remaining = 0.0
        self._timer_expired   = False

    # Register

    def register_room(self, room: Room) -> None:
        self._rooms[room.name] = room

    def register_hidden_room(self, room: Room) -> None:
        self._hidden_rooms[room.name] = room
        print(f"[SceneManager] Hidden room registered: '{room.name}'")

    # Query

    def _get_room_by_name(self, name: str) -> Room | None:
        return self._rooms.get(name) or self._hidden_rooms.get(name)

    def get_room_names(self) -> list[str]:
        return list(self._rooms.keys())

    # Observer

    def on_notify(self, event_type: str, data=None) -> None:
        if event_type == "room_change":
            room_name: str = data
            print(f"[DEBUG SM] Received 'room_change', target: {room_name}")
            if self.current_room and self.current_room.name == room_name:
                print(f"[DEBUG SM] Same room ({room_name}), no change")
                return
            self.transition_to(room_name)

    # Transition 

    def transition_to(self, room) -> None:
        if isinstance(room, str):
            target = self._get_room_by_name(room)
            if target is None:
                print(f"[DEBUG SM] Room not found: '{room}' "
                      f"(visible: {list(self._rooms.keys())}, "
                      f"hidden: {list(self._hidden_rooms.keys())})")
                return
            room = target

        if self.current_room and self.current_room is room:
            return

        if room is None:
            print("[DEBUG SM] Cannot transition to None room!")
            return

        if self._state != TransitionState.IDLE:
            print(f"[DEBUG SM] Transition in progress, queuing '{room.name}'")
            self._pending_room = room
            return

        self._next_room  = room
        self._state      = TransitionState.FADE_OUT
        self._fade_alpha = 0

    def go_to_main_menu(self) -> None:
        self.hide_navigation_ui()
        self.stop_timer()
        self.transition_to("Main Menu")

    def _apply_room_change(self) -> None:
        if self.current_room:
            self.current_room.exit()
        self.current_room = self._next_room
        if hasattr(self.current_room, "current_order"):
            self.current_room.current_order = self.active_orders
        if hasattr(self.current_room, "cake"):
            self.current_room.cake = self.active_cakes
        self.current_room.enter()

        self.navigation_ui.set_room(self.current_room.name)

        if self.current_room.name in self._rooms:
            self._nav_visible = True
        else:
            self._nav_visible = False

        if self.audio:
            self.audio.play_bgm_for_room(self.current_room.name)

        print(f"[DEBUG SM] Current room: '{self.current_room.name}'")
        self._next_room = None

    # Nav UI 

    def show_navigation_ui(self) -> None:
        self._nav_visible = True

    def hide_navigation_ui(self) -> None:
        self._nav_visible = False

    # Timer 

    def start_timer(self, seconds: float) -> None:
        self._timer_active    = True
        self._timer_remaining = seconds
        self._timer_expired   = False
        print(f"[DEBUG SM] Timer started: {seconds}s")

    def stop_timer(self) -> None:
        self._timer_active = False
        self.navigation_ui.set_timer_text("")
        print("[DEBUG SM] Timer stopped")

    def add_time(self, seconds: float) -> None:
        if self._timer_active:
            self._timer_remaining += seconds
            print(f"[DEBUG SM] +{seconds}s added, remaining: {self._timer_remaining:.1f}s")

    def get_timer_remaining(self) -> float:
        return max(0.0, self._timer_remaining)

    def consume_timer_expired(self) -> bool:
        if self._timer_expired:
            self._timer_expired = False
            return True
        return False

    def _on_timer_expired(self) -> None:
        print("[DEBUG SM] Timer expired!")
        if self.current_room and self.current_room.name == "Cashier":
            if hasattr(self.current_room, "on_timer_expired"):
                self.current_room.on_timer_expired()
        else:
            self._timer_expired = True
            self.transition_to("Cashier")

    # Special triggers 

    def start_ending(self, npc_data) -> None:
        print(f"[DEBUG SM] start_ending called for '{npc_data.name}'")
        ending_room = self._hidden_rooms.get("Ending")
        if ending_room:
            ending_room.setup(npc_data, self.audio)
            self.hide_navigation_ui()
            self.stop_timer()
            self.transition_to(ending_room)
        else:
            print("[DEBUG SM] Ending room not registered!")

    # Update 

    def update(self, delta_time: float = 0.0) -> None:
        if self._state == TransitionState.FADE_OUT:
            self._fade_alpha += Constant.TRANSITION_SPEED
            if self._fade_alpha >= 255:
                self._fade_alpha = 255
                self._apply_room_change()
                self._state = TransitionState.FADE_IN

        elif self._state == TransitionState.FADE_IN:
            self._fade_alpha -= Constant.TRANSITION_SPEED
            if self._fade_alpha <= 0:
                self._fade_alpha = 0
                self._state      = TransitionState.IDLE
                print("[DEBUG SM] Transition complete")

                if self._pending_room:
                    pending            = self._pending_room
                    self._pending_room = None
                    print(f"[DEBUG SM] Executing pending transition to '{pending.name}'")
                    self.transition_to(pending)

        if self._timer_active:
            self._timer_remaining -= delta_time
            if self._timer_remaining <= 0:
                self._timer_remaining = 0
                self._timer_active    = False
                self._on_timer_expired()

        if self._timer_active:
            secs = max(0, int(self._timer_remaining))
            self.navigation_ui.set_timer_text(f"Time: {secs}s")
        else:
            self.navigation_ui.set_timer_text("")

        if self._nav_visible:
            self.navigation_ui.update()

        if self.current_room:
            try:
                self.current_room.update(delta_time)
            except TypeError:
                self.current_room.update()

    # Render 

    def render(self) -> None:
        if self.current_room:
            self.current_room.render()

        if self._nav_visible and self.current_room:
            self.navigation_ui.render(self.screen)

        if self.current_room and hasattr(self.current_room, '_render_above_nav'):
            self.current_room._render_above_nav(self.screen)

        if self._fade_alpha > 0:
            self._fade_surface.set_alpha(int(self._fade_alpha))
            self.screen.blit(self._fade_surface, (0, 0))

    # Events

    def handle_event(self, event) -> None:
        if self._nav_visible:
            self.navigation_ui.handle_event(event)

        if self.current_room and self._state == TransitionState.IDLE:
            self.current_room.handle_event(event)