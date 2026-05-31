#!/usr/bin/env python3
"""Real-time fly motor visualizer — 2D top-down view over UDP.

The visualizer doubles as a *Virtual Arena*: clicking or dragging the mouse
places a food / light stimulus that is sent back to the engine over a
reverse UDP channel.  The fly's connectome steers toward the stimulus in
real time.

Usage
-----
    # Terminal 1: start the engine with viz enabled
    conda run -n flybrain python -c "
    from lib.gpu_simulation import GPUClimateSimulation
    from lib.realtime_engine import RealtimeEngine
    import numpy as np
    d = np.load('data/projectome_v783.npz', allow_pickle=True)
    sim = GPUClimateSimulation(d['matrix'], list(d['neuropil_names']), device='cuda')
    engine = RealtimeEngine(sim, list(d['neuropil_names']), device='cuda', enable_viz=True)
    engine.start()
    "

    # Terminal 2: launch this visualizer
    conda run -n flybrain python fly_view.py
"""

import json
import math
import socket
import time

import pygame

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WIDTH, HEIGHT = 1400, 900
SCALE = 800                    # pixels per world unit
BG_COLOR = (16, 16, 24)
GRID_COLOR = (32, 32, 48)
FLY_BODY_COLOR = (180, 170, 140)
FLY_HEAD_COLOR = (200, 190, 160)
FLY_ABDOMEN_COLOR = (140, 130, 110)
LEG_SWING_COLOR = (60, 140, 200)
LEG_STANCE_COLOR = (160, 150, 130)
WING_COLOR = (120, 170, 220)
HEADING_COLOR = (240, 80, 80)
PATH_COLOR = (60, 90, 140)
HUD_COLOR = (200, 200, 200)
HUD_HI_COLOR = (255, 200, 100)
FEEDING_COLOR = (200, 180, 100)
CLEANING_COLOR = (100, 180, 255)

STIMULUS_GLOW = (255, 220, 100)
STIMULUS_LINE = (255, 200, 80, 60)
INVESTOR_BG = (10, 10, 18, 200)

UDP_RECV_PORT = 5555          # engine → visualizer
UDP_SEND_PORT = 5556          # visualizer → engine (stimulus)
UDP_HOST = "127.0.0.1"
MAX_PATH = 800

# ---------------------------------------------------------------------------
# Leg kinematics (body-local 2D)
# ---------------------------------------------------------------------------

LEG_ATTACH = {
    "L1": (0.14,  0.09), "R1": (0.14, -0.09),
    "L2": (0.00,  0.10), "R2": (0.00, -0.10),
    "L3": (-0.14, 0.09), "R3": (-0.14, -0.09),
}
TRIPOD_A = {"L1", "R2", "L3"}


def leg_endpoints_2d(
    name: str, gait_cycle: float, speed: float, turn: float,
) -> list[tuple[float, float]]:
    ax, ay = LEG_ATTACH[name]
    y_sign = 1 if name.startswith("L") else -1
    is_a = name in TRIPOD_A
    phase = (gait_cycle + (0.0 if is_a else 0.5)) % 1.0
    in_swing = phase >= 0.5
    swing_progress = (phase - 0.5) / 0.5 if in_swing else 0.0
    turn_bias = turn * y_sign * 0.3

    hip = (ax, ay)
    swing = speed * (1.0 if not in_swing else -0.6) + turn_bias
    femur_angle = -0.3 + 0.5 * swing
    femur_len, tibia_len = 0.09, 0.07
    knee = (hip[0] + femur_len * math.sin(femur_angle),
            hip[1] + y_sign * femur_len * 0.12)

    lift = 0.04 * math.sin(math.pi * swing_progress) if in_swing else 0.0
    tibia_angle = 0.5 + 0.6 * speed * (1.0 if in_swing else -0.3)
    foot = (knee[0] - tibia_len * 0.3 * math.sin(tibia_angle),
            knee[1] - lift)
    return [hip, knee, foot]


def _is_swing(name: str, gait_cycle: float) -> bool:
    is_a = name in TRIPOD_A
    return (gait_cycle + (0.0 if is_a else 0.5)) % 1.0 >= 0.5


# ---------------------------------------------------------------------------
# Viewer
# ---------------------------------------------------------------------------

class FlyViewer:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Fly Brain — Virtual Arena")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("monospace", 11)
        self.font_big = pygame.font.SysFont("monospace", 14)
        self.font_investor = pygame.font.SysFont("monospace", 13)

        # Incoming engine state (asynchronous UDP)
        self.motor: dict = {}
        self.path: list[tuple[float, float]] = []
        self.running = True

        # Stimulus state (mouse-driven)
        self.stimulus_world: tuple[float, float] | None = None
        self.stimulus_active = False
        self._stim_pulse = 0.0

        # UDP receiver (engine → visualizer)
        self.recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.recv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 2 ** 20)
        self.recv_sock.bind((UDP_HOST, UDP_RECV_PORT))
        self.recv_sock.setblocking(False)

        # UDP sender (visualizer → engine, stimulus coordinates)
        self.send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.send_sock.setblocking(False)
        self._send_addr = (UDP_HOST, UDP_SEND_PORT)

    # ------------------------------------------------------------------
    # I/O
    # ------------------------------------------------------------------

    def _poll_udp(self) -> None:
        try:
            data, _ = self.recv_sock.recvfrom(65536)
            parsed = json.loads(data.decode("utf-8"))
            if "pos" in parsed:
                px, py = parsed["pos"]
                self.path.append((px, py))
                if len(self.path) > MAX_PATH:
                    self.path.pop(0)
            self.motor = parsed
        except (BlockingIOError, json.JSONDecodeError, KeyError):
            pass

    def _send_stimulus(self) -> None:
        """Send the current stimulus world position to the engine."""
        if self.stimulus_world is None:
            return
        msg = json.dumps({
            "tx": self.stimulus_world[0],
            "ty": self.stimulus_world[1],
            "active": 1 if self.stimulus_active else 0,
        }).encode("utf-8")
        try:
            self.send_sock.sendto(msg, self._send_addr)
        except OSError:
            pass

    # ------------------------------------------------------------------
    # Coordinate transforms
    # ------------------------------------------------------------------

    def _w2s(self, wx: float, wy: float) -> tuple[int, int]:
        cx, cy = self.motor.get("pos", [0.0, 0.0])
        sx = WIDTH // 2 + int((wx - cx) * SCALE)
        sy = HEIGHT // 2 - int((wy - cy) * SCALE)
        return sx, sy

    def _s2w(self, sx: int, sy: int) -> tuple[float, float]:
        cx, cy = self.motor.get("pos", [0.0, 0.0])
        wx = (sx - WIDTH // 2) / SCALE + cx
        wy = -(sy - HEIGHT // 2) / SCALE + cy
        return wx, wy

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------

    def _draw_grid(self) -> None:
        pitch = 50
        for i in range(-30, 31):
            x = WIDTH // 2 + i * pitch
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, HEIGHT), 1)
            y = HEIGHT // 2 + i * pitch
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (WIDTH, y), 1)

    def _draw_path(self) -> None:
        if len(self.path) < 2:
            return
        pts = [self._w2s(x, y) for x, y in self.path]
        pygame.draw.lines(self.screen, PATH_COLOR, False, pts, 2)
        pygame.draw.circle(self.screen, HEADING_COLOR, pts[-1], 3)

    def _draw_stimulus(self) -> None:
        if self.stimulus_world is None or not self.stimulus_active:
            return
        tx, ty = self.stimulus_world
        sx, sy = self._w2s(tx, ty)

        # Pulsing glow ring
        self._stim_pulse = (self._stim_pulse + 0.04) % (2 * math.pi)
        pulse_r = 12 + int(6 * math.sin(self._stim_pulse))
        for r in range(pulse_r, pulse_r + 12, 4):
            alpha = max(0, 120 - (r - pulse_r) * 10)
            pygame.draw.circle(self.screen, STIMULUS_GLOW + (alpha,),
                               (sx, sy), r, 2)

        # Central dot
        pygame.draw.circle(self.screen, STIMULUS_GLOW, (sx, sy), 5)
        pygame.draw.circle(self.screen, (255, 255, 200), (sx, sy), 2)

        # "Food / Light Source" label
        label = self.font_big.render("Food / Light Source", True, STIMULUS_GLOW)
        self.screen.blit(label, (sx + 18, sy - 8))

        # Line from fly to stimulus
        pos = self.motor.get("pos", [0.0, 0.0])
        fx_s, fy_s = self._w2s(pos[0], pos[1])
        if math.hypot(sx - fx_s, sy - fy_s) > 20:
            pygame.draw.line(self.screen, STIMULUS_LINE[:3],
                             (fx_s, fy_s), (sx, sy), 1)

    def _draw_fly(self) -> None:
        md = self.motor
        pos = md.get("pos", [0.0, 0.0])
        heading = md.get("heading", 0.0)
        gait = md.get("gait_cycle", 0.0)
        speed = md.get("walking_speed", 0.0)
        turn = md.get("turning_rate", 0.0)
        wing_amp = md.get("wing_amplitude", 0.0)
        proboscis = md.get("proboscis_extension", 0.0)
        cleaning = md.get("face_cleaning_drive", 0.0)

        cx, cy = self._w2s(pos[0], pos[1])
        cos_h, sin_h = math.cos(heading), math.sin(heading)

        def b2s(lx: float, ly: float) -> tuple[int, int]:
            wx = lx * cos_h - ly * sin_h + pos[0]
            wy = lx * sin_h + ly * cos_h + pos[1]
            return self._w2s(wx, wy)

        # Legs
        for name in LEG_ATTACH:
            pts = leg_endpoints_2d(name, gait, speed, turn)
            col = LEG_SWING_COLOR if _is_swing(name, gait) else LEG_STANCE_COLOR
            for i in range(len(pts) - 1):
                p1 = b2s(pts[i][0], pts[i][1])
                p2 = b2s(pts[i + 1][0], pts[i + 1][1])
                pygame.draw.line(self.screen, col, p1, p2, 3)
            foot = b2s(pts[-1][0], pts[-1][1])
            pygame.draw.circle(self.screen, col, foot, 3)

        # Body (thorax)
        bw, bh = 0.045, 0.025
        surf = pygame.Surface((int(2 * bw * SCALE), int(2 * bh * SCALE)),
                              pygame.SRCALPHA)
        pygame.draw.ellipse(surf, FLY_BODY_COLOR + (220,), surf.get_rect())
        self.screen.blit(pygame.transform.rotate(surf, -heading * 180 / math.pi),
                         surf.get_rect(center=(cx, cy)))

        # Head
        hx, hy = b2s(0.07, 0.0)
        pygame.draw.circle(self.screen, FLY_HEAD_COLOR, (hx, hy),
                           int(0.018 * SCALE))

        # Proboscis
        if proboscis > 0.05:
            pe = b2s(0.07 + 0.03 * proboscis, 0.0)
            pygame.draw.line(self.screen, FEEDING_COLOR, (hx, hy), pe, 3)

        # Abdomen
        abx, aby = b2s(-0.06, 0.0)
        bend = md.get("abdomen_bend", 0.0)
        abw, abh = int(0.03 * SCALE), int(0.02 * SCALE)
        pygame.draw.ellipse(self.screen, FLY_ABDOMEN_COLOR,
                            (abx - abw // 2, int(aby + bend * 15 * SCALE) - abh // 2,
                             abw, abh))

        # Wings
        if wing_amp > 0.01:
            for y_dir in (1, -1):
                ax, ay = b2s(0.01, y_dir * 0.05)
                ang = heading + y_dir * (0.4 + 0.5 * wing_amp) * math.pi / 4
                wl = int(0.06 * SCALE * (0.5 + 0.5 * wing_amp))
                wx = ax + int(wl * math.cos(ang))
                wy = ay - int(wl * math.sin(ang))
                pygame.draw.line(self.screen, WING_COLOR, (ax, ay), (wx, wy), 3)

        # Heading arrow
        al = int(0.06 * SCALE)
        pygame.draw.line(self.screen, HEADING_COLOR,
                         (cx, cy),
                         (cx + int(al * math.cos(heading)),
                          cy - int(al * math.sin(heading))), 2)

        # Cleaning highlight
        if cleaning > 0.3:
            pygame.draw.circle(self.screen, CLEANING_COLOR,
                               (cx, cy), int(0.08 * SCALE), 1)

    def _draw_motor_hud(self) -> None:
        md = self.motor
        y, lh = 15, 17
        bars = [
            ("walking_speed", HEADING_COLOR),
            ("turning_rate", (100, 200, 255)),
            ("gait_energy", (200, 200, 100)),
            ("wing_amplitude", (150, 200, 240)),
            ("head_pitch", (180, 180, 180)),
            ("head_yaw", (180, 180, 180)),
            ("proboscis_extension", FEEDING_COLOR),
            ("face_cleaning_drive", CLEANING_COLOR),
            ("abdomen_bend", (200, 180, 160)),
            ("body_height", (160, 200, 160)),
        ]
        for key, color in bars:
            val = md.get(key, 0.0)
            self.screen.blit(self.font.render(f"{key:25s}", True, HUD_COLOR),
                             (15, y))
            bx, by = 230, y + 3
            bw, bh = 120, 11
            pygame.draw.rect(self.screen, (40, 40, 50), (bx, by, bw, bh))
            fw = max(2, int(bw * abs(val)))
            fc = color if val >= 0 else (color[0] // 2, color[1] // 2, color[2] // 2)
            pygame.draw.rect(self.screen, fc, (bx, by, fw, bh))
            vs = self.font.render(f"{val:+.3f}", True, HUD_HI_COLOR)
            self.screen.blit(vs, (bx + bw + 8, y))
            y += lh

        # Behavior state
        state = md.get("pose", "")
        if state:
            c = {"FEEDING": FEEDING_COLOR, "FACE_CLEANING": CLEANING_COLOR,
                 "WALKING": HEADING_COLOR}.get(state, HUD_HI_COLOR)
            self.screen.blit(self.font_big.render(f"State: {state}", True, c),
                             (WIDTH - 220, 15))

        # Tick + FPS
        self.screen.blit(
            self.font.render(f"tick {md.get('t', 0)}  |  "
                             f"viz {self.clock.get_fps():.0f} FPS", True, HUD_COLOR),
            (15, HEIGHT - 30))

    # ------------------------------------------------------------------
    # Investor HUD  (target vs fly, firing rate, latency)
    # ------------------------------------------------------------------

    def _draw_investor_hud(self) -> None:
        md = self.motor
        pos = md.get("pos", [0.0, 0.0])
        firing = md.get("firing_rate", 0.0)
        latency = md.get("latency_ms", 0.0)
        stim_active = md.get("stimulus_active", 0)

        # Panel background (bottom-right corner)
        panel_x, panel_y = WIDTH - 420, HEIGHT - 160
        panel_w, panel_h = 405, 145
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill(INVESTOR_BG)
        self.screen.blit(panel, (panel_x, panel_y))
        pygame.draw.rect(self.screen, (60, 60, 80), (panel_x, panel_y, panel_w, panel_h), 1)

        x, y = panel_x + 12, panel_y + 12
        lh2 = 18

        # Title
        title = self.font_big.render("INVESTOR METRICS", True, (255, 255, 200))
        self.screen.blit(title, (x, y))
        y += lh2 + 4

        # Target coordinates
        if stim_active:
            tx = md.get("tx", 0.0)
            ty = md.get("ty", 0.0)
            tgt_str = f"Target:     ({tx:+06.3f}, {ty:+06.3f})"
            fly_str = f"Fly:        ({pos[0]:+06.3f}, {pos[1]:+06.3f})"
            dx = tx - pos[0]
            dy = ty - pos[1]
            dist = math.hypot(dx, dy)
            delta_str = f"\N{GREEK CAPITAL LETTER DELTA}    ({dx:+06.3f}, {dy:+06.3f})  d={dist:.3f}"
            self.screen.blit(self.font_investor.render(tgt_str, True, STIMULUS_GLOW),
                             (x, y))
            y += lh2
            self.screen.blit(self.font_investor.render(fly_str, True, HUD_COLOR),
                             (x, y))
            y += lh2
            self.screen.blit(self.font_investor.render(delta_str, True, HUD_HI_COLOR),
                             (x, y))
        else:
            self.screen.blit(self.font_investor.render(
                "No stimulus  (click to place)", True, (100, 100, 120)), (x, y))
            y += lh2 * 2

        y += 4

        # Firing rate + latency
        fr_str = f"Mean Firing Rate:   {firing:.4f}  Hz"
        lat_str = f"Matrix Latency:     {latency:.3f}  ms"
        self.screen.blit(self.font_investor.render(fr_str, True,
                         (100, 220, 100) if firing > 0.1 else (200, 100, 100)),
                         (x, y))
        y += lh2
        lat_color = (100, 220, 100) if latency < 16.0 else (255, 150, 50)
        self.screen.blit(self.font_investor.render(lat_str, True, lat_color),
                         (x, y))

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_c:
                        # Clear stimulus
                        self.stimulus_active = False
                        self.stimulus_world = None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # left click
                        self.stimulus_world = self._s2w(*event.pos)
                        self.stimulus_active = True
                elif event.type == pygame.MOUSEMOTION:
                    if self.stimulus_active and event.buttons[0]:
                        self.stimulus_world = self._s2w(*event.pos)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        # Keep the stimulus at the final position
                        pass

            self._poll_udp()
            if self.stimulus_active and self.stimulus_world is not None:
                self._send_stimulus()

            self.screen.fill(BG_COLOR)
            self._draw_grid()
            self._draw_path()
            self._draw_stimulus()
            self._draw_fly()
            self._draw_motor_hud()
            self._draw_investor_hud()
            pygame.display.flip()
            self.clock.tick(60)

        # Cleanup: send deactivation on exit
        if self.stimulus_world is not None:
            try:
                self.send_sock.sendto(
                    json.dumps({"tx": 0, "ty": 0, "active": 0}).encode("utf-8"),
                    self._send_addr,
                )
            except OSError:
                pass
        pygame.quit()
        self.recv_sock.close()
        self.send_sock.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"[FlyView] Listening on {UDP_HOST}:{UDP_RECV_PORT}, "
          f"sending stimulus on {UDP_HOST}:{UDP_SEND_PORT}")
    FlyViewer().run()
    print("[FlyView] Exited.")
