import os
import argparse
import json
import networkx as nx
import matplotlib.pyplot as plt

from history_tracer import _load_log

LOG_DIR = os.path.join('glyph_memory', 'logs')

def plot_adjacency_graph(output='adjacency_graph.png'):
    G = nx.DiGraph()
    entries = _load_log('adjacency_walk.log')
    for e in entries:
        src = e.get('from')
        dst = e.get('to')
        if src and dst:
            G.add_edge(src, dst)
    if not G:
        print('No adjacency data found')
        return
    plt.figure(figsize=(8,6))
    nx.draw_networkx(G, node_color='lightblue', edge_color='gray', with_labels=True)
    plt.tight_layout()
    plt.savefig(output)
    print(f'Graph saved to {output}')


def plot_weight_history(token, output='weight_history.png'):
    entries = [e for e in _load_log('weight_updates.log') if e.get('token') == token]
    if not entries:
        print('No weight history for token')
        return
    weights = [e['new_weight'] for e in entries]
    plt.figure(figsize=(6,4))
    plt.plot(range(len(weights)), weights, marker='o')
    plt.title(f'Weight over time for {token}')
    plt.xlabel('update')
    plt.ylabel('weight')
    plt.tight_layout()
    plt.savefig(output)
    print(f'History saved to {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Visualize SKG engine history')
    parser.add_argument('--graph', action='store_true', help='Plot adjacency graph')
    parser.add_argument('--token', help='Plot weight history for token')
    parser.add_argument('--out', default=None, help='Output image path')
    args = parser.parse_args()

    if args.graph:
        out = args.out or 'adjacency_graph.png'
        plot_adjacency_graph(out)
    if args.token:
        out = args.out or f'{args.token}_weights.png'
        plot_weight_history(args.token, out)
    if not args.graph and not args.token:
        parser.print_help()
