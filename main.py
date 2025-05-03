import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
from tkinter import Tk, Label, Button, Text, Entry, OptionMenu, StringVar, END
from tkinter import messagebox
from PIL import Image, ImageTk  # Removed the unnecessary ImageResampling import

class GraphApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Graph Traversal GUI")
        self.graph = {}

        # Instructions
        Label(root, text="Enter graph as 'Node: Neighbor1 Neighbor2' (one per line):").pack()
        self.text_input = Text(root, height=10, width=50)
        self.text_input.pack()

        # Buttons
        Button(root, text="Build Graph", command=self.build_graph).pack(pady=2)
        Button(root, text="Draw Graph", command=self.draw_graph).pack(pady=2)

        # Start node input and algorithm choice
        Label(root, text="Start Node:").pack()
        self.start_entry = Entry(root)
        self.start_entry.pack()

        Label(root, text="Choose Algorithm:").pack()
        self.algorithm = StringVar()
        self.algorithm.set("bfs")
        OptionMenu(root, self.algorithm, "bfs", "dfs").pack()

        Button(root, text="Run Traversal", command=self.run_traversal).pack(pady=5)

        # Traversal result output
        self.output_label = Label(root, text="Traversal Output:")
        self.output_label.pack()

        # Image display
        self.image_label = Label(root)
        self.image_label.pack()

    def build_graph(self):
        self.graph.clear()
        lines = self.text_input.get("1.0", END).strip().splitlines()
        for line in lines:
            try:
                node, neighbors = line.split(":")
                node = node.strip().upper()
                neighbor_list = neighbors.strip().upper().split()
                self.graph[node] = neighbor_list
            except ValueError:
                messagebox.showerror("Format Error", "Each line must be like 'A: B C'")
                return
        messagebox.showinfo("Graph Built", "Graph has been built successfully!")

    def draw_graph(self):
        G = nx.DiGraph()
        for node, neighbors in self.graph.items():
            for neighbor in neighbors:
                G.add_edge(node, neighbor)

        pos = nx.nx_agraph.graphviz_layout(G, prog='dot', args='-Grankdir=LR')
        nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1500, font_size=16, arrows=True)
        plt.title("Graph Visualization")
        plt.savefig('Graph.png')
        plt.clf()

        img = Image.open("Graph.png")
        img = img.resize((500, 300), Image.Resampling.LANCZOS)  # Correct usage of Resampling.LANCZOS
        self.tk_img = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.tk_img)

    def bfs(self, start):
        visited = set()
        queue = deque([start])
        order = []

        while queue:
            node = queue.popleft()
            if node not in visited:
                order.append(node)
                visited.add(node)
                queue.extend(self.graph.get(node, []))
        return order

    def dfs(self, start, visited=None, order=None):
        if visited is None:
            visited = set()
        if order is None:
            order = []

        order.append(start)
        visited.add(start)

        for neighbor in self.graph.get(start, []):
            if neighbor not in visited:
                self.dfs(neighbor, visited, order)

        return order

    def run_traversal(self):
        start = self.start_entry.get().strip().upper()
        if start not in self.graph:
            messagebox.showerror("Invalid Node", f"Node '{start}' not found in graph.")
            return

        algo = self.algorithm.get()
        if algo == 'bfs':
            result = self.bfs(start)
        else:
            result = self.dfs(start)

        self.output_label.config(text=f"Traversal Output: {' → '.join(result)}")

# Run the app
if __name__ == "__main__":
    root = Tk()
    app = GraphApp(root)
    root.mainloop()

