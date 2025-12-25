import tkinter as tk
from tkinter import ttk, messagebox
import random

class CacheSimulatorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cache Memory Mapping Simulator - Group 3 microproject")
        self.geometry("1020x700")
        self.configure(bg="#154360")  # dark blue border

        # Variables: Declare FIRST
        self.mapping_var = tk.StringVar(value="direct")
        self.memory_size_var = tk.StringVar(value="64")
        self.cache_size_var = tk.StringVar(value="8")
        self.set_size_var = tk.StringVar(value="2")
        self.access_var = tk.StringVar()
        self.status_var = tk.StringVar()

        self.memory = []
        self.cache = []
        self.replace_queue = []
        self.mapping_type = None
        self.cache_size = 0
        self.memory_size = 0
        self.set_size = 1
        self.num_sets = 0

        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style(self)

        style.configure("Custom.TButton",
                        background="#0B3D91",
                        foreground="white",
                        font=("Arial", 11, "bold"),
                        padding=6)
        style.map("Custom.TButton",
                  background=[("active", "#4274E0"), ("!active", "#0B3D91")],
                  foreground=[("active", "#0B3D91"), ("!active", "#4274E0")])

        style.configure("TLabelframe",
                        background="SystemButtonFace",
                        bordercolor="SystemButtonFace")
        style.configure("TLabelframe.Label",
                        foreground="#154360",
                        font=("Arial", 18, "bold"),
                        background="SystemButtonFace")

        style.configure("Blue.TLabel",
                        foreground="#154360",
                        font=("Arial", 14),
                        background="SystemButtonFace")

        style.configure("Treeview", font=("Arial", 12), padding=(0, 2))
        style.map("Treeview", background=[("selected", "#B2C8DF")])

        style.configure("Custom.TRadiobutton",
                        font=("Arial", 14),
                        foreground="#154360")

    def create_widgets(self):
        frame_config = ttk.LabelFrame(self, text="Configuration")
        frame_config.pack(padx=7, pady=7, anchor="n")

        for i in range(4):
            # column 1 (Entries) is made as small as possible
            if i == 1:
                frame_config.grid_columnconfigure(i, weight=0, minsize=1)
            else:
                frame_config.grid_columnconfigure(i, minsize=120)

        ttk.Label(frame_config, text="Main Memory Size (blocks):", style="Blue.TLabel").grid(
            row=0, column=0, sticky="w", padx=2, pady=3)
        ttk.Entry(frame_config, textvariable=self.memory_size_var, width=4, font=("Arial", 14)).grid(
            row=0, column=1, sticky="ew", padx=0)

        ttk.Label(frame_config, text="Cache Size (blocks):", style="Blue.TLabel").grid(
            row=1, column=0, sticky="w", padx=2, pady=3)
        ttk.Entry(frame_config, textvariable=self.cache_size_var, width=4, font=("Arial", 14)).grid(
            row=1, column=1, sticky="ew", padx=0)

        ttk.Label(frame_config, text="Mapping Technique:", style="Blue.TLabel").grid(
            row=2, column=0, sticky="w", padx=2, pady=3)

        rb_direct = ttk.Radiobutton(frame_config, text="Direct", variable=self.mapping_var, value="direct",
                                    command=self.toggle_set_size, style="Custom.TRadiobutton")
        rb_assoc = ttk.Radiobutton(frame_config, text="Associative", variable=self.mapping_var, value="associative",
                                   command=self.toggle_set_size, style="Custom.TRadiobutton")
        rb_setassoc = ttk.Radiobutton(frame_config, text="Set-Associative", variable=self.mapping_var, value="set-associative",
                                      command=self.toggle_set_size, style="Custom.TRadiobutton")
        rb_direct.grid(row=2, column=1, sticky="w", padx=8, pady=2)
        rb_assoc.grid(row=2, column=2, sticky="w", padx=8, pady=2)
        rb_setassoc.grid(row=2, column=3, sticky="w", padx=8, pady=2)

        ttk.Label(frame_config, text="Blocks per Set (for Set-Associative):", style="Blue.TLabel").grid(
            row=3, column=0, sticky="w", padx=2, pady=3)
        self.set_size_entry = ttk.Entry(frame_config, textvariable=self.set_size_var, width=7, font=("Arial", 14))
        self.set_size_entry.grid(row=3, column=1, sticky="w", padx=0)

        self.btn_init = ttk.Button(frame_config, text="Initialize Cache Simulator",
                                  command=self.initialize_simulator, style="Custom.TButton")
        self.btn_init.grid(row=4, column=0, columnspan=4, pady=8)

        frame_access = ttk.LabelFrame(self, text="Memory Block Access")
        frame_access.pack(padx=7, pady=5, anchor="n")

        ttk.Label(frame_access, text="Enter Memory Block Address:", style="Blue.TLabel").grid(
            row=0, column=0, sticky="w", padx=2, pady=2)
        self.entry_access = ttk.Entry(frame_access, textvariable=self.access_var, width=18, font=("Arial", 14))
        self.entry_access.grid(row=0, column=1, sticky="w", padx=2)
        self.entry_access.bind("<Return>", lambda e: self.access_block())

        self.btn_access = ttk.Button(frame_access, text="Access Block", command=self.access_block, style="Custom.TButton")
        self.btn_access.grid(row=0, column=2, padx=2)

        self.lbl_status = ttk.Label(self, textvariable=self.status_var, font=("Arial", 14, "bold"),
                                   foreground="#0B5345", background="#AACADD")
        self.lbl_status.pack(pady=3, anchor="n")

        frame_cache = ttk.LabelFrame(self, text="Cache Content")
        frame_cache.pack(fill="both", expand=True, padx=7, pady=9)

        columns = ("Index", "Tag", "Data")
        self.tree = ttk.Treeview(frame_cache, columns=columns, show="headings", height=15)
        self.tree.heading("Index", text="Index")
        self.tree.heading("Tag", text="Tag")
        self.tree.heading("Data", text="Data")
        self.tree.column("Index", anchor="center", width=75)
        self.tree.column("Tag", anchor="center", width=50)  # much less wide
        self.tree.column("Data", anchor="center", width=130)
        self.tree.pack(fill="both", expand=True)

        self.set_size_entry.config(state="disabled")
        self.entry_access.config(state="disabled")
        self.btn_access.config(state="disabled")

        self.tree.tag_configure('cache', background='#EBF5FB', foreground='#154360', font=("Arial", 12))

        for btn in [self.btn_init, self.btn_access]:
            btn.bind("<Enter>", lambda e, b=btn: b.state(['active']))
            btn.bind("<Leave>", lambda e, b=btn: b.state(['!active']))

    def toggle_set_size(self):
        if self.mapping_var.get() == "set-associative":
            self.set_size_entry.config(state="normal")
        else:
            self.set_size_entry.config(state="disabled")

    def initialize_simulator(self):
        try:
            self.memory_size = int(self.memory_size_var.get())
            self.cache_size = int(self.cache_size_var.get())
            if self.memory_size <= 0 or self.cache_size <= 0:
                raise ValueError
            self.mapping_type = self.mapping_var.get()
            if self.mapping_type == "set-associative":
                self.set_size = int(self.set_size_var.get())
                if self.set_size <= 0 or self.cache_size % self.set_size != 0:
                    messagebox.showerror("Error", "Cache size must be divisible by blocks per set for Set-Associative.")
                    return
                self.num_sets = self.cache_size // self.set_size
            else:
                self.set_size = 1
                self.num_sets = 0
        except ValueError:
            messagebox.showerror("Error", "Please enter valid positive integers.")
            return

        self.memory = [random.randint(0, 255) for _ in range(self.memory_size)]

        if self.mapping_type == "direct":
            self.cache = [None] * self.cache_size
        elif self.mapping_type == "associative":
            self.cache = [None] * self.cache_size
            self.replace_queue = []
        else:
            self.cache = [[None] * self.set_size for _ in range(self.num_sets)]
            self.replace_queue = [[] for _ in range(self.num_sets)]

        self.entry_access.config(state="normal")
        self.btn_access.config(state="normal")
        self.status_var.set("Cache initialized. Ready to access blocks.")
        self.update_cache_display()

    def access_block(self):
        block_str = self.access_var.get()
        if not block_str.isdigit():
            messagebox.showwarning("Warning", "Please enter a valid non-negative integer block address.")
            return
        block_addr = int(block_str)
        if block_addr >= self.memory_size or block_addr < 0:
            messagebox.showwarning("Warning", f"Block address must be between 0 and {self.memory_size - 1}.")
            return

        hit = self.simulate_access(block_addr)
        status_text = f"Accessing block {block_addr}: {'HIT ✅' if hit else 'MISS ❌'}"
        self.status_var.set(status_text)
        self.update_cache_display()
        self.access_var.set("")

    def simulate_access(self, block_addr):
        data = self.memory[block_addr]
        hit = False

        if self.mapping_type == "direct":
            index = block_addr % self.cache_size
            tag = block_addr // self.cache_size
            line = self.cache[index]
            if line and line['tag'] == tag:
                hit = True
            else:
                self.cache[index] = {'tag': tag, 'data': data}

        elif self.mapping_type == "associative":
            tag = block_addr
            for i, line in enumerate(self.cache):
                if line and line['tag'] == tag:
                    hit = True
                    break
            if not hit:
                if len(self.replace_queue) >= self.cache_size:
                    to_replace = self.replace_queue.pop(0)
                    self.cache[to_replace] = {'tag': tag, 'data': data}
                    self.replace_queue.append(to_replace)
                else:
                    for i in range(self.cache_size):
                        if not self.cache[i]:
                            self.cache[i] = {'tag': tag, 'data': data}
                            self.replace_queue.append(i)
                            break

        else:  # set-associative
            set_index = block_addr % self.num_sets
            tag = block_addr // self.num_sets
            cache_set = self.cache[set_index]

            for i, line in enumerate(cache_set):
                if line and line['tag'] == tag:
                    hit = True
                    break
            if not hit:
                if len(self.replace_queue[set_index]) >= self.set_size:
                    to_replace = self.replace_queue[set_index].pop(0)
                    cache_set[to_replace] = {'tag': tag, 'data': data}
                    self.replace_queue[set_index].append(to_replace)
                else:
                    for i in range(self.set_size):
                        if not cache_set[i]:
                            cache_set[i] = {'tag': tag, 'data': data}
                            self.replace_queue[set_index].append(i)
                            break

        return hit

    def update_cache_display(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if self.mapping_type == "direct":
            self.tree["columns"] = ("Index", "Tag", "Data")
            self.tree.heading("Index", text="Index")
            self.tree.heading("Tag", text="Tag")
            self.tree.heading("Data", text="Data")
            self.tree.column("Index", width=75)
            self.tree.column("Tag", width=50)
            self.tree.column("Data", width=130)

            for i, line in enumerate(self.cache):
                tag = line['tag'] if line else "-"
                data = line['data'] if line else "-"
                self.tree.insert("", "end", values=(i, tag, data), tags=('cache',))
        elif self.mapping_type == "associative":
            self.tree["columns"] = ("Line", "Tag", "Data")
            self.tree.heading("Line", text="Line")
            self.tree.heading("Tag", text="Tag")
            self.tree.heading("Data", text="Data")
            self.tree.column("Line", width=85)
            self.tree.column("Tag", width=130)
            self.tree.column("Data", width=130)

            for i, line in enumerate(self.cache):
                tag = line['tag'] if line else "-"
                data = line['data'] if line else "-"
                self.tree.insert("", "end", values=(i, tag, data), tags=('cache',))
        else:
            self.tree["columns"] = ("Set", "Block", "Tag", "Data")
            self.tree.heading("Set", text="Set")
            self.tree.heading("Block", text="Block")
            self.tree.heading("Tag", text="Tag")
            self.tree.heading("Data", text="Data")
            self.tree.column("Set", width=85)
            self.tree.column("Block", width=60)
            self.tree.column("Tag", width=130)
            self.tree.column("Data", width=130)

            for s, cache_set in enumerate(self.cache):
                for b, line in enumerate(cache_set):
                    tag = line['tag'] if line else "-"
                    data = line['data'] if line else "-"
                    self.tree.insert("", "end", values=(s, b, tag, data), tags=('cache',))

        self.tree.tag_configure('cache', background='#EBF5FB', foreground='#154360', font=("Arial", 12))

if __name__ == "__main__":
    app = CacheSimulatorGUI()
    app.mainloop()
