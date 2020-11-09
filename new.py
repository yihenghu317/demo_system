from read_db import *
from alpha_beta_core import *


engine = create_engine('sqlite:///new_graph.db', echo=False)
meta = MetaData(bind=engine)


# left_node = get_left_node(meta, engine)
# right_node = get_right_node(meta, engine)
# edges = get_edges(meta, engine)


# alpha, beta = get_max_alpha_beta(edges)

# e, l, r = generate_alpha_beta_core(left_node, right_node, edges, alpha, 0)
e, l, r = generate_alpha_beta(meta, engine, 40, 2)
print(e, l, r)
