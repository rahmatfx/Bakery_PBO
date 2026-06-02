import math
import Constant


class _Track:

    def __init__(self, duration: float):
        self.elapsed: float = 0.0
        self.duration: float = duration
        self.done: bool = False

    def update(self, delta_time: float) -> tuple[float, float, float]:
        self.elapsed += delta_time
        if self.elapsed >= self.duration:
            self.elapsed = self.duration
            self.done = True
        return 0.0, 0.0, 1.0

    @property
    def progress(self) -> float:
        if self.duration <= 0:
            return 1.0
        return min(1.0, self.elapsed / self.duration)


class _ShakeTrack(_Track):

    def __init__(self, intensity: int, duration: float):
        super().__init__(duration)
        self.intensity = intensity
        self._frequency = Constant.ANIM_SHAKE_FREQUENCY

    def update(self, delta_time: float) -> tuple[float, float, float]:
        _, _, _ = super().update(delta_time)
        if self.done:
            return 0.0, 0.0, 1.0

        decay = 1.0 - self.progress
        dx = math.sin(self.elapsed * self._frequency) * self.intensity * decay
        return dx, 0.0, 1.0


class _PopInTrack(_Track):

    def __init__(self, duration: float, overshoot: float = 0.2):
        super().__init__(duration)
        self.overshoot = overshoot

    def update(self, delta_time: float) -> tuple[float, float, float]:
        _, _, _ = super().update(delta_time)
        if self.done:
            return 0.0, 0.0, 1.0

        t = self.progress
        if t < 0.6:
            scale = t / 0.6 * (1.0 + self.overshoot)
        else:
            settle_t = (t - 0.6) / 0.4
            scale = (1.0 + self.overshoot) - self.overshoot * settle_t

        return 0.0, 0.0, max(0.0, scale)


class _PopOutTrack(_Track):

    def update(self, delta_time: float) -> tuple[float, float, float]:
        _, _, _ = super().update(delta_time)
        if self.done:
            return 0.0, 0.0, 0.0

        scale = 1.0 - self.progress
        return 0.0, 0.0, max(0.0, scale)


class _BounceTrack(_Track):

    def __init__(self, duration: float, height: int = 0):
        super().__init__(duration)
        self.height = height or Constant.ANIM_BOUNCE_HEIGHT
        self._frequency = Constant.ANIM_BOUNCE_FREQUENCY

    def update(self, delta_time: float) -> tuple[float, float, float]:
        _, _, _ = super().update(delta_time)
        if self.done:
            return 0.0, 0.0, 1.0

        decay = 1.0 - self.progress
        dy = -abs(math.sin(self.elapsed * self._frequency)) * self.height * decay
        return 0.0, dy, 1.0


class _SlideTrack(_Track):

    def __init__(self, start_dx: int, start_dy: int,
                 duration: float, ease: str = "out"):
        super().__init__(duration)
        self.start_dx = start_dx
        self.start_dy = start_dy
        self.ease = ease

    def update(self, delta_time: float) -> tuple[float, float, float]:
        _, _, _ = super().update(delta_time)
        if self.done:
            return 0.0, 0.0, 1.0

        t = self.progress
        if self.ease == "out":
            t_ease = 1.0 - (1.0 - t) ** 3
        else:
            t_ease = t

        dx = self.start_dx * (1.0 - t_ease)
        dy = self.start_dy * (1.0 - t_ease)
        return dx, dy, 1.0


class _FadeTrack(_Track):

    def __init__(self, duration: float, sink: int = 0, min_scale: float = 0.88):
        super().__init__(duration)
        self.sink = sink or Constant.ANIM_FADE_SINK
        self.min_scale = min_scale

    def update(self, delta_time: float) -> tuple[float, float, float]:
        _, _, _ = super().update(delta_time)
        if self.done:
            return 0.0, 0.0, 1.0

        t = self.progress

        if t < 0.3:
            phase = t / 0.3
            dy = self.sink * phase
            scale = 1.0 - (1.0 - self.min_scale) * phase
        else:
            phase = (t - 0.3) / 0.7
            ease = 1.0 - (1.0 - phase) ** 2
            dy = self.sink * (1.0 - ease)
            scale = self.min_scale + (1.0 - self.min_scale) * ease

        return 0.0, dy, max(0.0, scale)


class Animator:

    def __init__(self):
        self._tracks: dict[str, _Track] = {}


    def shake(self, track_id: str, intensity: int = 0,
              duration: float = 0.0) -> None:
        intensity = intensity or Constant.ANIM_SHAKE_INTENSITY
        duration = duration or Constant.ANIM_SHAKE_DURATION
        self._tracks[track_id] = _ShakeTrack(intensity, duration)

    def pop_in(self, track_id: str, duration: float = 0.0,
               overshoot: float = 0.2) -> None:
        duration = duration or Constant.ANIM_POP_DURATION
        self._tracks[track_id] = _PopInTrack(duration, overshoot)

    def pop_out(self, track_id: str, duration: float = 0.0) -> None:
        duration = duration or Constant.ANIM_POP_DURATION
        self._tracks[track_id] = _PopOutTrack(duration)

    def bounce(self, track_id: str, duration: float = 0.0,
               height: int = 0) -> None:
        duration = duration or Constant.ANIM_BOUNCE_DURATION
        self._tracks[track_id] = _BounceTrack(duration, height)

    def slide(self, track_id: str, start_dx: int, start_dy: int = 0,
              duration: float = 0.0, ease: str = "out") -> None:
        duration = duration or Constant.ANIM_SLIDE_DURATION
        self._tracks[track_id] = _SlideTrack(start_dx, start_dy, duration, ease)

    def fade(self, track_id: str, duration: float = 0.0,
             sink: int = 0, min_scale: float = 0.88) -> None:
        duration = duration or Constant.ANIM_FADE_DURATION
        sink = sink or Constant.ANIM_FADE_SINK
        self._tracks[track_id] = _FadeTrack(duration, sink, min_scale)


    def update(self, delta_time: float) -> dict[str, tuple[float, float, float]]:
        result = {}
        finished = []

        for track_id, track in self._tracks.items():
            dx, dy, scale = track.update(delta_time)
            result[track_id] = (dx, dy, scale)
            if track.done:
                finished.append(track_id)

        for track_id in finished:
            del self._tracks[track_id]

        return result


    def is_active(self, track_id: str) -> bool:
        return track_id in self._tracks

    def get_offset(self, track_id: str) -> tuple[float, float, float]:
        track = self._tracks.get(track_id)
        if track is None:
            return 0.0, 0.0, 1.0
        return 0.0, 0.0, 1.0

    def stop(self, track_id: str) -> None:
        self._tracks.pop(track_id, None)

    def stop_all(self) -> None:
        self._tracks.clear()
