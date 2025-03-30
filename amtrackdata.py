import requests
import networkx as nx
import matplotlib.pyplot as plt

trains_data = requests.get("https://api-v3.amtraker.com/v3/trains").json()

G = nx.DiGraph()
for train_id, train_list in trains_data.items():
    for train in train_list:
        stations = [s["code"] for s in train["stations"] if s["code"]]
        for i in range(len(stations) - 1):
            src, dst = stations[i], stations[i + 1]
            G.add_edge(src, dst, weight=G[src][dst]["weight"] + 1 if G.has_edge(src, dst) else 1)

degrees = dict(G.degree(weight="weight"))
top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:20]
top_node_set = set(node for node, _ in top_nodes)

subG = G.subgraph([n for n in G.nodes() if n in top_node_set or any(n2 in top_node_set for n2 in G.neighbors(n))]).copy()

eigen_centrality = nx.eigenvector_centrality(subG, weight="weight", max_iter=1000)
top_eigen = sorted(eigen_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
print("Top 5 stations by eigenvector centrality:")
for node, value in top_eigen:
    print(f"{node} {round(value, 4)}")

plt.figure(figsize=(14, 10))
pos = nx.spring_layout(subG, k=1.5, iterations=100)
node_sizes = [degrees.get(node, 0) * 40 for node in subG.nodes()]
nx.draw_networkx_nodes(subG, pos, node_size=node_sizes, node_color="skyblue", alpha=0.6, edgecolors="black", linewidths=1.5)
nx.draw_networkx_nodes(subG, pos, nodelist=[s[0] for s in top_nodes], node_size=[s[1] * 40 for s in top_nodes], node_color="red", alpha=0.9, edgecolors="black", linewidths=1.5)
nx.draw_networkx_edges(subG, pos, alpha=0.2, arrowsize=8, width=0.5)
nx.draw_networkx_labels(subG, pos, {node: node for node in [s[0] for s in top_nodes]}, font_size=8, font_weight="bold")
plt.title("Top Amtrak Stations Network")
plt.axis("off")
plt.savefig("amtrak_network_readable.png", dpi=300)