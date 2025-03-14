import networkx as nx
import matplotlib.pyplot as plt
import sys

# Árvore de busca para visualização
search_tree = nx.DiGraph()
node_counter = 0

def add_tree_node(label, parent_node_id=None):
    """
    Adiciona um nó à árvore de busca com o rótulo 'label'.
    Se 'parent_node_id' for informado, cria uma aresta do pai para o novo nó.
    Retorna o ID do nó criado.
    """
    global node_counter
    node_id = node_counter
    node_counter += 1
    search_tree.add_node(node_id, label=label)
    if parent_node_id is not None:
        search_tree.add_edge(parent_node_id, node_id)
    return node_id

def read_graph(file_path):
    """
    Lê o arquivo e cria o grafo.
    Formato esperado:
      DIMENSION 
      <número de vértices>
      GRAPH
      <vértice1> <vértice2> <custo>
      ...
    """
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
    
    # Cria um grafo não direcionado
    G = nx.Graph()
    G.add_nodes_from(range(1, dimension + 1))
    G.add_weighted_edges_from(edges)
    return G

def is_valid(G, vertex, color, assignment):
    """
    Verifica se é válido colorir 'vertex' com 'color',
    isto é, nenhum vizinho já colorido possui a mesma cor.
    """
    for neighbor in G.neighbors(vertex):
        if neighbor in assignment and assignment[neighbor] == color:
            return False
    return True

def cost_for_vertex(G, vertex, assignment):
    """
    Calcula o custo de colorir 'vertex' dado que alguns vizinhos já foram coloridos.
    O custo é a soma dos pesos das arestas que ligam 'vertex' a cada vizinho já colorido.
    """
    custo = 0
    for neighbor in G.neighbors(vertex):
        if neighbor in assignment:
            custo += G[vertex][neighbor]["weight"]
    return custo

def state_to_string(state):
    """
    Converte um estado (vertex, color, cost_adicional) em string para log.
    """
    vertex, color, cost = state
    return f"(v={vertex}, cor={color}, custo_add={cost})"

def greedy_search(G, vertices, root_id, log_filename="greedy_log.txt"):
    """
    Executa a busca gulosa para encontrar uma coloração válida.
    Em cada passo, gera-se uma lista de 'abertos' (todas as cores válidas para o vértice),
    escolhe-se aquela com menor custo adicional e move-se para 'fechados'.
    
    Cada estado aqui é representado como (vertex, color, custo_adicional).
    """
    assignment = {}
    current_cost = 0
    current_tree_node_id = root_id
    
    with open(log_filename, "w", encoding="utf-8") as log_file:
        for index, vertex in enumerate(vertices):
            log_file.write(f"\n=== Iteração para vértice {vertex} ===\n")
            
            # Lista de estados abertos: (vertex, color, custo_adicional)
            abertos = []
            
            # Gera todas as cores válidas para este vértice
            for color in [1, 2, 3, 4]:
                if is_valid(G, vertex, color, assignment):
                    # Cria um "estado" para log
                    new_assignment = assignment.copy()
                    new_assignment[vertex] = color
                    additional_cost = cost_for_vertex(G, vertex, new_assignment)
                    abertos.append((vertex, color, additional_cost))
            
            # Log dos abertos
            if abertos:
                log_file.write("Abertos: " + ", ".join(state_to_string(s) for s in abertos) + "\n")
            else:
                log_file.write("Abertos: (nenhum estado válido)\n")
                log_file.write(f"Falha ao colorir o vértice {vertex}. Sem cores válidas.\n")
                return None
            
            # Escolhe a cor com menor custo adicional (abordagem gulosa)
            chosen_state = min(abertos, key=lambda x: x[2])  # x[2] é o custo_add
            (chosen_vertex, chosen_color, chosen_add_cost) = chosen_state
            
            # Lista de fechados (neste caso, só o estado escolhido)
            fechados = [chosen_state]
            log_file.write("Fechados (escolhido): " + ", ".join(state_to_string(s) for s in fechados) + "\n")
            
            # Aplica a cor escolhida
            assignment[chosen_vertex] = chosen_color
            current_cost += chosen_add_cost
            
            # Atualiza a árvore de busca
            new_label = f"{chosen_vertex}={chosen_color}"
            current_tree_node_id = add_tree_node(new_label, current_tree_node_id)
            
            log_file.write(f"Cor escolhida para vértice {vertex} = {chosen_color}, custo adicional = {chosen_add_cost}\n")
            log_file.write(f"Custo acumulado até agora: {current_cost}\n")
    
    # Ao final, criamos um nó na árvore com a solução
    sol_label = f"Solução: {assignment}, Custo Total: {current_cost}"
    add_tree_node(sol_label, current_tree_node_id)
    
    return (assignment, len(vertices), current_tree_node_id, current_cost)

def draw_colored_graph(G, assignment, output_file="colored_graph_greedy.png"):
    """
    Desenha o grafo colorido de acordo com o dicionário 'assignment'.
    As cores são: 1->red, 2->green, 3->blue, 4->yellow.
    """
    color_map = {1: "red", 2: "green", 3: "blue", 4: "yellow"}
    node_colors = []
    for node in G.nodes():
        if node in assignment:
            node_colors.append(color_map.get(assignment[node], "gray"))
        else:
            node_colors.append("gray")
    try:
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot', args='-Granksep=2 -Gnodesep=1')
    except Exception:
        pos = nx.spring_layout(G)
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=800, font_size=12)
    plt.title("Grafo Colorido (Busca Gulosa)")
    plt.savefig(output_file)
    plt.close()

def draw_search_tree(tree, output_file="search_tree_greedy.png"):
    """
    Desenha a árvore de busca com os nós coloridos.
    Cada nó da árvore apresenta o rótulo no formato "v=c" (ex.: "3=blue") quando possível.
    """
    try:
        pos = nx.nx_agraph.graphviz_layout(tree, prog='dot', args='-Granksep=2 -Gnodesep=1')
    except Exception:
        pos = nx.spring_layout(tree)
    
    labels = nx.get_node_attributes(tree, 'label')
    color_map = {"1": "red", "2": "green", "3": "blue", "4": "yellow"}
    node_colors = []
    for n in tree.nodes():
        label = labels.get(n, "")
        if "=" in label:
            parts = label.split("=")
            if len(parts) == 2:
                c = parts[1].strip()
                node_colors.append(color_map.get(c, "lightgray"))
            else:
                node_colors.append("lightgray")
        else:
            node_colors.append("lightgray")
    
    plt.figure(figsize=(16, 12))
    nx.draw(tree, pos, with_labels=True, labels=labels, node_color=node_colors,
            node_size=500, font_size=10, arrows=True)
    plt.title("Árvore de Busca Gulosa (Colorida)")
    plt.savefig(output_file)
    plt.close()

def main():
    if len(sys.argv) < 2:
        sys.exit("Uso: python main.py <arquivo_grafo>")
    
    file_path = sys.argv[1]
    G = read_graph(file_path)
    vertices = list(G.nodes())
    vertices.sort()  # Ordena os vértices (por exemplo, 1, 2, 3, ...)
    
    root_id = add_tree_node("root")
    solution = greedy_search(G, vertices, root_id, log_filename="greedy_log.txt")
    
    if solution:
        assignment, index, tree_node_id, total_cost = solution
        print("Solução encontrada:", assignment, "Custo Total:", total_cost)
        draw_colored_graph(G, assignment, output_file="colored_graph_greedy.png")
        print("Grafo colorido salvo em 'colored_graph_greedy.png'.")
    else:
        print("Nenhuma solução encontrada.")
    
    draw_search_tree(search_tree, output_file="search_tree_greedy.png")
    print("Árvore de busca salva em 'search_tree_greedy.png'.")
    print("Log de Busca Gulosa salvo em 'greedy_log.txt'.")

if __name__ == '__main__':
    main()
