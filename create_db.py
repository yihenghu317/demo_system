from sqlalchemy import *


engine = create_engine('sqlite:///new_graph.db', echo=True)
meta = MetaData()

# left_node = Table(
#     'left', meta,
#     Column('id', Integer, autoincrement=True, primary_key=True),
#     Column('name', String),
#     Column('bipartite', Integer),
#     Column('hierarchy', Integer),
#     Column('degree', Integer)
# )

# right_node = left_node = Table(
#     'right', meta,
#     Column('id', Integer, autoincrement=True, primary_key=True),
#     Column('name', String),
#     Column('bipartite', Integer),
#     Column('hierarchy', Integer),
#     Column('degree', Integer)
# )


# edges = Table(
#     'edges', meta,
#     Column('left', Integer),
#     Column('right', Integer),
#     Column('wingno', Integer),
# )

# meta.create_all(engine)
