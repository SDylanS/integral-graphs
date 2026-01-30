import networkx as nx
import matplotlib.pyplot as plt

grafy_g6 = [
    "N@rIASH_CP_Z@Hr~_?g"
]

for i, g6 in enumerate(grafy_g6):
    G = nx.from_graph6_bytes(g6.encode('ascii'))
    plt.figure(figsize=(6, 6))
    pos = nx.circular_layout(G) 
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500)
    plt.title(f"Graf Całkowity #{i+1}")
    plt.savefig(f"graf_{i+1}.png")
    print(f"Wygenerowano graf_{i+1}.png")