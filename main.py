import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from tkinter import Tk, Label, Button, Text, Entry, StringVar, END, messagebox, Frame
from tkinter import ttk
from PIL import Image, ImageTk
import tempfile
import os
import re

BG = "#1e1e1e"
TEXT_BG = "#2e2e2e"
BTN_BG = "#3e3e3e"
FG = "white"
IMG_SIZE = (500, 300)
NODE_CLR = "#00acc1"


class GraphManager:
    def __init__(self):
        self.graph = {}
        # Cached nx_graph updated only in build for efficiency
        self.nx_graph = nx.DiGraph()

    def build(self, text):
        if not text.strip():
            raise ValueError("Input cannot be empty")
        self.graph.clear()
        self.nx_graph.clear()
        for i, line in enumerate(text.strip().splitlines(), 1):
            try:
                node, neighbors = map(str.strip, line.upper().split(":"))
                if not node:
                    raise ValueError(f"Line {i}: Node name cannot be empty")
                if node in self.graph:
                    raise ValueError(f"Line {i}: Duplicate node definition: '{node}'")
                if not re.match(r"^[a-zA-Z0-9_]+$", node):
                    raise ValueError(
                        f"Line {i}: Node name '{node}' contains invalid characters (use a-z, A-Z, 0-9, _)"
                    )
                neighbor_list = (
                    [n.strip() for n in neighbors.split() if n.strip()]
                    if neighbors.strip()
                    else []
                )
                for neighbor in neighbor_list:
                    if not neighbor:
                        raise ValueError(f"Line {i}: Neighbor name cannot be empty")
                    if not re.match(r"^[a-zA-Z0-9_]+$", neighbor):
                        raise ValueError(
                            f"Line {i}: Neighbor name '{neighbor}' contains invalid characters (use a-z, A-Z, 0-9, _)"
                        )
                self.graph[node] = neighbor_list
                self.nx_graph.add_edges_from((node, n) for n in neighbor_list)
            except ValueError as e:
                if str(e).startswith("Line"):
                    raise
                raise ValueError(
                    f"Line {i}: Each line must be in the format 'NODE: NEIGHBOR1 NEIGHBOR2 ...'"
                )

    def draw(self):
        if not self.graph:
            raise ValueError("Graph is empty")
        node_count = len(self.nx_graph.nodes)
        node_size = max(800, 1500 // (node_count // 10 + 1))
        font_size = max(10, 16 // (node_count // 20 + 1))
        try:
            pos = nx.nx_agraph.graphviz_layout(
                self.nx_graph, prog="dot", args="-Grankdir=LR"
            )
        except (ImportError, AttributeError):
            pos = nx.spring_layout(self.nx_graph)
            messagebox.showwarning(
                "Warning",
                "Graphviz not available, using spring layout. Complex graphs may appear cluttered.",
            )
        plt.figure(facecolor=BG)
        nx.draw(
            self.nx_graph,
            pos,
            with_labels=True,
            node_color=NODE_CLR,
            edge_color=FG,
            font_color=FG,
            font_size=font_size,
            node_size=node_size,
            arrows=True,
        )
        plt.title("Graph", color=FG)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            plt.savefig(tmp.name, facecolor=BG)
            plt.close()
            with Image.open(tmp.name) as img:
                img = img.resize(IMG_SIZE, Image.Resampling.LANCZOS)
                tk_img = ImageTk.PhotoImage(img)
            try:
                os.unlink(tmp.name)
            except OSError:
                pass
        return tk_img

    def bfs(self, start):
        # Note: Only reachable nodes are included; extend to include all nodes if needed
        all_nodes = set(self.graph).union(*self.graph.values())
        if start not in all_nodes:
            raise ValueError(f"Node '{start}' not in graph")
        visited, queue, order = set(), deque([start]), []
        while queue:
            node = queue.popleft()
            if node not in visited:
                visited.add(node)
                order.append(node)
                for neighbor in self.graph.get(node, []):
                    if neighbor not in visited:
                        queue.append(neighbor)
        return order

    def dfs(self, start):
        # Note: Only reachable nodes are included; extend to include all nodes if needed
        all_nodes = set(self.graph).union(*self.graph.values())
        if start not in all_nodes:
            raise ValueError(f"Node '{start}' not in graph")
        visited, order, stack = set(), [], [start]
        while stack:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                order.append(node)
                for neighbor in reversed(self.graph.get(node, [])):
                    if neighbor not in visited:
                        stack.append(neighbor)
        return order


class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Traversal")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.root.geometry("600x600")
        self.g = GraphManager()
        self.algo = StringVar(value="bfs")
        self.img = None
        self._ui()
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)

    def _ui(self):
        for i, w in enumerate([0, 1, 1, 0]):
            self.root.grid_rowconfigure(i, weight=w)
        self.root.grid_columnconfigure(0, weight=1)

        # Input section
        input_frame = Frame(self.root, bg=BG)
        input_frame.grid(row=0, column=0, pady=5, sticky="n")
        Label(
            input_frame,
            text="Graph (e.g., A: A B C, self-loops allowed):",
            bg=BG,
            fg=FG,
        ).grid(row=0, column=0, columnspan=2, pady=5)
        self.input = Text(
            input_frame, height=10, width=40, bg=TEXT_BG, fg=FG, insertbackground=FG
        )
        self.input.grid(row=1, column=0, pady=5, padx=5, sticky="e")
        button_frame = Frame(input_frame, bg=BG)
        button_frame.grid(row=1, column=1, pady=5, padx=5, sticky="w")
        Button(
            button_frame, text="Build", command=self.build, bg=BTN_BG, fg=FG, width=10
        ).pack(pady=2)
        Button(
            button_frame, text="Draw", command=self.draw, bg=BTN_BG, fg=FG, width=10
        ).pack(pady=2)

        # Image display
        self.img_label = Label(self.root, bg=BG)
        self.img_label.grid(row=1, column=0, pady=5, sticky="nsew")

        # Controls
        control_frame = Frame(self.root, bg=BG)
        control_frame.grid(row=2, column=0, pady=5, sticky="nsew")
        control_frame.grid_columnconfigure(0, weight=1)
        control_frame.grid_columnconfigure(1, weight=1)
        Label(control_frame, text="Start:", bg=BG, fg=FG).grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.start = Entry(control_frame, bg=TEXT_BG, fg=FG, insertbackground=FG)
        self.start.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        Label(control_frame, text="Algo:", bg=BG, fg=FG).grid(
            row=1, column=0, padx=5, pady=5, sticky="e"
        )
        style = ttk.Style()
        style.configure("TMenubutton", background=BTN_BG, foreground=FG)
        style.map("TMenubutton", background=[("active", BTN_BG)])
        menu = ttk.OptionMenu(
            control_frame, self.algo, "bfs", "bfs", "dfs", style="TMenubutton"
        )
        menu.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        Button(
            control_frame, text="Run", command=self.run, bg=BTN_BG, fg=FG, width=10
        ).grid(row=2, column=0, columnspan=2, pady=5)

        # Output
        self.out = Label(
            self.root, text="Output:", bg=BG, fg=FG, font=("Helvetica", 16, "bold")
        )
        self.out.grid(row=3, column=0, pady=5, sticky="nsew")

    def build(self):
        try:
            self.g.build(self.input.get("1.0", END))
            self.algo.set("bfs")
            self.img_label.config(image="")
            self.out.config(text="Output:")
            messagebox.showinfo("Success", "Graph built!")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def draw(self):
        try:
            self.img_label.config(image="")
            tk_img = self.g.draw()
            self.img = tk_img
            self.img_label.config(image=self.img)
        except ValueError as e:
            messagebox.showerror("Error", f"Draw failed: {str(e)}")
        except IOError as e:
            messagebox.showerror(
                "Error", f"Draw failed: {str(e)}. Check disk permissions or space."
            )
        except ImportError as e:
            messagebox.showerror("Error", f"Draw failed: {str(e)}")

    def run(self):
        start = self.start.get().strip().upper()
        if not self.g.graph:
            self.out.config(text="Output:")
            self.start.delete(0, END)
            messagebox.showerror("Error", "Graph is empty")
            return
        method = self.g.bfs if self.algo.get() == "bfs" else self.g.dfs
        try:
            result = method(start)
            self.out.config(text=f"Output: {' → '.join(result)}")
        except ValueError as e:
            self.out.config(text="Output:")
            self.start.delete(0, END)
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = Tk()
    app = GraphApp(root)
    root.mainloop()
