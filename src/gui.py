import tkinter as tk
from tkinter.filedialog import askopenfilename
import main

def openFile():
    global filepath
    filepath = askopenfilename(
        filetypes=[("XML Files", "*.XML"), ("All Files", "*.*")]
    )
    if not filepath:
        print("ERROR: No file selected")
        return
    print(f"File Path:{filepath}")
    cb = main.circutBalancer()
    cb.run(xmlPath=filepath)

if __name__ == "__main__":
    openFile()
    input("Press the Return key to continue...")