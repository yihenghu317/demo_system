from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, insert
from xml.dom import minidom
import lxml.etree as ET
import pandas as pd
from itertools import chain
import plotly.graph_objs as go
from read_db import *
from new_functions import *
import os
import base64
import random
import numpy as np
from alpha_beta_core import *


def colors(n):

    ret = [
        # '#83ae9b',
        # '#cbcba9',
        # '#f9cdae',
        # '#f69a9a',
        # '#ef4566',
        # '#7d87c9',
        # '#b39ee6',
        # '#f5b1f5',
        # '#fbe5f5',
        # '#4957b8',
        # '#93b1c3',
        # '#bf7cab',
        # '#9c96c5',
        # '#c998a7',
        # '#7986c7',
        # '#AD441C',
        # '#6AC641',
        # '#9D7921',
        # '#016C62',
        # '#F8EDFF',
        # '#4d5abd',
        # '#8DC599',
        # '#1FF3D9',
        # '#E00E9B',
        # '#24EC7A',
    ]

    if n > len(ret):
        rest_len = n - len(ret)
        rest = []
        while rest_len >= 0:
            new_c = "#"+''.join([random.choice('0123456789ABCDEF')
                                 for j in range(6)])
            if new_c in ret:
                continue
            rest.append(new_c)
            rest_len += -1
        ret += rest

    return ret


def add_icon_helper(L_node, R_node, x1_pos, x2_pos, limg, rimg, l_node_name, r_node_name,):
    images = []
    nl = len(L_node)
    nr = len(R_node)

    def k(a, m, b, n):
        return (m-n)/(a-b)

    def intercept(a, m, b, n):
        return (a*n-m*b)/(a-b)

    # xc = (-0.7*nl+24.4)/23
    x1 = 25
    y1 = 0.28

    x2 = 2
    y2 = 1

    rc = k(x1, y1, x2, y2)*nr + intercept(x1, y1, x2, y2)

    if rc < 0.3:
        rc = 0.3

    rsize = 0.11*rc

    for i in range((int)(nr)):
        y_pos = 0
        if nr > 1:
            y_pos = i*1/(float)(nr-1)

        images.append(
            dict(
                source=rimg,
                xref="x",
                yref="y",
                # x = x2_pos,
                # y = i*0.85/(float)(nr-1) + 0.14,
                x=2.03,
                y=y_pos,
                sizex=rsize,
                sizey=rsize,
                # xanchor= "left",
                # yanchor= "top"
                xanchor="center",
                # yanchor= "top"
                yanchor="middle",
            )
        )

    xc = k(x1, y1, x2, y2)*nl + intercept(x1, y1, x2, y2)

    if xc < 0.3:
        xc = 0.3

    lsize = xc*0.13
    for i in range((int)(nl)):
        y_pos = 0
        if nl > 1:
            y_pos = i*1/(float)(nl-1)
        images.append(

            dict(
                source=limg,
                xref='x',
                yref='y',
                x=0.98,
                y=y_pos,
                sizex=lsize,
                sizey=lsize,
                xanchor="center",
                yanchor="middle",
            )
        )
    return images, add_text(L_node, lsize, l_node_name)


def add_text(L_nodes, lsize, node_text, x1_pos=0.01,):
    texts = []
    nl = len(L_nodes)

    def k(a, m, b, n):
        return (m-n)/(a-b)

    def intercept(a, m, b, n):
        return (a*n-m*b)/(a-b)

    # xc = (-0.7*nl+24.4)/23
    x1 = 25
    y1 = 0.28

    x2 = 2
    y2 = 1
    xc = k(x1, y1, x2, y2)*nl + intercept(x1, y1, x2, y2)

    if xc < 0.5:
        xc = 0.5

    for i in range(len(L_nodes)):
        y_pos = -lsize/2
        if nl > 1:
            y_pos = i*1/(float)(nl-1)-lsize/2
        texts.append(
            dict(
                # source= limg,
                xref="x",
                yref="y",
                # x1= 0.01,
                x=0.98,
                # y= 0.13+ (i/(float)(nl)),
                # y = i/(float)(nl) - 0.06,
                # y = i*0.873/(float)(nl-1) + 0.14 - 0.1,
                y=y_pos,
                # text = str(L_nodes[i]),
                text=node_text[L_nodes[i]],
                font={"size": 12*xc},
                showarrow=False,
                xanchor="center",
                yanchor="middle",
            )
        )
    return texts


def add_icon_node(L_node, R_node, l_node_name, r_node_name, compare=False):
    nl = len(L_node)
    nr = len(R_node)
    with open(os.getcwd() + "/assets/icon_doc_fill.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    # Add the prefix that plotly will want when using the string as source
    rencoded_image = "data:image/png;base64," + encoded_string

    with open(os.getcwd() + "/assets/bussiness-man.jpg", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    # Add the prefix that plotly will want when using the string as source
    lencoded_image = "data:image/png;base64," + encoded_string

    with open(os.getcwd() + "/assets/1.png", "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    # Add the prefix that plotly will want when using the string as source
    m_image = "data:image/png;base64," + encoded_string

    images = []
    size = 500

    if compare:
        images += add_icon_helper(nr[0], nl[0], 0.01,
                                  0.43, lencoded_image, rencoded_image)
        images += add_icon_helper(nr[1], nl[1], 0.50,
                                  0.94, lencoded_image, rencoded_image)
    else:
        images += add_icon_helper(L_node, R_node, 0.01,
                                  0.93, lencoded_image, rencoded_image, l_node_name, r_node_name, )

    return images


def construct_graph_db(L_nodes, R_nodes, edges, meta, engine, color_list=None,  x1_pos=1, x2_pos=2, icon=True):
    # L_nodes = get_node(meta,engine,0)
    # R_nodes = get_node(meta,engine,1)

    # pos = {[node, (x1_pos,index*l_scale)] for index, node in enumerate(L_nodes)}

    # preprocess the order
    wing_left = {}
    wing_right = {}

    wing_no = get_edge_wingno(meta, engine)
    for edge in edges:
        wn = wing_no[(edge[0], edge[1])]
        if edge[0] not in wing_left.keys():
            wing_left[edge[0]] = wn
        else:
            if wn > wing_left[edge[0]]:
                wing_left[edge[0]] = wn

        if edge[1] not in wing_right.keys():
            wing_right[edge[1]] = wn
        else:
            if wn > wing_right[edge[1]]:
                wing_right[edge[1]] = wn


    # sort wing_left and wing_right
    wing_left = list(
        dict(sorted(wing_left.items(), key=lambda kv: kv[1])).keys())
    wing_right = list(
        dict(sorted(wing_right.items(), key=lambda kv: kv[1])).keys())
    # wing_right = list(wing_right.keys())
    length = (float)(max(len(wing_left), len(wing_right)))

    l_scale = 0
    r_scale = 0
    if len(wing_left) > 1:

        l_scale = 1/(float)(len(wing_left)-1)

    if len(wing_right) > 1:
        r_scale = 1/(float)(len(wing_right)-1)

    pos_left = {}
    pos_right = {}
    for index, node in enumerate(wing_left):
        pos_left[node] = (x1_pos, index*l_scale)

    for index, node in enumerate(wing_right):
        pos_right[node] = (x2_pos, index*r_scale)

    if color_list is None:
        color_list = colors(max(wing_no.values())+1)

    dot_color = 'white'
    if not icon:
        dot_color = 'black'

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker={
            'colorscale': 'Jet',
            'color': dot_color,
            'size': 10,
        },
        # textposition="bottom center",
    )

    edge_trace = []

    cw = 0
    lines = []
    max_wing = max(wing_no.values())

    trace_list_x = {}
    trace_list_y = {}
    for i in range(max_wing+1):
        trace_list_x[i] = []
        trace_list_y[i] = []

    for edge in edges:
        x0, y0 = pos_left[edge[0]]
        x1, y1 = pos_right[edge[1]]
        # trace_list_x += [x0, x1, None]
        # trace_list_y += [y0, y1, None]
        wn = wing_no[(edge[0], edge[1])]

        trace_list_x[wn] += [x0, x1, None]
        trace_list_y[wn] += [y0, y1, None]

    for i in range(max_wing+1):
        if len(trace_list_x[i]) == 0:
            continue
        new_edge_trace = go.Scatter(
            x=trace_list_x[i],
            y=trace_list_y[i],
            line={'width': 0.7, 'color': color_list[i]},
            hoverinfo='none',
            mode='lines',
        )
        edge_trace.append(new_edge_trace)

    node_trace_x = []
    node_trace_y = []
    node_text = []

    i = 0

    # node_name = get_node_list_name(L_nodes+R_nodes, meta, engine)
    l_node_name = get_left_node_list_name(wing_left, meta, engine)
    r_node_name = get_right_node_list_name(wing_right, meta, engine)

    # for node in (L_nodes+R_nodes):
    #     x, y = pos[node]
    #     node_trace_x.append(x)
    #     node_trace_y.append(y)
    #     node_text.append(node_name[node])
    #     i += 1

    # for node in L_nodes:
    for node in wing_left:
        x, y = pos_left[node]
        node_trace_x.append(x)
        node_trace_y.append(y)
        node_text.append(l_node_name[node])
        i += 1

    for node in wing_right:
        # for node in R_nodes:
        x, y = pos_right[node]
        node_trace_x.append(x)
        node_trace_y.append(y)
        node_text.append(r_node_name[node])
        i += 1


    node_trace['x'] = node_trace_x
    node_trace['y'] = node_trace_y
    node_trace['text'] = node_text

    aimage, atext = add_icon_node(
        wing_left, wing_right, l_node_name, r_node_name)

    if not icon:
        aimage = []
    data = {
        "data":   edge_trace + [node_trace],
        "layout": go.Layout(
            images=aimage,
            showlegend=False,
            hovermode='closest',
            margin={'b': 20, 'l': 10, 'r': 20, 't': 40, },
            xaxis={'showgrid': False,
                   'zeroline': False, 'showticklabels': False},
            yaxis={'showgrid': False,
                   'zeroline': False, 'showticklabels': False},

            # annotations=add_text(L_nodes),
            annotations=atext,

        )
    }
    # return {'data': data, 'left': L_nodes, 'right': R_nodes, 'edges': edges, }
    return data


# def construct_base_graph(meta, engine):
#     l_node = get_node(meta, engine, 0)
#     r_node = get_node(meta, engine, 1)
#     edges = get_edges(meta, engine)
#     return construct_graph_db(l_node, r_node, edges, meta, engine)

# return left node and right node

def compress_graph(edges):
    left = set([i[0] for i in edges])
    right = set([i[1] for i in edges])
    return list(left), list(right)


def wing_node_select(input_data):
    meta = input_data['meta']
    engine = input_data['engine']
    node = input_data['node']  # node value
    wing_number = input_data['wing_number']
    # l_node = get_left_node(meta, engine)
    # r_node = get_right_node(meta, engine)
    alpha = input_data['alpha']
    beta = input_data['beta']
    model = input_data['model']

    no_node = False
    if node is not None and node != "":
        # node = get_id(meta, engine, node)
        node, ninl = get_id_by_name(meta, engine, node)
        if node is None:
            return None
    else:
        no_node = True

    if model == 1:
        wing_subgraph_left_node, wing_subgraph_right_node = select_wing_number(
            meta, engine, wing_number)

        wing_subgraph_edges, wing_subgraph_left_node, wing_subgraph_right_node = get_subgraph_db(
            wing_subgraph_left_node, wing_subgraph_right_node, meta, engine)

    if model == 2:

        wing_subgraph_edges, wing_subgraph_left_node, wing_subgraph_right_node = generate_alpha_beta(
            meta, engine, alpha, beta)

        wing_subgraph_left_node, wing_subgraph_right_node = compress_graph(
            wing_subgraph_edges)

    if no_node:
        return {'left': wing_subgraph_left_node, 'right': wing_subgraph_right_node, 'edges': wing_subgraph_edges}

    if ninl == 1 and node not in wing_subgraph_left_node:
        return None
    if ninl == 0 and node not in wing_subgraph_right_node:
        return None

    wing_subgraph_left_node, wing_subgraph_right_node = breadth_first_search(
        wing_subgraph_left_node, wing_subgraph_right_node, wing_subgraph_edges, node, ninl)

    wing_subgraph_edges, wing_subgraph_left_node, wing_subgraph_right_node = get_subgraph_db(
        wing_subgraph_left_node, wing_subgraph_right_node,  meta, engine)

    # return construct_graph_db(node_data['left'], node_data['right'], wing_subgraph_edges, meta, engine, color_list)
    return {'left': wing_subgraph_left_node, 'right':  wing_subgraph_right_node, 'edges': wing_subgraph_edges}


# def wing_node_subgraph_node(input_data):
#     meta = input_data['meta']
#     engine = input_data['engine']
#     node = input_data['node']
#     wing_number = input_data['wing_number']
#     color_list = input_data['color_list']
#     # l_node = get_node(meta, engine, 0)
#     l_node = get_left_node(meta, engine)
#     # r_node = get_node(meta, engine, 1)
#     r_node = get_right_node(meta, engine)
#     alpha = input_data['alpha']
#     beta = input_data['beta']

#     no_node = False
#     if node is not None and node is not "":
#         node = get_id_by_name(meta, engine, node)
#         if node is None:
#             return None
#     else:
#         no_node = True

#     wing_subgraph_left_node, wing_subgraph_right_node = select_wing_number(
#         meta, engine, wing_number)

#     wing_subgraph_edges, node_data = get_subgraph_db(
#         wing_subgraph_left_node, wing_subgraph_right_node, engine)

#     if alpha != 0 and beta != 0:
#         wing_subgraph_edges, node_data = generate_alpha_beta_core(
#             node_data['left'], node_data['right'], wing_subgraph_edges, alpha, beta)

#     if no_node:
#         return construct_graph_db(node_data['left'], node_data['right'], wing_subgraph_edges, meta, engine, color_list)

#     if node not in wing_subgraph_nodes:
#         return None

#     node_d = 1
#     if node in wing_subgraph_right_node:
#         node_d = 0

#     wing_subgraph_left_node, wing_subgraph_right_node = breadth_first_search(
#         wing_subgraph_left_node, wing_subgraph_right_node, wing_subgraph_edges, node, node_d)
#     wing_subgraph_edges, node_data = get_subgraph_db(
#         wing_subgraph_left_node, wing_subgraph_right_node,  engine)

#     return construct_graph_db(node_data['left'], node_data['right'], wing_subgraph_edges, meta, engine, color_list)


def count_caterpillars(l_node, r_node, edges):
    total = 0
    # for u in (l_node + r_node):
    #     u_neighbor = find_neighbor(edges, u)
    #     for v in u_neighbor:
    #         if v < u:
    #             total += (len(u_neighbor)-1)*(len(find_neighbor(edges, v))-1)

    for u in l_node:
        u_neighbor = find_right_neighbor(edges, u)
        for v in u_neighbor:  # v is right node
            if v < u:
                total += (len(u_neighbor)-1) * \
                    (len(find_left_neighbor(edges, v))-1)

    for u in r_node:
        u_neighbor = find_left_neighbor(edges, u)
        for v in u_neighbor:  # v is left node
            if v < u:
                total += (len(u_neighbor)-1) * \
                    (len(find_right_neighbor(edges, v))-1)
    return total


def count_butterfly(left, right, e):

    l_node = left.copy()
    r_node = right.copy()
    edges = []
    ############count butterfly####################
    # process_l_node to distinguish left and right node
    for i in range(len(r_node)):
        r_node[i] = str(r_node[i])
    for i in range(len(l_node)):
        l_node[i] = "l_" + str(l_node[i])
    for i in range(len(e)):
        # edges[i][0] = "l_" + str(edges[i][0])
        # edges[i][1] = str(edges[i][1])
        l = "l_" + str(e[i][0])
        r = str(e[i][1])
        edges.append((l, r))

    nodes = l_node + r_node
    nodes_length = len(nodes)

    node_degree = {}

    for i in range(nodes_length):
        node_degree[i] = []

    initial_wedge = {}

    for node in nodes:
        degree = len(find_neighbor(edges, node))
        node_degree[degree].append(node)
        initial_wedge[node] = 0

    node_index = []

    # compute priority
    p = {}
    index = 1
    for i in range(nodes_length):
        if node_degree[i] == []:
            continue
        sort = quicksort(node_degree[i])[::-1]
        for c in sort:
            p[c] = index
            index += 1

    bf_count = 0
    for u in nodes:
        count_wedge = initial_wedge.copy()
        # initialise count wedge

        # for v in G.neighbors(u):
        for v in find_neighbor(edges, u):
            if p[v] < p[u]:
                # for w in G.neighbors(v):
                for w in find_neighbor(edges, v):
                    if p[w] < p[u]:
                        count_wedge[w] += 1

        for key, value in count_wedge.items():
            if value > 1:
                bf_count += factorial(value)/(factorial(value-2)*2)

    # 3

    caterpillars = count_caterpillars(l_node, r_node, edges)
    t = 0
    if caterpillars > 0:
        t = 4*(bf_count)/caterpillars
    return (int)(bf_count), t


def degree_calculate(l_node, r_node, edges):
    # nodes = nodes['left']+nodes['right']
    l_degree_table = {}
    r_degree_table = {}
    for n in l_node:
        l_degree_table[n] = 0
    for n in r_node:
        r_degree_table[n] = 0

    for e in edges:
        l_degree_table[e[0]] += 1
        r_degree_table[e[1]] += 1

    value_list = list(l_degree_table.values()) + list(r_degree_table.values())

    if len(value_list) == 0:
        return [0, 0, 0]

    return [sum(value_list)/len(value_list),
            max(value_list), min(value_list)]


def generate_author_table(l_node, r_node, edges, meta, engine):
    if len(l_node) == 0:
        return []
    nodes_degree = {}
    for n in (l_node):
        nodes_degree[n] = 0

    for e in edges:
        nodes_degree[e[0]] += 1

    data = []
    # node_name = get_node_list_name(l_node, meta, engine)
    node_name = get_left_node_list_name(l_node, meta, engine)
    for i in range(len(l_node)):
        node_data = {'ID': (int)(
            l_node[i]), 'Author': node_name[l_node[i]], 'Degree': nodes_degree[l_node[i]]}
        data.append(node_data)
    return data


def process_paper(text):
    s = text.split(' ')
    result = ""
    i = 0
    while s:
        if i+6 >= len(s):
            result += " ".join(s[i:])
            break
        result += " ".join(s[i:i+6]) + "\n"
        i += 6

    return result


def generate_paper_table(l_node, r_node, edges, meta, engine):
    if len(r_node) == 0:
        return []

    nodes_degree = {}
    for n in (r_node):
        nodes_degree[n] = 0

    for e in edges:
        nodes_degree[e[1]] += 1

    data = []
    # node_name = get_node_list_name(r_node, meta, engine)
    node_name = get_right_node_list_name(r_node, meta, engine)
    for i in r_node:
        node_data = {'ID': (int)(
            i), 'Paper': node_name[i], 'Degree': nodes_degree[i]}
        data.append(node_data)
    return data


def process_data(data, filename, meta, engine):
    if '.xml' in filename:
        return read_xml_to_db(filename, meta, engine)
    # else:
        # return read_file_to_db(data, meta, engine)
    return None


def read_file_to_db(data, meta, engine):
    data_list = data.split("\n")
    i = 0
    x = []
    y = []
    edges = []
    for line in data_list:

        number = line.split()
        if number == []:
            continue

        # check if the first line is '%', skip
        if not number[0].isdigit() and not number[0].isalpha():
            continue

        i += 1
        x1 = "x_" + number[1]
        y1 = "y_" + number[0]
        if x1 not in x:
            x.append(x1)
        if y1 not in y:
            y.append(y1)
        edges.append((x1, y1))

    x = list(x)
    y = list(y)
    edges = list(edges)

    x_dict = {}
    for i, value in enumerate(x):
        x_dict[value] = i
    y_dict = {}
    for i, value in enumerate(y):
        y_dict[value] = i

    edge_list = []
    for e in edges:
        edge_list.append((x_dict[e[0]], y_dict[e[1]]))
    # x-> left node
    # y-> right node
    max_wing, hier, wing_number = wing_decomposition(
        list(range(len(x))), list(range(len(y))), edge_list)

    node_data = [{'name': value, 'bipartite': 0, 'hierarchy': hier[value]}
                 for value in x] + [{'name': value, 'bipartite': 1, 'hierarchy': hier[value]} for value in y]

    left_data = [{'id': i, 'name': value, 'bipartite': 0, 'hierarchy': hier[value]}
                 for i, value in enumerate(x)]

    right_data = [{'id': i, 'name': value, 'bipartite': 1,
                   'hierarchy': hier[value]} for i, value in enumerate(y)]

    # my_table = Table('nodes', meta, autoload=True)
    left_table = Table('left', meta, autoload=True)
    engine.execute(left_table.insert(), left_data)

    right_table = Table('right', meta, autoload=True)
    engine.execute(right_table.insert(), right_data)

    # edge_data = [{'left': e[0], 'right':e[1], 'wingno':wing_number[e]}
    #  for e in edges]
    edge_data = [{'left': e[0], 'right':e[1], 'wingno':wing_number[e]}
                 for e in edge_list]

    edge_table = Table('edges', meta, autoload=True)
    engine.execute(edge_table.insert(), edge_list)
    return data


def read_xml_to_db(file, meta, engine):
    try:

        context = ET.iterparse(file, events=("end",), recover=True)
        context = iter(context)

        x = set()
        y = set()
        edges = set()
        i = 0

        x_degree = {}
        y_degree = {}

        authors = []
        for event, element, in context:
            if element.text is None:
                continue

            text = element.text

            if element.tag == 'author':
                authors.append(text)
            if element.tag == 'title':
                title = text

            if len(element) >= 2:
                if title == "" or len(title) < 2:
                    title = ""
                    authors = []
                    continue
                try:
                    # print(authors,title)
                    x.update(authors)
                    y.add(title)
                    for a in authors:
                        edges.add((a, title))
                        # if a in x_degree.keys():
                        #     x_degree[a] += 1
                        # else:
                        #     x_degree[a] = 1

                    # if title in y_degree.keys():
                    #     y_degree[title] += 1
                    # else:
                    #     y_degree[title] = 1
                except:
                    print("character error")
                    x.remove(authors)
                    y.remove(title)

                finally:
                    title = ""
                    authors = []

        if len(x.intersection(y)) != 0:
            r = set()
            for i in x.intersection(y):
                y.remove(i)

                for e in edges:
                    if e[1] == i:
                        r.add(e)

            for i in r:
                edges.remove(i)

        x = list(x)
        y = list(y)
        edges = list(edges)
        # calculate degrees:
        for i in x:
            x_degree[i] = 0
        for i in y:
            y_degree[i] = 0
        for e in edges:
            x_degree[e[0]] += 1
            y_degree[e[1]] += 1

        x_dict = {}
        for i, value in enumerate(x):
            x_dict[value] = i

        y_dict = {}
        for i, value in enumerate(y):
            y_dict[value] = i

        max_wing, hier, wing_number = wing_decomposition(
            x, y, edges)
    except:
        return None
    else:
        # node_data = [{'name': value, 'bipartite': 0, 'hierarchy': hier[value]}
        #  for value in x] + [{'name': value, 'bipartite': 1, 'hierarchy': hier[value]} for value in y]

        left_data = [{'id': i, 'name': value, 'bipartite': 0, 'hierarchy': hier[value], 'degree':x_degree[value]}
                     for i, value in enumerate(x)]

        right_data = [{'id': i, 'name': value, 'bipartite': 1,
                       'hierarchy': hier[value], 'degree':y_degree[value]} for i, value in enumerate(y)]

        # my_table = Table('nodes', meta, autoload=True)
        left_table = Table('left', meta, autoload=True)
        engine.execute(left_table.insert(), left_data)

        right_table = Table('right', meta, autoload=True)
        engine.execute(right_table.insert(), right_data)

        # edge_data = [{'left': e[0], 'right':e[1], 'wingno':wing_number[e]}
        #  for e in edges]
        edge_data = [{'left': x_dict[e[0]], 'right':y_dict[e[1]], 'wingno':wing_number[e]}
                     for e in edges]

        edge_table = Table('edges', meta, autoload=True)
        engine.execute(edge_table.insert(), edge_data)

        return True

# engine = create_engine('sqlite:///graph.db', echo = False)
# meta = MetaData(bind=engine)
