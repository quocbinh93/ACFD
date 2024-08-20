import tkinter as tk
from tkinter import ttk

use_case_data = None

def save_use_case(use_case_data):
    with open("use_case.txt", "w", encoding="utf-8") as file:
        for key, value in use_case_data.items():
            file.write(f"{key}: {value}\n")

def get_use_case_input():
    global use_case_data
    use_case_data = {
        label: entry_widgets[label].get("1.0", tk.END).strip() if isinstance(entry_widgets[label], tk.Text) 
            else entry_widgets[label].get()
        for label in labels
    }
    save_use_case(use_case_data)
    window.destroy()

def cancel():
    window.destroy() 

window = tk.Tk()
window.title("Use Case Description Tool")

# Styling (with some enhancements)
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", padding=(10, 5), font=("Segoe UI", 10))
style.configure("TEntry", padding=5, font=("Segoe UI", 10))
style.configure("TButton", padding=(15, 10), font=("Segoe UI", 11, "bold"), borderwidth=0, anchor="center") 
style.map("TButton",
          foreground=[("pressed", "black"), ("active", "black")],
          background=[("pressed", "!disabled", "#e0e0e0"), ("active", "#f0f0f0")])
window.configure(bg="#f0f0f0")

# Layout with Frames
main_frame = ttk.Frame(window, padding=20)
main_frame.pack(fill=tk.BOTH, expand=True)

labels = ["Name", "Goal", "Actors", "Preconditions", "Postconditions", "Invariants",
          "Main Success Scenario", "Variations", "Extensions", "Included Use Cases"]
entry_widgets = {}

for label in labels:
    ttk.Label(main_frame, text=label).pack(fill=tk.X, pady=(0, 5))

    if label in ["Main Success Scenario", "Variations", "Extensions"]:
        entry_widget = tk.Text(main_frame, height=5, wrap=tk.WORD)
    else:
        entry_widget = ttk.Entry(main_frame)
        
    entry_widget.pack(fill=tk.X, pady=(0, 10), expand=True)  # Allow multi-line entries to expand vertically 
    entry_widgets[label] = entry_widget

# Button Frame for better organization
button_frame = ttk.Frame(main_frame)
button_frame.pack(pady=(10, 0))

save_button = ttk.Button(button_frame, text="Create", command=get_use_case_input)
save_button.pack(side=tk.LEFT, padx=(0, 10))  # Add padding between buttons

cancel_button = ttk.Button(button_frame, text="Cancel", command=cancel)
cancel_button.pack(side=tk.LEFT)

window.mainloop()
