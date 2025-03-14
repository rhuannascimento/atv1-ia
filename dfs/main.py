import networkx as nx
import matplotlib.pyplot as plt
import sys

search_tree = nx.DiGraph()
node_counter = 0

def add_tree_node(label, parent_node_id=None):
    """
    Adiciona um nó à árvore de busca com o rótulo 'label'. Se informado,
    cria uma aresta do nó 'parent_node_id' para o novo nó.
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
      <vértice1> <vértice2>
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
        if len(parts) >= 2:
            u = int(parts[0])
            v = int(parts[1])
            edges.append((u, v))
    
    G = nx.Graph()
    G.add_nodes_from(range(1, dimension + 1))
    G.add_edges_from(edges)
    return G

def is_valid(G, vertex, color, assignment):
    """
    Verifica se é válido colorir 'vertex' com 'color', isto é, nenhum vizinho já
    colorido possui a mesma cor.
    """
    for neighbor in G.neighbors(vertex):
        if neighbor in assignment and assignment[neighbor] == color:
            return False
    return True

def state_to_string_simple(state, vertices):
    """
    Converte o estado para uma string simples contendo o ID do nó e a cor
    atribuída no último vértice (ou 'sem cor' se nenhum vértice foi colorido).
    Cada estado é uma tupla: (assignment, index, tree_node_id)
    """
    assignment, index, tree_node_id = state
    if index > 0:
        last_vertex = vertices[index - 1]
        last_color = assignment[last_vertex]
        return f"ID {tree_node_id}: {last_vertex} = {last_color}"
    else:
        return f"ID {tree_node_id}: sem cor"

def dfs(G, vertices, root_id, log_filename="dfs_log.txt"):
    """
    Executa a busca em profundidade para encontrar uma coloração válida.
    Em cada iteração, grava (comentado, mas pode ser reativado) um log simples (em português)
    com a lista de estados abertos ("Abertos") e fechados ("Fechados").
    
    Cada estado é representado por (assignment, index, tree_node_id).
    """
    open_stack = []
    closed_states = []
    initial_state = ({}, 0, root_id)
    open_stack.append(initial_state)
    iteration = 0

    with open(log_filename, "w", encoding="utf-8") as log_file:
        while open_stack:
            log_file.write(f"Iteração {iteration}:\n")
            log_file.write("Abertos: " + ", ".join([state_to_string_simple(s, vertices) for s in open_stack]) + "\n")
            log_file.write("Fechados: " + ", ".join([state_to_string_simple(s, vertices) for s in closed_states]) + "\n\n")
            iteration += 1

            state = open_stack.pop()
            assignment, index, tree_node_id = state

            if index == len(vertices):
                sol_label = "Solução: " + str(assignment)
                add_tree_node(sol_label, tree_node_id)
                return assignment

            vertex = vertices[index]
            for color in [1, 2, 3, 4]:
                if is_valid(G, vertex, color, assignment):
                    new_assignment = assignment.copy()
                    new_assignment[vertex] = color
                    new_index = index + 1
                    new_label = f"{vertex} = {color}"
                    new_tree_node_id = add_tree_node(new_label, tree_node_id)
                    new_state = (new_assignment, new_index, new_tree_node_id)
                    open_stack.append(new_state)
            closed_states.append(state)
    return None

def draw_colored_graph(G, assignment, output_file="colored_graph_dfs.png"):
    """
    Desenha o grafo colorido usando o dicionário 'assignment' e salva a imagem.
    """
    color_map = {1: "red", 2: "green", 3: "blue", 4: "yellow"}
    node_colors = [color_map[assignment[node]] if node in assignment else "gray" for node in G.nodes()]
    
    try:
        pos = nx.nx_agraph.graphviz_layout(G, prog='dot', args='-Granksep=2 -Gnodesep=1')
    except Exception as e:
        pos = nx.spring_layout(G)

    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=800, font_size=12)
    plt.title("Grafo Colorido (DFS)")
    plt.savefig(output_file)
    plt.close()

def draw_search_tree(tree, output_file="search_tree_dfs.png"):
    """
    Desenha a árvore de busca com nós preenchidos com a cor correspondente.
    Tenta usar um layout hierárquico com Graphviz, aplicando espaçamentos personalizados;
    caso não seja possível, utiliza um layout padrão.
    """
    try:
        pos = nx.nx_agraph.graphviz_layout(tree, prog='dot', args='-Granksep=2 -Gnodesep=1')
    except Exception as e:
        pos = nx.spring_layout(tree)
    
    labels = nx.get_node_attributes(tree, 'label')
    mapping = {"1": "red", "2": "green", "3": "blue", "4": "yellow"}
    
    node_colors = []
    for n in tree.nodes():
        label = labels.get(n, "")
        fill_color = "lightgray"  
        if " = " in label:
            try:
                parts = label.split(" = ")
                candidate = parts[-1].strip()
                if candidate in mapping:
                    fill_color = mapping[candidate]
            except Exception as ex:
                fill_color = "lightgray"
        node_colors.append(fill_color)
    
    plt.figure(figsize=(16, 12))
    nx.draw(tree, pos, with_labels=True, labels=labels, node_color=node_colors,
            node_size=500, font_size=10, arrows=True)
    plt.title("Árvore de Busca (DFS) com nós coloridos")
    plt.savefig(output_file)
    plt.close()

def main():
    if len(sys.argv) < 2:
        sys.exit(1)
    
    file_path = sys.argv[1]
    G = read_graph(file_path)
    vertices = list(G.nodes())
    vertices.sort()
    
    root_id = add_tree_node("root")
    solution = dfs(G, vertices, root_id, log_filename="dfs_log.txt")
    
    if solution:
        print("Solução encontrada:", solution)
    else:
        print("Nenhuma solução encontrada.")
    
    draw_colored_graph(G, solution, output_file="colored_graph_dfs.png")
    print("Grafo colorido salvo em 'colored_graph_dfs.png'.")
    
    draw_search_tree(search_tree, output_file="search_tree_dfs.png")
    print("Árvore de busca salva em 'search_tree_dfs.png'.")
    print("Log de DFS salvo em 'dfs_log.txt'.")

if __name__ == '__main__':
    main()
