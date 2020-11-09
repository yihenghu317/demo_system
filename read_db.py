from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, insert
from xml.dom import minidom
import pandas as pd
from itertools import chain
import plotly.graph_objs as go


def insert_node(data, meta, engine, my_table=None):
    if my_table == None:
        my_table = Table('nodes', meta, autoload=True)

    try:
        engine.execute(my_table.insert(),
                       name=data['name'], bipartite=data['bipartite'])
    finally:
        return


def insert_edges(data, meta, engine, my_table=None):
    if my_table is None:
        my_table = Table('edges', meta, autoload=True)

    try:
        engine.execute(my_table.insert(),
                       left=data['left'], right=data['right'])
    finally:
        return


# def delete_all(meta, engine):
#     nodes = Table('nodes', meta, autoload=True)
#     edges = Table('edges', meta, autoload=True)

#     try:
#         d = nodes.delete()
#         d.execute()

#     # try:
#         d = edges.delete()
#         d.execute()
#     finally:
#         return

def delete_all(meta, engine):
    right = Table('right', meta, autoload=True)
    left = Table('left', meta, autoload=True)
    edges = Table('edges', meta, autoload=True)

    try:
        d = right.delete()
        d.execute()

        d = left.delete()
        d.execute()

        d = edges.delete()
        d.execute()
    finally:
        return


def update_degree(degree_table, meta, my_table=None):
    if my_table is None:
        my_table = Table('nodes', meta, autoload=True)

    for key, value in degree_table.items():
        my_table.update(my_table.c.name == key).execute(degree=value)
    return


def fetch_data(q, engine):
    result = pd.read_sql(
        sql=q,
        con=engine
    )
    return result

# def find_neighbor_from_db(node, meta,engine):
#     query = (
#         f'''
#         SELECT LEFT
#         FROM EDGES
#         WHERE right='{node}'
#         '''
#     )
#     result = fetch_data(query,engine)
#     # result = result.values.tolist()
#     result = list(chain.from_iterable(result.values))

#     query = (
#         f'''
#         SELECT RIGHT
#         FROM EDGES
#         WHERE left='{node}'
#         '''
#     )

#     results = fetch_data(query,engine)
#     results = list(chain.from_iterable(results.values))

#     result = result + results


#     # print(result)
#     return result

def find_neighbor(edges, node):
    result = []
    for edge in edges:
        if node == edge[0]:
            result.append(edge[1])
        if node == edge[1]:
            result.append(edge[0])
    return result


def breadth_first_search(l_nodes, r_nodes, edges, source, left=1):

    queue = []
    left_que = []
    right_que = []

    visited_r = {}
    visited_l = {}
    for i in l_nodes:
        visited_l[i] = False
    for i in r_nodes:
        visited_r[i] = False

    if left == 1:
        left_que.append(source)
        visited_l[i] = True
        queue.append(1)
    else:
        right_que.append(source)
        visited_r[i] = True
        queue.append(0)

    # visited = {}
    # for i in nodes:
    #     visited[i] = False
    # visited[source] = True

    # result = []
    l_result = []
    r_result = []

    while queue:
        d = queue.pop(0)
        # result.append(s)
        s = None
        if d == 1:  # left
            s = left_que.pop(0)
            l_result.append(s)
            for i in find_right_neighbor(edges, s):  # i is right neighbor
                if i not in visited_r.keys():
                    continue
                if visited_r[i] == False:
                    right_que.append(i)
                    visited_r[i] = True
                    queue.append(0)

        else:
            #  s is right node
            s = right_que.pop(0)
            r_result.append(s)

            for i in find_left_neighbor(edges, s):  # i is left neighbor
                if i not in visited_l.keys():
                    continue
                if visited_l[i] == False:
                    left_que.append(i)
                    visited_l[i] = True
                    queue.append(1)

        # for i in find_neighbor(edges, s):
        #     if i not in visited.keys():
        #         continue
        #     if visited[i] == False:
        #         queue.append(i)
        #         visited[i] = True
    return l_result, r_result


# for left node to find its right neighbor
def find_right_neighbor(edges, node):
    result = []
    for e in edges:
        if e[0] == node:
            result.append(e[1])
    return result

# for right node to find its left neighbor


def find_left_neighbor(edges, node):
    result = []
    for e in edges:
        if e[1] == node:
            result.append(e[0])
    return result


def process_disconnected_graph(l_node, r_node, edges):
    # all_node = l_node+r_node
    result_l = []
    result_r = []
    while l_node + r_node:
        s = (l_node + r_node)[0]

        nd = 1
        if not l_node:
            nd = 0

        l, r = breadth_first_search(l_node, r_node, edges, s, nd)

        # if not (len(l) == 0 or len(r) == 0):

        result_l += l
        result_r += r

        # for node in relate:
        #     if node in l_node:
        #         result_l.append(node)

        #     if node in r_node:
        #         result_r.append(node)

        # all_node = [a for a in all_node if a not in relate]
        l_node = [a for a in l_node if a not in l]
        r_node = [a for a in r_node if a not in r]

    return list(set(result_l)), list(set(result_r))

# return edges,[l,r]


def get_subgraph_db(l_node, r_node, meta, engine):
    res_data = {}
    res_data['left'] = l_node
    res_data['right'] = r_node

    # edge_query = (
    #     f'''
    #     select left, right from edges
    #     '''
    # )

    edges = get_edge_subgraph(meta, engine, l_node, r_node)

    res_data['left'], res_data['right'] = process_disconnected_graph(
        res_data['left'], res_data['right'], edges)

    return edges, res_data['left'], res_data['right']


def get_id(meta, engine, name):
    query = (
        f'''
        select CAST(id as TEXT) from nodes where 
        name = '{name}'
        '''
    )
    result = fetch_data(query, engine)
    result = list(chain.from_iterable(result.values))
    if result:
        return result[0]
    else:
        return None


def get_id_by_name(meta, engine, name):
    l_query = (
        # f'''
        # select CAST(id as TEXT) from left where
        # name = '{name}'
        # '''
        f'''
        select id from left where 
        name = '{name}'
        '''
    )

    result = fetch_data(l_query, engine)
    result = list(chain.from_iterable(result.values))

    if result:
        return result[0], 1

    r_query = (
        f'''
        select id from right where 
        name = '{name}'
        '''
    )
    result = fetch_data(r_query, engine)
    result = list(chain.from_iterable(result.values))

    if result:
        return result[0], 0
    return None, None


def get_node(meta, engine, bipartite):
    query = (
        f'''
        Select CAST(id as TEXT) from nodes
        where bipartite = '{bipartite}'
        order by name
        '''
    )
    results = fetch_data(query, engine)
    results = list(chain.from_iterable(results.values))
    return results


def get_left_node(meta, engine):
    query = (
        f'''
        Select id from left
        '''
    )
    results = fetch_data(query, engine)
    results = list(chain.from_iterable(results.values))
    return results


def get_right_node(meta, engine):
    query = (
        f'''
        Select id from right
        '''
    )
    results = fetch_data(query, engine)
    results = list(chain.from_iterable(results.values))
    return results


def get_all_nodes(meta, engine):
    l = get_node(meta, engine, 0)
    r = get_node(meta, engine, 1)
    return l+r


def get_edges(meta, engine):
    query = (
        f'''
        select left, right from edges
        '''
    )
    # query = (
    #     f'''
    #     select CAST(b.id as TEXT) as left_id,CAST(n.id as TEXT) as right_id from
    #     ( (edges join nodes on nodes.name = edges.left) as b
    #     join nodes as n on b.right = n.name )
    #     '''
    # )
    results = fetch_data(query, engine).values

    res = []
    for e in results:
        res.append((e[0], e[1]))
    # print(res)

    return res


def get_node_list_name(id_list, meta, engine):
    if len(id_list) == 1:
        id_list = '(' + str(id_list[0]) + ')'
    else:
        id_list = str(tuple(id_list))

    query = (
        '''SELECT CAST(id as TEXT),name FROM nodes WHERE id IN ''' + id_list
    )
    results = fetch_data(query, engine).values
    res = {}
    for i in results:
        res[i[0]] = i[1]

    return res


def get_right_node_list_name(id_list, meta, engine):
    if len(id_list) == 1:
        id_list = '(' + str(id_list[0]) + ')'
    else:
        id_list = str(tuple(id_list))

    query = (
        '''SELECT id,name FROM right WHERE id IN ''' + id_list
    )
    results = fetch_data(query, engine).values
    res = {}
    for i in results:
        res[i[0]] = i[1]

    return res


def get_left_node_list_name(id_list, meta, engine):
    if len(id_list) == 1:
        id_list = '(' + str(id_list[0]) + ')'
    else:
        id_list = str(tuple(id_list))

    query = (
        '''SELECT id,name FROM left WHERE id IN ''' + id_list
    )
    results = fetch_data(query, engine).values
    res = {}
    for i in results:
        res[i[0]] = i[1]

    return res


def get_max_hier(meta, engine):
    query = (
        f'''
        select max(hierarchy) from left
        '''
    )

    results = fetch_data(query, engine)
    result_1 = list(chain.from_iterable(results.values))[0]

    query = (
        f'''
        select max(hierarchy) from right
        '''
    )

    results = fetch_data(query, engine)
    result_2 = list(chain.from_iterable(results.values))[0]

    result = max(result_1, result_2)
    return result


# def get_max_alpha(meta, engine):
#     query = (
#         f'''
#         SELECT c.name, max(c.degree) FROM
#         (SELECT nodes.name, count(*) as degree
#         from nodes join edges on
#         nodes.name = edges.left
#         group by nodes.name
#         order by nodes.name) as c
#         '''
#     )
#     results = fetch_data(query, engine)
#     result = list(chain.from_iterable(results.values))[1]
#     return result


# def get_max_beta(meta, engine):
#     query = (
#         f'''
#         SELECT c.name, max(c.degree) FROM
#         (SELECT nodes.name, count(*) as degree
#         from nodes join edges on
#         nodes.name = edges.right
#         group by nodes.name
#         order by nodes.name) as c
#         '''
#     )
#     results = fetch_data(query, engine)
#     result = list(chain.from_iterable(results.values))[1]
#     return result


def update_hierarchy(hierarchy, meta, node_table=None):
    if node_table is None:
        node_table = Table('nodes', meta, autoload=True)

    for key, value in hierarchy.items():
        node_table.update(node_table.c.name == key).execute(hierarchy=value)

    return

# return nodes


# def select_wing_number(meta, engine, wing_number):
#     query = (
#         f'''
#         Select CAST(id as TEXT) from nodes
#         where hierarchy >= '{wing_number}'
#         order by id
#         '''
#     )

#     result = list(chain.from_iterable(fetch_data(query, engine).values))
#     return result
def select_wing_number(meta, engine, wing_number):
    l_query = (
        f'''
         Select id from left
         where hierarchy >= '{wing_number}'
         order by id    
        '''
    )

    l_result = list(chain.from_iterable(fetch_data(l_query, engine).values))

    r_query = (
        f'''
        Select id from right
         where hierarchy >= '{wing_number}'
         order by id    
        '''
    )

    r_result = list(chain.from_iterable(fetch_data(r_query, engine).values))

    return l_result, r_result


def get_edge_wingno(meta, engine):
    # query = (
    #     f'''
    #     select CAST(b.id as TEXT) as left_id,CAST(n.id as TEXT) as right_id,wingno from
    #     ( (edges join nodes on nodes.name = edges.left) as b
    #     join nodes as n on b.right = n.name )
    #     '''
    # )
    query = (
        f'''
        select * from edges
        '''
    )
    result = fetch_data(query, engine).values
    wing_no = {}
    for c in result:
        wing_no[(c[0], c[1])] = c[2]
    return wing_no


def get_left_node_degree_greater_than(meta, engine, degree):
    if degree == 0:
        degree = 1

    query = (
        f'''
        Select id from left where degree >= '{degree}'
        '''
    )
    results = fetch_data(query, engine)
    results = list(chain.from_iterable(results.values))
    return results


def get_right_node_degree_greater_than(meta, engine, degree):
    if degree == 0:
        degree = 1
    query = (
        f'''
        Select id from right where degree >= '{degree}'
        '''
    )
    results = fetch_data(query, engine)
    results = list(chain.from_iterable(results.values))
    return results


def genearete_tuple_str(id_list):
    result = "()"
    if len(id_list) == 1:
        result = '(' + str(id_list[0]) + ')'
    else:
        result = str(tuple(id_list))
    return result


def get_edge_subgraph(meta, engine, left_id, right_id):
    # if len(id_list) == 1:
    #     id_list = '(' + id_list[0] + ')'
    # else:
    #     id_list = str(tuple(id_list))
    l = genearete_tuple_str(left_id)
    r = genearete_tuple_str(right_id)

    query = (
        '''select left, right from edges where left IN ''' + l + ''' and right IN ''' + r
    )

    results = fetch_data(query, engine)

    return results.values.tolist()


def get_max_left_degree(meta, engine):
    query = (
        f'''
        select max(degree) from left
        '''
    )

    results = fetch_data(query, engine)
    result = list(chain.from_iterable(results.values))[0]
    return result


def get_max_right_degree(meta, engine):
    query = (
        f'''
        select max(degree) from right
        '''
    )

    results = fetch_data(query, engine)
    result = list(chain.from_iterable(results.values))[0]
    return result
