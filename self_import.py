import re
from sqlalchemy import *
from new_functions import *


def process_self_import(edge, left, right, meta, engine):
    try:
        edge = edge.split("\n")
        edges = set()
        edge_key = set()
        x_degree = {}
        y_degree = {}
        for l in edge:
            l = l.replace("\n", "")
            e = re.split('[\t \n|,]+', l)
            if len(e) < 2:
                continue

            l = e[0] + '_l'
            r = e[1] + '_r'
            edge_key.add((l, r))

            e[0] = int(e[0])
            e[1] = int(e[1])
            edges.add((e[0], e[1]))

            if e[0] in x_degree.keys():
                x_degree[e[0]] += 1
            else:
                x_degree[e[0]] = 1

            if e[1] in y_degree.keys():
                y_degree[e[1]] += 1
            else:
                y_degree[e[1]] = 1

        edges = list(edges)
        edge_key = list(edge_key)

        left = left.split("\n")
        right = right.split("\n")
        x = {}
        y = {}
        x_key = []
        y_key = []

        for l in left:
            l = l.replace("\n", "")
            e = re.split('[\t \n|,]+', l, 1)
            if len(e) < 2:
                continue

            x_key.append(e[0] + "_l")

            e[0] = int(e[0])
            x[e[0]] = e[1]

        for l in right:
            l = l.replace("\n", "")
            e = re.split('[\t \n|,]+', l, 1)
            if len(e) < 2:
                continue
            y_key.append(e[0] + "_r")

            e[0] = int(e[0])
            y[e[0]] = e[1]

        max_wing, hier, wing_number = wing_decomposition(
            x_key, y_key, edge_key)
    except:
        return None

    else:

        xd_keys = list(x_degree.keys())
        yd_keys = list(y_degree.keys())

        left_data = [{'id': key, 'name': value, 'bipartite': 0,
                      'hierarchy': hier[str(key) + '_l'], 'degree':x_degree[key] if key in xd_keys else 0} for key, value in x.items()]

        right_data = [{'id': key, 'name': value, 'bipartite': 1,
                       'hierarchy': hier[str(key) + '_r'], 'degree':y_degree[key] if key in yd_keys else 0} for key, value in y.items()]

        left_table = Table('left', meta, autoload=True)
        engine.execute(left_table.insert(), left_data)

        right_table = Table('right', meta, autoload=True)
        engine.execute(right_table.insert(), right_data)

        edge_data = [{'left': e[0], 'right':e[1], 'wingno':wing_number[(str(e[0]) + '_l', str(e[1]) + '_r')]}
                     for e in edges]

        edge_table = Table('edges', meta, autoload=True)
        engine.execute(edge_table.insert(), edge_data)

        return True
