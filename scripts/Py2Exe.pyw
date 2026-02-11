import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
import subprocess
import os
import shutil
import threading
import time
import sys


def normalize_drop_path(data: str) -> str:
    data = (data or "").strip()
    if not data:
        return ""
    parts = data.split()
    first = parts[0].strip()
    return first.strip("{}")


def drop_python(event):
    path = normalize_drop_path(event.data)
    py_file.set(path)
    drop_label_py.config(text=f"Python file:\n{path}")


def select_icon():
    file = filedialog.askopenfilename(filetypes=[("ICO files", "*.ico")])
    if file:
        icon_file.set(file)
        drop_label_icon.config(text=f"Icon selected:\n{file}")


def update_progress(value):
    progress_var.set(value)
    root.update_idletasks()


def run_pip_install(packages):
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade"] + packages
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def ensure_tools_installed():
    update_progress(5)
    try:
        run_pip_install(["pyinstaller", "tkinterdnd2"])
    except Exception:
        pass


def add_data_entry(src_path: str):
    src_path = src_path.strip()
    if not src_path:
        return
    dest = data_dest.get().strip() or "assets"
    add_data_listbox.insert("end", f"{src_path}  ->  {dest}")


def pick_data_files():
    paths = filedialog.askopenfilenames(title="Select data files to bundle")
    if paths:
        for p in paths:
            add_data_entry(p)


def pick_data_folder():
    p = filedialog.askdirectory(title="Select a folder to bundle")
    if p:
        add_data_entry(p)


def remove_selected_data():
    sel = list(add_data_listbox.curselection())
    sel.reverse()
    for i in sel:
        add_data_listbox.delete(i)


def get_add_data_args():
    args = []
    dest = data_dest.get().strip() or "assets"
    for i in range(add_data_listbox.size()):
        line = add_data_listbox.get(i)
        if "->" in line:
            src = line.split("->", 1)[0].strip()
        else:
            src = line.strip()
        if src:
            args.extend(["--add-data", f"{src};{dest}"])
    return args


def set_data_controls_enabled(enabled: bool):
    state = "normal" if enabled else "disabled"
    dest_entry.configure(state=state)
    btn_add_files.configure(state=state)
    btn_add_folder.configure(state=state)
    btn_remove.configure(state=state)
    add_data_listbox.configure(state=state)


def on_toggle_add_data():
    set_data_controls_enabled(add_data_var.get())


def build_action():
    threading.Thread(target=build_thread, daemon=True).start()


def build_thread():
    update_progress(1)
    ensure_tools_installed()
    update_progress(10)

    py_path = py_file.get().strip()
    if not py_path:
        messagebox.showerror("Error", "Please drag & drop a .py or .pyw file!")
        update_progress(0)
        return

    if not (py_path.lower().endswith(".py") or py_path.lower().endswith(".pyw")):
        messagebox.showerror("Error", "Please drag & drop a valid .py or .pyw file!")
        update_progress(0)
        return

    if not os.path.exists(py_path):
        messagebox.showerror("Error", f"File not found:\n{py_path}")
        update_progress(0)
        return

    py_dir = os.path.dirname(py_path)
    base_name = os.path.splitext(os.path.basename(py_path))[0]

    cmd = [sys.executable, "-m", "PyInstaller", "--onefile"]

    if noconsole_var.get():
        cmd.append("--noconsole")
    if admin_var.get():
        cmd.append("--uac-admin")
    if icon_var.get() and icon_file.get():
        cmd.extend(["--icon", icon_file.get()])

    if add_data_var.get():
        cmd.extend(get_add_data_args())

    cmd.append(py_path)

    update_progress(15)
    time.sleep(0.15)

    try:
        subprocess.run(cmd, cwd=py_dir, check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Build failed!\n\nTip: try without 'Run without Console' to see errors.")
        update_progress(0)
        return
    except Exception as e:
        messagebox.showerror("Error", f"Build failed:\n{e}")
        update_progress(0)
        return

    update_progress(60)
    time.sleep(0.15)

    build_path = os.path.join(py_dir, "build")
    spec_file = os.path.join(py_dir, f"{base_name}.spec")
    dist_path = os.path.join(py_dir, "dist")
    exe_path = os.path.join(dist_path, f"{base_name}.exe")

    try:
        if os.path.exists(build_path):
            shutil.rmtree(build_path)
        if os.path.exists(spec_file):
            os.remove(spec_file)
    except Exception:
        pass

    update_progress(80)
    time.sleep(0.15)

    if os.path.exists(exe_path):
        final_path = os.path.join(py_dir, f"{base_name}.exe")
        try:
            if os.path.exists(final_path):
                os.remove(final_path)
            shutil.move(exe_path, final_path)
            if os.path.exists(dist_path):
                shutil.rmtree(dist_path)
        except Exception as e:
            messagebox.showerror("Error", f"EXE created but moving failed:\n{e}")
            update_progress(0)
            return

        update_progress(100)
        messagebox.showinfo("Success", f"EXE built successfully:\n{final_path}")
    else:
        update_progress(0)
        messagebox.showerror("Error", "EXE not found! Build may have failed.")



root = TkinterDnD.Tk()
root.title("Python to EXE Builder")
root.geometry("760x620")
root.configure(bg="#2e2e2e")

py_file = tk.StringVar()
icon_file = tk.StringVar()
data_dest = tk.StringVar(value="assets")

style = ttk.Style()
style.theme_use("clam")

style.configure("TLabel", background="#2e2e2e", foreground="#d6c6e1", font=("Helvetica", 11))
style.configure("TButton", background="#6c547c", foreground="#f0f0f0", font=("Helvetica", 11, "bold"), padding=8)
style.map("TButton", background=[('active', '#7d6391')])
style.configure("TProgressbar", troughcolor="#444", background="#9b7bcf")
style.configure("TCheckbutton", background="#2e2e2e", foreground="#d6c6e1", font=("Helvetica", 10))
style.map("TCheckbutton",
          foreground=[('selected', '#d6c6e1')],
          background=[('selected', '#2e2e2e')])


main = ttk.Frame(root)
main.pack(fill="both", expand=True, padx=14, pady=12)


drop_label_py = ttk.Label(main, text="Drag & Drop your Python file here (.py or .pyw)", relief="ridge", padding=15)
drop_label_py.pack(fill="x", pady=(0, 10))
drop_label_py.drop_target_register(DND_FILES)
drop_label_py.dnd_bind("<<Drop>>", drop_python)


admin_var = tk.BooleanVar()
icon_var = tk.BooleanVar()
noconsole_var = tk.BooleanVar()
add_data_var = tk.BooleanVar()

opts = ttk.Frame(main)
opts.pack(fill="x", pady=(0, 6))
opts.columnconfigure(0, weight=1)
opts.columnconfigure(1, weight=1)
opts.columnconfigure(2, weight=1)
opts.columnconfigure(3, weight=1)

ttk.Checkbutton(opts, text="Run as Admin", variable=admin_var).grid(row=0, column=0, sticky="w", padx=(2, 8))
ttk.Checkbutton(
    opts, text="Select Icon", variable=icon_var,
    command=lambda: select_icon() if icon_var.get() else None
).grid(row=0, column=1, sticky="w", padx=(2, 8))
ttk.Checkbutton(opts, text="Run without Console", variable=noconsole_var).grid(row=0, column=2, sticky="w", padx=(2, 8))
ttk.Checkbutton(opts, text="Include Data (images/files)", variable=add_data_var, command=on_toggle_add_data)\
    .grid(row=0, column=3, sticky="w", padx=(2, 0))

drop_label_icon = ttk.Label(main, text="No icon selected", padding=5)
drop_label_icon.pack(anchor="w", pady=(0, 8))


data_frame = ttk.LabelFrame(main, text="Add Data (bundled into EXE)")
data_frame.pack(fill="x", pady=(0, 10))
data_frame.columnconfigure(1, weight=1)

ttk.Label(data_frame, text="Destination folder inside bundle:").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 6))
dest_entry = ttk.Entry(data_frame, textvariable=data_dest, width=18)
dest_entry.grid(row=0, column=1, sticky="w", padx=(0, 8), pady=(10, 6))
ttk.Label(data_frame, text="(example: assets)").grid(row=0, column=2, sticky="w", padx=(0, 10), pady=(10, 6))

btn_row = ttk.Frame(data_frame)
btn_row.grid(row=1, column=0, columnspan=3, sticky="w", padx=10, pady=(2, 6))

btn_add_files = ttk.Button(btn_row, text="Add File(s)", command=pick_data_files)
btn_add_files.pack(side="left", padx=(0, 8))
btn_add_folder = ttk.Button(btn_row, text="Add Folder", command=pick_data_folder)
btn_add_folder.pack(side="left", padx=(0, 8))
btn_remove = ttk.Button(btn_row, text="Remove Selected", command=remove_selected_data)
btn_remove.pack(side="left")

add_data_listbox = tk.Listbox(data_frame, height=5)
add_data_listbox.grid(row=2, column=0, columnspan=3, sticky="ew", padx=10, pady=(0, 10))


ttk.Button(main, text="Build EXE (auto-installs PyInstaller)", command=build_action).pack(pady=(4, 8))


progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(main, orient="horizontal", mode="determinate", variable=progress_var)
progress_bar.pack(fill="x", pady=(0, 10))


ins_frame = ttk.LabelFrame(main, text="Instructions")
ins_frame.pack(fill="both", expand=True)

instructions = """HOW TO USE

1) Drag & drop a .py or .pyw file.
2) Optional: Run without Console (best for GUI apps).
3) Optional: Select Icon (.ico).
4) Optional: Include Data:
   - Add File(s) or Add Folder
   - Destination folder defaults to: assets

IN YOUR APP CODE (to read bundled files)

import sys, os
def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel)

# If destination is assets:
path = resource_path("assets/your_image.png")
"""

txt = tk.Text(ins_frame, wrap="word", bg="#1f1f1f", fg="#d6c6e1", insertbackground="#d6c6e1")
txt.pack(fill="both", expand=True, padx=10, pady=10)
txt.insert("1.0", instructions)
txt.config(state="disabled")


set_data_controls_enabled(False)

root.mainloop()
