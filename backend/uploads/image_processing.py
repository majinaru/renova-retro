import cv2 as cv
import networkx as nx
import numpy as np
from scipy.spatial import Voronoi, voronoi_plot_2d
import matplotlib.pyplot as plt
import sys
import os


# Recebe o caminho da imagem como argumento
if len(sys.argv) > 1:
    image_path = sys.argv[1]
    print(f"Path to the image provided: {image_path}")
else:
    print("No image path provided.")
    sys.exit(1)

# Verifica se o arquivo existe
if not os.path.isfile(image_path):
    print(f"File does not exist: {image_path}")
    sys.exit(1)

# Tentativa de carregar a imagem
img = cv.imread(image_path)
if img is None:
    print(f"Failed to load image: {image_path}")
    sys.exit(1)
else:
    print(f"Image loaded successfully: {image_path}")

# Exibir as dimensões da imagem
height, width, channels = img.shape
print(f"Image dimensions: {width}x{height}, Channels: {channels}")
img_RGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)

def ret_graph(img_RGB):
    G = nx.Graph()

    row,col,_ = img_RGB.shape

    for i in range(row):
        for j in range(col):
            G.add_node((i,j), color = img_RGB[i,j])
            # adiciona arestas entre um no e todo os seus vizinhos 
            if i > 0:
                G.add_edge((i-1,j), (i,j)) 
                if j > 0:
                    G.add_edge((i-1,j-1), (i,j))  
                if j < col-1:
                    G.add_edge((i-1,j+1), (i,j))  
            if i < row-1:
                G.add_edge((i+1,j), (i,j))  
                if j > 0:
                    G.add_edge((i+1,j-1), (i,j)) 
                if j < col-1:
                    G.add_edge((i+1,j+1), (i,j))  
            if j > 0:
                G.add_edge((i,j-1), (i,j)) 
            if j < col-1:
                G.add_edge((i,j+1), (i,j))  

    plt.figure()
    pos = {(i,j):(j,-i) for i,j in G.nodes()}
    nx.draw(G, pos=pos, node_size=25, node_color= 'blue' , with_labels=False, edge_color='red')

    for node in G.nodes():
        i, j = node
        if  i >= 0 and j >= 0 and i < row and j < col:
            neigh = [n for n in G.neighbors(node)]
            
            for n in neigh:
                ni, nj = n
                # Se a diferenÃ§a for maior que o limite em qualquer canal, remova a aresta
                if (img_RGB[i,j][0] != img_RGB[ni,nj][0]) and (img_RGB[i,j][1] != img_RGB[ni,nj][1]) and (img_RGB[i,j][2] != img_RGB[ni,nj][2]):
                    G.remove_edge(node, n)

    return G

def remove_edges(G, img):
    row,col,_ = img.shape
    for node in G.nodes():
        i,j = node

        if i >= 0 and j >= 0 and i < row and j < col:

            if G.has_edge((i,j), (i,j+1)) and G.has_edge((i, j), (i+1,j)) and G.has_edge((i,j+1),(i+1,j+1)) and G.has_edge((i+1,j),(i+1,j+1)):
                if G.has_edge((i,j), (i+1,j+1)):
                    G.remove_edge((i,j), (i+1,j+1)) 
                if G.has_edge((i,j+1), (i+1,j)):
                    G.remove_edge((i,j+1), (i+1,j))

    return G

def divide_edges(G):
    new_edges = []  # Lista para armazenar as novas arestas
    for edge in G.edges():
        node1, node2 = edge
        x1, y1 = node1
        x2, y2 = node2
        # Calcular o ponto médio da aresta
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        mid_point = (mid_x, mid_y)
        # Adicionar as novas arestas conectando o ponto médio aos nós correspondentes
        new_edges.append((node1, mid_point))
        new_edges.append((mid_point, node2))
    # Remover as arestas originais
    G.remove_edges_from(G.edges())
    # Adicionar as novas arestas ao grafo
    G.add_edges_from(new_edges)
    return G

def find_nearest_pixel(vertex, img_shape):
    # Encontrar o pixel mais próximo ao vértice do diagrama de Voronoi
    i = int(round(-vertex[1]))
    j = int(round(vertex[0]))
    i = max(min(i, img_shape[0] - 1), 0)  # Garantir que o índice i esteja dentro dos limites da imagem
    j = max(min(j, img_shape[1] - 1), 0)  # Garantir que o índice j esteja dentro dos limites da imagem
    return i, j

def calculate_voronoi_cells(G_divided, img_shape):
    voronoi_cells = {}  # Dicionário para armazenar as células de Voronoi para cada nó
    
    # Converter os nós do grafo em pontos para o cálculo do diagrama de Voronoi
    points = [(j, -i) for i, j in G_divided.nodes()]
    
    # Calcular o diagrama de Voronoi
    vor = Voronoi(points)
    
    # Para cada vértice no diagrama de Voronoi, encontrar os pixels mais próximos e atribuí-los à célula correspondente
    for region_index, region_vertices in enumerate(vor.regions):
        if region_index < len(vor.points):  # Verificar se o índice está dentro dos limites dos pontos de Voronoi
            if -1 not in region_vertices:  # Ignorar regiões sem vértices (não são células válidas)
                node = tuple(vor.points[region_index])  # Converter para tupla
                node_cell = []
                for vertex_index in region_vertices:
                    vertex = vor.vertices[vertex_index]
                    # Encontrar os pixels mais próximos ao vértice do diagrama de Voronoi
                    nearest_pixel = find_nearest_pixel(vertex, img_shape)
                    node_cell.append(nearest_pixel)
                voronoi_cells[node] = node_cell
    
    return voronoi_cells

def collapse_valence_2_nodes(G, voronoi_cells):
    # Criar uma cópia do grafo para iterar enquanto modificamos o original
    G_copy = G.copy()
    
    # Percorrer todos os nós do grafo
    for node in list(G.nodes()):
        neighbors = list(G.neighbors(node))
        
        # Se o nó tiver exatamente dois vizinhos
        if len(neighbors) == 2:
            # Obter os vizinhos
            neighbor1, neighbor2 = neighbors
            
            # Verificar se os vizinhos estão na mesma célula de Voronoi
            node_cell = voronoi_cells.get(node)
            neighbor1_cell = voronoi_cells.get(neighbor1)
            neighbor2_cell = voronoi_cells.get(neighbor2)
            
            if node_cell == neighbor1_cell == neighbor2_cell:
                # Remover o nó do grafo
                G_copy.remove_node(node)
                
                # Conectar diretamente os vizinhos
                if not G_copy.has_edge(neighbor1, neighbor2):
                    G_copy.add_edge(neighbor1, neighbor2)
    
    return G_copy

def generate_voronoi_image(img_RGB, output_file):
    G = ret_graph(img_RGB)
    G2 = remove_edges(G, img_RGB)
    G_divided = divide_edges(G2)
    voronoi_cells = calculate_voronoi_cells(G_divided, img_RGB.shape)
    G_simplified = collapse_valence_2_nodes(G_divided, voronoi_cells)

    # Gera a imagem do diagrama de Voronoi
    fig, ax = plt.subplots(figsize=(8, 8))
    voronoi_plot_2d(Voronoi(np.array([(j, -i) for i, j in G_divided.nodes()])), ax=ax, show_vertices=False, line_colors='red')
    for node, cell in voronoi_cells.items():
        ax.fill(*zip(*cell), alpha=0.2)
    ax.set_title('Generalized Voronoi Cells')
    plt.savefig(output_file)
    plt.close()

# Chama a função para gerar a imagem
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, 'voronoi_diagram.png')
generate_voronoi_image(img_RGB, output_file)
