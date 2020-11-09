import os
import glob
import itertools
from math import factorial
from read_db import *
from wordcloud import WordCloud
import networkx as nx


def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr)//2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)


def find_neighbor(edges, node):
    result = []
    for edge in edges:
        if node == edge[0]:
            result.append(edge[1])
        if node == edge[1]:
            result.append(edge[0])
    return result

# def count_edge_butterfly(L,G):


def count_edge_butterfly(L, G):
    butterflies_edges = {}

    # initialise
    for e in G.edges:
        butterflies_edges[e] = 0

    for u in L:
        neighbor = [n for n in G.neighbors(u)]
        for pair in itertools.combinations(neighbor, 2):
            v1 = pair[0]
            v2 = pair[1]
            v1_neighbor = [n for n in G.neighbors(v1) if n > u]
            v2_neighbor = [n for n in G.neighbors(v2) if n > u]
            # intersection
            I = list(set(v1_neighbor) & set(v2_neighbor))
            for i in I:
                edges = [(u, v1), (u, v2), (i, v1), (i, v2)]

                for e in edges:
                    # if e not in butterflies_edges.keys():

                        #     print(neighbor)
                    butterflies_edges[e] += 1
                    # elif (e[1],e[0]) in butterflies_edges.keys() :
                    # else:
                    # butterflies_edges[(e[1],e[0])] += 1

    return butterflies_edges

# def adj_butterflies_by_edge(G,edge,return_value = "edge"):


def adj_butterflies_by_edge(G, edge, return_value="edge"):
    edges = []
    u1 = edge[0]
    u2 = edge[1]
    neighbor = [n for n in G.neighbors(u1)]
    neighbor.remove(u2)
    btf = []
    # for pair in itertools.combinations(neighbor,2):
    v2_neighbor = [n for n in G.neighbors(u2)]
    for v in neighbor:
        v1_neighbor = [n for n in G.neighbors(v)]

        I = list(set(v1_neighbor) & set(v2_neighbor))
        I.remove(u1)
        for i in I:
            edges += [(u1, v), (u1, u2), (i, v), (i, u2)]
            if return_value == "butterfly":
                btf.append([(u1, v), (u1, u2), (i, v), (i, u2)])

    if return_value == "butterfly":
        return btf

    edges = list(set(edges))
    return edges

    edges = list(set(edges))
    return edges


def wing_decomposition(L, R, graph_edges):
    # edges = graph_edges.copy()
    # L = quicksort(L)
    # G = Graph.copy()

    G = nx.Graph()
    G.add_nodes_from(L, bipartite=0)
    G.add_nodes_from(R, bipartite=1)
    G.add_edges_from(graph_edges)

    butterflies_edges = count_edge_butterfly(L, G)
    # print("buf edge",butterflies_edges)

    wing_number = {}

    min_buf_value = min(butterflies_edges.values())
    min_buf = [k for k, v in butterflies_edges.items() if v == min_buf_value]

    # print(
    #     "start: min buf",min_buf
    # )

    while len(min_buf) != 0:
        # print(min_buf)
        for e in min_buf:
            wing_number[e] = butterflies_edges[e]

            bufs = adj_butterflies_by_edge(G, e, "butterfly")

            for b in bufs:
                for f in b:
                    if f == e:
                        continue
                    if butterflies_edges[f] > butterflies_edges[e]:
                        butterflies_edges[f] += -1

            butterflies_edges.pop(e)

            G.remove_edge(e[0], e[1])

        if len(butterflies_edges) == 0:
            break

        min_buf_value = min(butterflies_edges.values())
        min_buf = [k for k, v in butterflies_edges.items() if v ==
                   min_buf_value]
    max_wingnumber = max(wing_number.values())

    hierarchy = {}

    for node in (L+R):
        hierarchy[node] = 0

    # print(wing_number)
    for key, value in wing_number.items():
        # Graph[key[0]][key[1]]['wing'] = value
        # for i in range(value+1):
            # hierarchy[i]['L'].add(key[0])

            # hierarchy[i]['R'].add(key[1])
        if value > hierarchy[key[0]]:
            hierarchy[key[0]] = value
        if value > hierarchy[key[1]]:
            hierarchy[key[1]] = value
    return max_wingnumber, hierarchy, wing_number


# def count_butterfly(nodes,edges):
#     # initilize node wedge
#     nodes_length = len(nodes)
#     node_degree = {}

#     for i in range(nodes_length):
#         node_degree[i] = []


#     initial_wedge = {}

#     for node in nodes:
#         # degree = len([n for n in G.neighbors(node)])
#         degree = len(find_neighbor(edges,node))
#         node_degree[degree].append(node)
#         initial_wedge[node] = 0

#     node_index = []

#     # compute priority
#     p = {}
#     index = 1
#     for i in range(nodes_length):
#         if node_degree[i] == []:
#             continue
#         sort = quicksort(node_degree[i])[::-1]
#         for c in sort:
#             p[c] = index
#             index += 1


#     bf_count = 0
#     for u in nodes:
#         count_wedge = initial_wedge.copy()
#         #initialise count wedge


#         # for v in G.neighbors(u):
#         for v in find_neighbor(edges,u):
#             if p[v] < p[u]:
#                 # for w in G.neighbors(v):
#                 for w in find_neighbor(edges,v):
#                     if p[w] < p[u]:
#                         count_wedge[w] += 1

#         for key,value in count_wedge.items():
#             if value > 1:
#                 bf_count += factorial(value)/(factorial(value-2)*2)

#     # print(bf_count)
#     return (int)(bf_count)
    # return 4*bf_count/count_caterpillars()

# return all nodes, connected graph
# def breadth_first_search(nodes, edges, source):

#     queue = []
#     queue.append(source)

#     visited = {}
#     for i in nodes:
#         visited[i] = False
#     visited[source] = True

#     result = []

#     while queue:
#         s = queue.pop(0)
#         result.append(s)

#         for i in find_neighbor(edges, s):
#             if visited[i] == False:
#                 queue.append(i)
#                 visited[i] = True
#     return result


def generate_word_cloud(text):
    # text += '''Meltdown Spectre Attacks Exploiting Speculative Execution deijse jiwoafhawi dhuihawiufh dhsuaidh dwa'''
    word_cloud = WordCloud(max_font_size=30).generate(text)

    word_list = []
    freq_list = []
    fontsize_list = []
    position_list = []
    orientation_list = []
    color_list = []

    for (word, freq), fontsize, position, orientation, color in word_cloud.layout_:
        word_list.append(word)
        freq_list.append(freq)
        fontsize_list.append(fontsize)
        position_list.append(position)
        orientation_list.append(orientation)
        color_list.append(color)

    # get the positions
    x_arr = []
    y_arr = []
    for i in position_list:
        x_arr.append(i[1])
        y_arr.append(i[0])

    y_max = max(y_arr) + 40
    # get the relative occurence frequencies
    new_freq_list = []
    for i in freq_list:
        new_freq_list.append(i * 80)

    trace = go.Scatter(
        x=x_arr,
        y=y_arr,
        textfont=dict(size=new_freq_list, color='white'),
        hoverinfo="text",
        textposition="top center",
        # hovertext=["{0} - {1}".format(w, f) for w, f in zip(word_list, freq_list)],
        hovertext=[],
        mode="text",
        text=[],
    )

    text_annotation = []
    for i in range(len(x_arr)):
        angle = 0
        if orientation_list[i] == 2:
            # angle = 90

            text_layout = dict(
                # x = x_arr[i]/x_scale,
                # y = y_arr[i]/y_scale,
                x=x_arr[i],
                y=y_arr[i],
                # xref = 'paper',
                xref='x',
                yref='y',
                # yref = 'paper',
                text=word_list[i],
                font=dict(
                    color=color_list[i],
                    size=fontsize_list[i],
                ),
                showarrow=False,
                # xanchor= "center",
                xanchor="right",
                yanchor="top",
                # yanchor = "bottom",
                textangle=-90,
                # yanchor= "middle",

            )

        else:

            text_layout = dict(
                # x = x_arr[i]/x_scale,
                # y = y_arr[i]/y_scale,
                x=x_arr[i],
                y=y_arr[i],
                # xref = 'paper',
                xref='x',
                yref='y',
                # yref = 'paper',
                text=word_list[i],
                font=dict(
                    color=color_list[i],
                    size=fontsize_list[i],
                ),
                showarrow=False,
                # xanchor= "center",
                xanchor="left",
                yanchor="top",
                textangle=0,
                # yanchor= "middle",

            )
        text_annotation.append(text_layout)

    layout = go.Layout(
        {
            "xaxis": {
                "showgrid": False,
                "showticklabels": False,
                "zeroline": False,
                # "automargin": True,
                # "range": [200,0],
            },
            "yaxis": {
                "showgrid": False,
                "showticklabels": False,
                "zeroline": False,
                # "automargin": True,
                "range": [y_max, 0],
            },
            "margin": dict(t=20, b=20, l=10, r=10, pad=4),
            "hovermode": "closest",
            "annotations": text_annotation,
        }
    )

    wordcloud_figure_data = {"data": [trace], "layout": layout}
    # wordcloud_figure_data = {"data": [], "layout": layout}
    return wordcloud_figure_data


def delete_files():
    files = glob.glob('./read_file/*')
    for f in files:
        os.remove(f)
