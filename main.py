from collections import deque
import networkx as nx
import matplotlib.pyplot as plt

# 1. Function to build a graph from user input
def build_graph():
    graph = {}
    print("Enter your graph (type 'done' when finished):")
    while True:
        node = input("Enter node name (or 'done' to finish): ").strip().upper()
        if node == 'DONE':
            break
        neighbors = input(f"Enter neighbors of {node} separated by spaces: ").strip().upper().split()
        graph[node] = neighbors
    return graph

# 2. Function to draw the graph
def draw_graph(graph):
    G = nx.DiGraph()   # Use DiGraph for a directed graph (you can change to Graph() for undirected)

    for node, neighbors in graph.items():
        for neighbor in neighbors:
            G.add_edge(node, neighbor)

    pos = nx.nx_agraph.graphviz_layout(G, prog='dot', args='-Grankdir=LR')  # Layout for better visuals
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1500, font_size=16, arrows=True)
    plt.title("Graph Visualization")
    plt.savefig('Graph.png')

# 3. Breadth-First Search (BFS)
def bfs(graph, start):
    visited = set()
    queue = deque([start])

    while queue:
        node = queue.popleft()
        if node not in visited:
            print(node, end=' ')
            visited.add(node)
            queue.extend(graph.get(node, []))

# 4. Depth-First Search (DFS)
def dfs(graph, start, visited=None):
    if visited is None:
        visited = set()
    print(start, end=' ')
    visited.add(start)

    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            dfs(graph, neighbor, visited)

# 5. Main program
def main():
    print("Graph Traversal Program")
    graph = build_graph()

    print("\nDrawing the graph...")
    draw_graph(graph)

    choice = input("\nChoose algorithm (bfs/dfs): ").strip().lower()
    start_node = input("Enter the starting node: ").strip().upper()

    if start_node not in graph:
        print(f"Node {start_node} does not exist in the graph.")
        return

    print("\nTraversal Order:")
    if choice == 'bfs':
        bfs(graph, start_node)
    elif choice == 'dfs':
        dfs(graph, start_node)
    else:
        print("Invalid choice. Please enter 'bfs' or 'dfs'.")

if __name__ == "__main__":
    main()
