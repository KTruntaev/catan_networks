import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

# ============================================================================
# Visualization
# ============================================================================

# Mapping from resource name -> hex fill color
RESOURCE_COLORS = {
    'wood':   '#2d6a1e',   # dark green
    'wheat':  '#f5c542',   # golden yellow
    'sheep':  '#a8d948',   # light green
    'brick':  '#c45a2c',   # terracotta
    'ore':    '#8a8a8a',   # grey
    'desert': '#f0e0a0',   # sand
}

def draw_board(G, hex_centers, tile_data=None, node_labels=True, node_colors=None,
               title="Catan Board", ax=None, cmap='YlOrRd', colorbar=True):
    """
    Draw the Catan board with hex tiles and intersection nodes.

    Parameters
    ----------
    G : nx.Graph
        The intersection graph (from generate_catan_board).
    hex_centers : list of (x, y)
        Tile center coordinates (from generate_catan_board).
    tile_data : list of (resource, number) tuples (length 19), or None
        Specifies the resource type and number token for each tile, in the
        same reading order as hex_centers. Example:
            [('wood', 8), ('brick', 10), ..., ('desert', 0)]
        If None, all hexes are drawn as plain outlines.
    node_labels : bool or dict
        - True  -> label each node with its index (0-53)
        - False -> no labels
        - dict  -> custom labels, e.g. {0: "A", 1: "B", ...}
    node_colors : list/array of numeric values, or None
        If provided, nodes are colored by this value using `cmap`.
    title : str
        Plot title.
    ax : matplotlib Axes, optional
        Axes to draw on. If None, a new 10x10 figure is created.
    cmap : str
        Matplotlib colormap name (used when node_colors is provided).
    colorbar : bool
        Whether to add a colorbar when node_colors is provided.

    Returns
    -------
    fig, ax : the matplotlib Figure and Axes (for further customization)
    """
    from matplotlib.patches import RegularPolygon

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
    else:
        fig = ax.figure

    # --- Draw hex tiles ---
    for i, (cx, cy) in enumerate(hex_centers):
        if tile_data is not None:
            resource, number = tile_data[i]
            facecolor = RESOURCE_COLORS[resource]
            alpha = 0.5
        else:
            facecolor = '#d4e8c2'
            alpha = 0.4

        # orientation=0 gives pointy-top in matplotlib (vertex at 12 o'clock)
        ax.add_patch(RegularPolygon(
            (cx, cy), 6, radius=1.0, orientation=0,
            facecolor=facecolor, edgecolor='#333', linewidth=1.5, alpha=alpha
        ))

        # Number token label (skip desert)
        if tile_data is not None:
            resource, number = tile_data[i]
            if number > 0:
                # 6 and 8 are the most probable rolls -> red for emphasis
                color = 'red' if number in (6, 8) else 'black'
                ax.text(cx, cy, str(number), ha='center', va='center',
                        fontsize=14, fontweight='bold', color=color)
            else:
                ax.text(cx, cy, 'D', ha='center', va='center',
                        fontsize=14, fontweight='bold', color='#8B7355')

    # --- Draw graph edges (road segments) ---
    pos = nx.get_node_attributes(G, 'pos')
    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#888', width=1.5, alpha=0.6)

    # --- Draw graph nodes (intersections / settlement spots) ---
    if node_colors is not None:
        nc = nx.draw_networkx_nodes(G, pos, ax=ax, node_size=250,
                                    node_color=node_colors, cmap=cmap,
                                    edgecolors='black', linewidths=1)
        if colorbar and nc is not None:
            plt.colorbar(nc, ax=ax, shrink=0.6, label=title)
    else:
        nx.draw_networkx_nodes(G, pos, ax=ax, node_size=250,
                               node_color='#e67e22',
                               edgecolors='black', linewidths=1)

    # --- Node labels ---
    if node_labels is True:
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=7, font_weight='bold')
    elif isinstance(node_labels, dict):
        nx.draw_networkx_labels(G, pos, labels=node_labels, ax=ax,
                                font_size=7, font_weight='bold')

    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=13)
    return fig, ax


def draw_edge_resources(G, hex_centers, tile_data, resource=None,
                        title=None, ax=None, cmap='YlOrRd', colorbar=True):
    """
    Visualize edge weights (resource pips) as colored, thickness-scaled road segments.

    Parameters
    ----------
    G : nx.Graph
        The intersection graph with edge resources already computed.
    hex_centers : list of (x, y)
        Tile center coordinates.
    tile_data : list of (resource, number) tuples (length 19)
        For drawing the hex background.
    resource : str or None
        A specific resource ('wheat', 'ore', etc.) to visualize,
        or None to show total_pips across all resources.
    title : str or None
        Plot title. Auto-generated if None.
    ax : matplotlib Axes, optional
    cmap : str
        Colormap for edge coloring.
    colorbar : bool
        Whether to show a colorbar.

    Returns
    -------
    fig, ax
    """
    from matplotlib.patches import RegularPolygon
    from matplotlib.collections import LineCollection
    import matplotlib.cm as cm
    import matplotlib.colors as mcolors

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
    else:
        fig = ax.figure

    if title is None:
        title = f"Edge Resources: {resource if resource else 'total pips'}"

    # --- Draw hex tiles (faded background) ---
    for i, (cx, cy) in enumerate(hex_centers):
        res, number = tile_data[i]
        facecolor = RESOURCE_COLORS[res]
        ax.add_patch(RegularPolygon(
            (cx, cy), 6, radius=1.0, orientation=0,
            facecolor=facecolor, edgecolor='#333', linewidth=1.0, alpha=0.3
        ))
        if number > 0:
            color = 'red' if number in (6, 8) else 'black'
            ax.text(cx, cy, str(number), ha='center', va='center',
                    fontsize=12, fontweight='bold', color=color, alpha=0.5)
        else:
            ax.text(cx, cy, 'D', ha='center', va='center',
                    fontsize=12, fontweight='bold', color='#8B7355', alpha=0.5)

    # --- Collect edge weights ---
    pos = nx.get_node_attributes(G, 'pos')
    attr = resource if resource else 'total_pips'

    edge_vals = []
    segments = []
    for u, v in G.edges():
        val = G[u][v].get(attr, 0)
        edge_vals.append(val)
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        segments.append([(x0, y0), (x1, y1)])

    edge_vals = np.array(edge_vals, dtype=float)
    vmin, vmax = edge_vals.min(), edge_vals.max()

    # Normalize for color and width
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    colormap = cm.get_cmap(cmap)

    # Width: scale from 1 (min) to 8 (max)
    if vmax > vmin:
        widths = 3
    else:
        widths = np.full_like(edge_vals, 3.0)

    lc = LineCollection(segments, linewidths=widths, cmap=colormap, norm=norm)
    lc.set_array(edge_vals)
    ax.add_collection(lc)

    if colorbar:
        plt.colorbar(lc, ax=ax, shrink=0.6, label=f"Pips ({attr})")

    # --- Draw nodes (small, neutral) ---
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=80,
                           node_color='white', edgecolors='#555', linewidths=0.8)

    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=13)
    # Need to autoscale since we used add_collection
    ax.autoscale_view()
    return fig, ax


# Player colors for game state visualization
PLAYER_COLORS = {
    0: '#e63946',   # red
    1: '#457b9d',   # blue
    2: '#2a9d8f',   # teal
    3: '#e9c46a',   # gold
}
UNOWNED_NODE_COLOR = '#d4d4d4'
UNOWNED_EDGE_COLOR = '#aaaaaa'


def draw_game_state(G, hex_centers, tile_data, title="Game State", ax=None):
    """
    Visualize the current game state with settlements and roads colored by owner.

    Owned settlements are drawn larger and in the player's color.
    Owned roads are drawn thicker and in the player's color.
    Unowned nodes/edges are drawn small and grey.

    Parameters
    ----------
    G : nx.Graph
        The intersection graph with 'owner' attributes on nodes and edges.
        owner = -1 means unowned, 0-3 means player id.
    hex_centers : list of (x, y)
        Tile center coordinates.
    tile_data : list of (resource, number) tuples (length 19)
    title : str
        Plot title.
    ax : matplotlib Axes, optional

    Returns
    -------
    fig, ax
    """
    from matplotlib.patches import RegularPolygon
    from matplotlib.collections import LineCollection

    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
    else:
        fig = ax.figure

    # --- Draw hex tiles ---
    for i, (cx, cy) in enumerate(hex_centers):
        resource, number = tile_data[i]
        facecolor = RESOURCE_COLORS[resource]
        ax.add_patch(RegularPolygon(
            (cx, cy), 6, radius=1.0, orientation=0,
            facecolor=facecolor, edgecolor='#333', linewidth=1.5, alpha=0.5
        ))
        if number > 0:
            color = 'red' if number in (6, 8) else 'black'
            ax.text(cx, cy, str(number), ha='center', va='center',
                    fontsize=14, fontweight='bold', color=color)
        else:
            ax.text(cx, cy, 'D', ha='center', va='center',
                    fontsize=14, fontweight='bold', color='#8B7355')

    # --- Draw edges by ownership ---
    pos = nx.get_node_attributes(G, 'pos')

    # Unowned edges first (thin, grey)
    unowned_segments = []
    for u, v in G.edges():
        if G[u][v].get('owner', -1) == -1:
            unowned_segments.append([pos[u], pos[v]])
    if unowned_segments:
        lc = LineCollection(unowned_segments, linewidths=1.5,
                            colors=UNOWNED_EDGE_COLOR, alpha=0.4)
        ax.add_collection(lc)

    # Owned edges per player (thick, colored)
    for pid, pcolor in PLAYER_COLORS.items():
        segments = []
        for u, v in G.edges():
            if G[u][v].get('owner', -1) == pid:
                segments.append([pos[u], pos[v]])
        if segments:
            lc = LineCollection(segments, linewidths=5, colors=pcolor, alpha=0.9)
            ax.add_collection(lc)

    # --- Draw nodes by ownership ---
    # Unowned nodes
    unowned = [n for n in G.nodes() if G.nodes[n].get('owner', -1) == -1]
    if unowned:
        nx.draw_networkx_nodes(G, pos, nodelist=unowned, ax=ax,
                               node_size=80, node_color=UNOWNED_NODE_COLOR,
                               edgecolors='#999', linewidths=0.8)

    # Owned nodes per player (larger, colored, bold border)
    for pid, pcolor in PLAYER_COLORS.items():
        owned = [n for n in G.nodes() if G.nodes[n].get('owner', -1) == pid]
        if owned:
            nx.draw_networkx_nodes(G, pos, nodelist=owned, ax=ax,
                                   node_size=400, node_color=pcolor,
                                   edgecolors='black', linewidths=2)
            # Label owned nodes with player id
            labels = {n: str(pid) for n in owned}
            nx.draw_networkx_labels(G, pos, labels=labels, ax=ax,
                                   font_size=9, font_weight='bold',
                                   font_color='white')

    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=13)
    ax.autoscale_view()
    return fig, ax
