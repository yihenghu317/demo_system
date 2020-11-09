from read_db import *


def generate_alpha_beta_core(l_node, r_node, edges, alpha, beta):
    l_nodes_degree = {}
    r_nodes_degree = {}

    for n in l_node:
        l_nodes_degree[n] = 0
    for n in r_node:
        r_nodes_degree[n] = 0

    new_l_node = l_node.copy()
    new_r_node = r_node.copy()
    new_e = edges.copy()

    for e in edges:
        l_nodes_degree[e[0]] += 1
        r_nodes_degree[e[1]] += 1

    prev_l = None
    prev_r = None

    while prev_l != new_l_node and prev_r != new_r_node:
        prev_l = new_l_node.copy()
        prev_r = new_r_node.copy()

        for l in l_node:
            if l not in new_l_node:
                continue

            if l_nodes_degree[l] < alpha:
                for e in edges:
                    if e not in new_e:
                        continue

                    if e[0] == l:
                        r_nodes_degree[e[1]] += -1
                        new_e.remove(e)
                new_l_node.remove(l)

        for r in r_node:
            if r not in new_r_node:
                continue

            if r_nodes_degree[r] < beta:
                for e in edges:
                    if e not in new_e:
                        continue

                    if e[1] == r:
                        l_nodes_degree[e[0]] += -1
                        new_e.remove(e)
                new_r_node.remove(r)

    return new_e, new_l_node, new_r_node


def get_max_alpha_beta(edges):
    l_node = {}
    r_node = {}
    for e in edges:
        if e[0] in l_node.keys():
            l_node[e[0]] += 1
        else:
            l_node[e[0]] = 1

        if e[1] in r_node.keys():
            r_node[e[1]] += 1
        else:
            r_node[e[1]] = 1

    return max(l_node.values()), max(r_node.values())


def generate_alpha_beta(meta, engine, alpha, beta):
    left = get_left_node_degree_greater_than(meta, engine, alpha)
    right = get_right_node_degree_greater_than(meta, engine, beta)

    edges = get_edge_subgraph(meta, engine, left, right)

    return generate_alpha_beta_core(left, right, edges, alpha, beta)


def get_total_max_alpha_beta(meta, engine):
    return get_max_left_degree(meta, engine), get_max_right_degree(meta, engine)
