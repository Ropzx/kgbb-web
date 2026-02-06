import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import subprocess
import os
import shutil
import threading
import time


def drop_python(event):
    py_file.set(event.data)
    drop_label_py.config(text=f"Python file:\n{event.data}")

def select_icon():
    file = filedialog.askopenfilename(filetypes=[("ICO files", "*.ico")])
    if file:
        icon_file.set(file)
        drop_label_icon.config(text=f"Icon selected:\n{file}")

def update_progress(value):
    progress_var.set(value)
    root.update_idletasks()

def build_action():
    threading.Thread(target=build_thread).start()

def build_thread():
    py_path = py_file.get().strip("{}")
    if not py_path.endswith(".py"):
        messagebox.showerror("Error", "Please drag & drop a valid .py file!")
        return

    py_dir = os.path.dirname(py_path)
    base_name = os.path.splitext(os.path.basename(py_path))[0]

    cmd = ["pyinstaller", "--onefile"]

    if noconsole_var.get():
        cmd.append("--noconsole")
    if admin_var.get():
        cmd.append("--uac-admin")
    if icon_var.get() and icon_file.get():
        cmd.extend(["--icon", icon_file.get()])

    cmd.append(py_path)

    update_progress(10)
    time.sleep(0.3)

    try:
        subprocess.run(cmd, cwd=py_dir, check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Build failed!")
        update_progress(0)
        return

    update_progress(60)
    time.sleep(0.3)


    build_path = os.path.join(py_dir, "build")
    spec_file = os.path.join(py_dir, f"{base_name}.spec")
    dist_path = os.path.join(py_dir, "dist")
    exe_path = os.path.join(dist_path, f"{base_name}.exe")

    if os.path.exists(build_path):
        shutil.rmtree(build_path)
    if os.path.exists(spec_file):
        os.remove(spec_file)

    update_progress(80)
    time.sleep(0.3)

    if os.path.exists(exe_path):
        final_path = os.path.join(py_dir, f"{base_name}.exe")
        shutil.move(exe_path, final_path)
        if os.path.exists(dist_path):
            shutil.rmtree(dist_path)
        update_progress(100)
        messagebox.showinfo("Success", f"EXE built successfully:\n{final_path}")
    else:
        update_progress(0)
        messagebox.showerror("Error", "EXE not found! Build may have failed.")


root = TkinterDnD.Tk()
root.title("Python to EXE Builder")
root.geometry("650x480")
root.configure(bg="#2e2e2e")  

py_file = tk.StringVar()
icon_file = tk.StringVar()


style = ttk.Style()
style.theme_use("clam")


style.configure("TLabel", background="#2e2e2e", foreground="#d6c6e1", font=("Helvetica", 11))

style.configure("TButton", background="#6c547c", foreground="#f0f0f0", font=("Helvetica", 11, "bold"), padding=8)
style.map("TButton",
          background=[('active', '#7d6391')])

style.configure("TProgressbar", troughcolor="#444", background="#9b7bcf")

style.configure("TCheckbutton",
                background="#2e2e2e",
                foreground="#d6c6e1",
                font=("Helvetica", 10))
style.map("TCheckbutton",
          foreground=[('selected', '#d6c6e1')],
          background=[('selected', '#2e2e2e')])


drop_label_py = ttk.Label(root, text="Drag & Drop your Python file here", relief="ridge", padding=15)
drop_label_py.pack(pady=20, padx=30, fill="x")
drop_label_py.drop_target_register(DND_FILES)
drop_label_py.dnd_bind("<<Drop>>", drop_python)

# Checkbuttons
admin_var = tk.BooleanVar()
icon_var = tk.BooleanVar()
noconsole_var = tk.BooleanVar()

ttk.Checkbutton(root, text="Run as Admin", variable=admin_var).pack(anchor="w", padx=30, pady=5)
ttk.Checkbutton(root, text="Select Icon", variable=icon_var, command=lambda: select_icon() if icon_var.get() else None).pack(anchor="w", padx=30, pady=5)
ttk.Checkbutton(root, text="Run without Console", variable=noconsole_var).pack(anchor="w", padx=30, pady=5)

drop_label_icon = ttk.Label(root, text="No icon selected", padding=5)
drop_label_icon.pack(anchor="w", padx=50, pady=5)

ttk.Button(root, text="Build EXE", command=build_action).pack(pady=20)

progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=550, mode="determinate", variable=progress_var)
progress_bar.pack(pady=15)

root.mainloop()
