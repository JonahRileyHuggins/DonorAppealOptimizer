import tkinter as tk
from tkinter import filedialog


def choose_file(start_folder=""):
    # The hidden window lets the Windows file browser open on its own.
    window = tk.Tk()
    window.withdraw()
    window.attributes("-topmost", True)

    chosen = filedialog.askopenfilename(
        title="Choose the individual donor export",
        initialdir=start_folder,
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
    )

    window.destroy()
    return chosen
