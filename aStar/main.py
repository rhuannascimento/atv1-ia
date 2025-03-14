import networkx as nx
import matplotlib.pyplot as plt
import sys
import heapq
import argparse

# Árvore de busca para visualização
search_tree = nx.DiGraph()
node_counter = 0

def add_tree_node(label, parent_node_id=None):
    global node_counter
    node_id = node_counter
    node_counter += 1
    search_tree.add_node(node_id, label=label)
    if parent_node_id is not None:
        search_tree.add_edge(parent_node_id, node_id)
    return node_id

def read_graph(file_path):
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    if lines[0].upper() != "DIMENSION":
        raise ValueError("Erro: esperava 'DIMENSION' na primeira linha.")
    dimension = int(lines[1])
    
    if lines[2].upper() != "GRAPH":
        raise ValueError("Erro: esperava 'GRAPH' após a dimensão.")
    
    edges = []
    for line in lines[3:]:
        parts = line.split()
        if len(parts) >= 3:
            u = int(parts[0])
            v = int(parts[1])
            cost = float(parts[2])
            edges.append((u, v, cost))
    
    G = nx.Graph()
    G.add_nodes_from(range(1, dimension + 1))
    G.add_weighted_edges_from(edges)
    return G

def is_valid(G, vertex, color, assignment):
    for neighbor in G.neighbors(vertex):
        if neighbor in assignment and assignment[neighbor] == color:
            return False
    return True

def cost_for_vertex(G, vertex, assignment):
    custo = 0
    for neighbor in G.neighbors(vertex):
        if neighbor in assignment:
            custo += G[vertex][neighbor]["weight"]
    return custo

def heuristic(G, current_assignment, vertex):
    """
    Calcula h(n) = (Nº de vizinhos não coloridos) × (peso médio das arestas)
    """
    neighbors = list(G.neighbors(vertex))
    uncolored = len([n for n in neighbors if n not in current_assignment])
    
    total_weight = sum(G[vertex][n]["weight"] for n in neighbors)
    avg_weight = total_weight / len(neighbors) if neighbors else 0
    
    return uncolored * avg_weight

def state_to_string(state, vertices, algorithm):
    if algorithm == "astar":
        assignment, index, tree_id, g, h = state
        f = g + h
        if index > 0:
            last_vertex = vertices[index - 1]
            last_color = assignment.get(last_vertex, "")
            return f"ID {tree_id}: {last_vertex}={last_color}, g={g}, h={h}, f={f}"
        return f"ID {tree_id}: Início, g={g}, h={h}, f={f}"
    else:
        assignment, index, tree_id, custo = state
        if index > 0:
            last_vertex = vertices[index - 1]
            last_color = assignment.get(last_vertex, "")
            return f"ID {tree_id}: {last_vertex}={last_color}, Custo={custo}"
        return f"ID {tree_id}: Início, Custo={custo}"

def astar_search(G, vertices, root_id, log_filename="astar_log.txt"):
    open_list = []
    closed_states = []
    state_counter = 0

    # Correção: Calcular a heurística para o primeiro vértice
    initial_vertex = vertices[0] if vertices else None
    initial_h = heuristic(G, {}, initial_vertex) if initial_vertex else 0

    initial_state = ({}, 0, root_id, 0, initial_h)
    heapq.heappush(open_list, (initial_h + 0, state_counter, initial_state))
    state_counter += 1
    iteration = 0

    with open(log_filename, "w", encoding="utf-8") as log_file:
        while open_list:
            # ... (código de log)
            
            current_f, _, current_state = heapq.heappop(open_list)
            assignment, index, tree_id, g, h = current_state

            # --- Verificação de segurança adicionada ---
            if index >= len(vertices):
                continue
            # -------------------------------------------

            vertex = vertices[index]  # Agora seguro

            for color in [1, 2, 3, 4]:
                if is_valid(G, vertex, color, assignment):
                    new_assignment = assignment.copy()
                    new_assignment[vertex] = color
                    
                    # CÁLCULO DO CUSTO REAL (g(n))
                    new_g = g + cost_for_vertex(G, vertex, new_assignment)
                    
                    # ----> AQUI ENTRA A HEURÍSTICA <----
                    new_h = heuristic(G, new_assignment, vertex)  # Calcula h(n) para o vértice atual
                    new_f = new_g + new_h  # f(n) = g(n) + h(n)
                    # -----------------------------------
                    
                    new_index = index + 1
                    new_label = f"{vertex}={color}\ng={new_g}, h={new_h}, f={new_f}"
                    new_tree_id = add_tree_node(new_label, tree_id)
                    
                    heapq.heappush(open_list, (new_f, state_counter, (new_assignment, new_index, new_tree_id, new_g, new_h)))
                    state_counter += 1
                    
            closed_states.append(current_state)
    return None

def ordered_search(G, vertices, root_id, log_filename="ordered_log.txt"):
    open_list = []
    closed_states = []
    state_counter = 0
    initial_state = ({}, 0, root_id, 0)
    heapq.heappush(open_list, (0, state_counter, initial_state))
    state_counter += 1
    iteration = 0

    with open(log_filename, "w", encoding="utf-8") as log_file:
        while open_list:
            log_file.write(f"Iteração {iteration}:\n")
            log_file.write("Abertos: " + ", ".join([state_to_string(s, vertices, "ordered") for _, _, s in open_list]) + "\n")
            log_file.write("Fechados: " + ", ".join([state_to_string(s, vertices, "ordered") for s in closed_states]) + "\n\n")
            iteration += 1

            _, _, state = heapq.heappop(open_list)
            assignment, index, tree_node_id, current_cost = state

            if index == len(vertices):
                sol_label = f"Solução: {assignment}, Custo Total: {current_cost}"
                add_tree_node(sol_label, tree_node_id)
                return state

            vertex = vertices[index]
            for color in [1, 2, 3, 4]:
                if is_valid(G, vertex, color, assignment):
                    new_assignment = assignment.copy()
                    new_assignment[vertex] = color
                    additional_cost = cost_for_vertex(G, vertex, new_assignment)
                    new_cost = current_cost + additional_cost
                    new_index = index + 1
                    new_label = f"{vertex}={color}"
                    new_tree_node_id = add_tree_node(new_label, tree_node_id)
                    new_state = (new_assignment, new_index, new_tree_node_id, new_cost)
                    heapq.heappush(open_list, (new_cost, state_counter, new_state))
                    state_counter += 1
            closed_states.append(state)
    return None

def greedy_search(G, vertices, root_id, log_filename="greedy_log.txt"):
    assignment = {}
    current_cost = 0
    current_tree_node_id = root_id

    with open(log_filename, "w", encoding="utf-8") as log_file:
        for index, vertex in enumerate(vertices):
            log_file.write(f"\n=== Iteração para vértice {vertex} ===\n")
            abertos = []
            
            for color in [1, 2, 3, 4]:
                if is_valid(G, vertex, color, assignment):
                    new_assignment = assignment.copy()
                    new_assignment[vertex] = color
                    additional_cost = cost_for_vertex(G, vertex, new_assignment)
                    abertos.append((vertex, color, additional_cost))
            
            if not abertos:
                log_file.write("Abertos: (nenhum estado válido)\n")
                return None
            
            chosen_state = min(abertos, key=lambda x: x[2])
            (chosen_vertex, chosen_color, chosen_add_cost) = chosen_state
            
            assignment[chosen_vertex] = chosen_color
            current_cost += chosen_add_cost
            
            new_label = f"{chosen_vertex}={chosen_color}"
            current_tree_node_id = add_tree_node(new_label, current_tree_node_id)
    
    sol_label = f"Solução: {assignment}, Custo Total: {current_cost}"
    add_tree_node(sol_label, current_tree_node_id)
    return (assignment, len(vertices), current_tree_node_id, current_cost)

def draw_colored_graph(G, assignment, output_file, title):
    color_map = {1: "red", 2: "green", 3: "blue", 4: "yellow"}
    node_colors = [color_map.get(assignment.get(node, 0), "gray") for node in G.nodes()]
    
    try:
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
    except:
        pos = nx.spring_layout(G)
    
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=800, font_size=12)
    plt.title(f"Grafo Colorido ({title})")
    plt.savefig(output_file)
    plt.close()

def draw_search_tree(tree, output_file, title):
    color_map = {"1": "red", "2": "green", "3": "blue", "4": "yellow"}
    node_colors = []
    labels = nx.get_node_attributes(tree, 'label')
    
    # Processa cores e formata rótulos
    formatted_labels = {}
    for node in tree.nodes():
        label = labels.get(node, "")
        color = "lightgray"
        formatted_label = ""
        
        if "=" in label:
            # Extrai a parte da cor
            parts = label.split("=")
            vertex_part = parts[0]
            color_part = parts[1].split("\n")[0].strip() if "\n" in label else parts[1]
            color = color_map.get(color_part, "lightgray")
            
            # Formatação especial para nós de solução
            if "Solução" in label:
                formatted_label = label.replace("Solução: ", "").replace(", Custo Total", "\nCusto Total")
            else:
                formatted_label = f"{vertex_part}={color_part}"
                
            # Adiciona informações de custo se existirem
            if "\n" in label:
                cost_info = label.split("\n")[1]
                formatted_label += f"\n{cost_info}"
        
        elif "Início" in label:
            formatted_label = "Início"
        else:
            formatted_label = label
        
        formatted_labels[node] = formatted_label
        node_colors.append(color)

    # Cria layout hierárquico
    try:
        pos = nx.nx_agraph.graphviz_layout(tree, prog='dot', args="-Grankdir=TB -Gnodesep=0.5 -Granksep=1.0")
    except:
        pos = nx.drawing.nx_pydot.pydot_layout(tree, prog='dot')

    plt.figure(figsize=(14, 10))
    
    # Desenha apenas o texto diretamente nos nós
    nx.draw(tree, pos,
           with_labels=True,
           labels=formatted_labels,
           node_color=node_colors,
           node_size=3000,
           font_size=9,
           font_color="black",
           edge_color="gray",
           width=1.5,
           arrows=True,
           linewidths=0.5)  # Remove bordas dos nós

    plt.title(title)
    plt.savefig(output_file, bbox_inches='tight')
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Algoritmos de Coloração de Grafos")
    parser.add_argument("file_path", help="Caminho do arquivo de entrada")
    parser.add_argument("--algorithm", choices=["greedy", "ordered", "astar"], default="greedy",
                      help="Algoritmo a ser utilizado (padrão: greedy)")
    args = parser.parse_args()

    G = read_graph(args.file_path)
    vertices = sorted(G.nodes())
    root_id = add_tree_node("root")

    solution = None
    log_file = ""
    output_prefix = args.algorithm

    if args.algorithm == "astar":
        solution = astar_search(G, vertices, root_id, f"{output_prefix}_log.txt")
        draw_colored_graph(G, solution[0] if solution else {}, f"colored_graph_{output_prefix}.png", "Busca A*")
        draw_search_tree(search_tree, f"search_tree_{output_prefix}.png", "Árvore de Busca A* (g, h, f)")
    elif args.algorithm == "ordered":
        solution = ordered_search(G, vertices, root_id, f"{output_prefix}_log.txt")
        draw_colored_graph(G, solution[0] if solution else {}, f"colored_graph_{output_prefix}.png", "Busca Ordenada")
        draw_search_tree(search_tree, f"search_tree_{output_prefix}.png", "Árvore de Busca Ordenada")
    else:
        solution = greedy_search(G, vertices, root_id, f"{output_prefix}_log.txt")
        draw_colored_graph(G, solution[0] if solution else {}, f"colored_graph_{output_prefix}.png", "Busca Gulosa")
        draw_search_tree(search_tree, f"search_tree_{output_prefix}.png", "Árvore de Busca Gulosa")

    if solution:
        print(f"Solução encontrada: {solution[0]}\nCusto Total: {solution[-1]}")
    else:
        print("Nenhuma solução encontrada.")

if __name__ == '__main__':
    main()