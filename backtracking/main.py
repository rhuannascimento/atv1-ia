import networkx as nx
import matplotlib.pyplot as plt

search_tree = nx.DiGraph()
node_counter = 0

def add_tree_node(label, parent_node_id=None):
    """
    Cria um novo nó na árvore de busca com o rótulo 'label' e, se informado,
    adiciona uma aresta do nó 'parent_node_id' para o novo nó.
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
    Espera o arquivo no seguinte formato:
      DIMENSION
      <número de vértices>
      GRAPH
      <u1> <v1>
      <u2> <v2>
      ...
    """
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    if lines[0].upper() != "DIMENSION":
        raise ValueError("Erro no formato do arquivo: Esperado 'DIMENSION' na primeira linha.")
    dimension = int(lines[1])
    
    if lines[2].upper() != "GRAPH":
        raise ValueError("Erro no formato do arquivo: Esperado 'GRAPH' após a dimensão.")
    
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
    Verifica se é válido colorir 'vertex' com 'color', ou seja, nenhum
    vizinho já colorido tem a mesma cor.
    """
    for neighbor in G.neighbors(vertex):
        if neighbor in assignment and assignment[neighbor] == color:
            return False
    return True

def backtrack(G, vertices, index, assignment, parent_node_id):
    """
    Função recursiva que implementa o algoritmo de backtracking.
    - G: grafo
    - vertices: lista ordenada de vértices
    - index: índice do vértice atual a ser colorido
    - assignment: dicionário com as cores atribuídas (ex: {1: 2, 2: 4, ...})
    - parent_node_id: nó da árvore de busca do qual este estado deriva
    A busca para ao encontrar a primeira solução válida.
    """
    if index == len(vertices):
        node_label = "Solução: " + str(assignment)
        add_tree_node(node_label, parent_node_id)
        return True, assignment

    vertex = vertices[index]
    for color in [1, 2, 3, 4]:
        if is_valid(G, vertex, color, assignment):
            assignment[vertex] = color
            node_label = f"{vertex} = {color}"
            new_node_id = add_tree_node(node_label, parent_node_id)
            found, sol = backtrack(G, vertices, index + 1, assignment, new_node_id)
            if found:
                return True, sol
            del assignment[vertex]
    return False, None

def draw_colored_graph(G, assignment, output_file="colored_graph.png"):
    """
    Desenha o grafo colorido usando o dicionário 'assignment' e salva a imagem.
    """
    color_map = {1: "red", 2: "green", 3: "blue", 4: "yellow"}
    node_colors = [color_map[assignment[node]] if node in assignment else "gray" for node in G.nodes()]
    pos = nx.spring_layout(G)
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=800, font_size=12)
    plt.title("Grafo Colorido")
    plt.savefig(output_file)
    plt.close()

def draw_search_tree(tree, output_file="search_tree_bfs.png"):
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
    plt.title("Árvore de Busca (BFS) com nós coloridos")
    plt.savefig(output_file)
    plt.close()


def main():
    import sys
    if len(sys.argv) < 2:
        print("Uso: python script.py <arquivo_grafo>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    G = read_graph(file_path)
    vertices = list(G.nodes())
    vertices.sort() 
    root_id = add_tree_node("root")
    found, solution = backtrack(G, vertices, 0, {}, root_id)
    if found:
        print("Solução encontrada:", solution)
    else:
        print("Nenhuma solução encontrada.")
    
    draw_colored_graph(G, solution)
    print("Grafo colorido salvo em 'colored_graph.png'.")
    draw_search_tree(search_tree)
    print("Árvore de busca salva em 'search_tree.png'.")

if __name__ == '__main__':
    main()
