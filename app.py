import base64
import os
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import networkx as nx
from collections import Counter
from dash.dependencies import Input, Output, State
import dash_table
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go
# from functions import *
from graph_generator import *
import plotly.tools as tls
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
from read_db import *
from sqlalchemy import create_engine, MetaData
import sys
import os
from alpha_beta_core import *
from movie_import import *
from self_import import *

num_nodes = 1000
engine = create_engine('sqlite:///graph.db', echo=False)
meta = MetaData(bind=engine)


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__,
                # external_stylesheets=external_stylesheets)
                external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)

color_list = []
max_compare = 4
Exisiting_Graph = False
Last_modified = []
New_File = False
New_File_compare = False
prev_wing_no = 0


Trigger_compare_alpha = False
Trigger_compare_beta = False
Trigger_compare = False
Trigger_compare_0 = False
Trigger_select_value = False
First_compare_0 = False

################### upload modal #####################################


def generate_upload_box(upload_id):
    label_id = upload_id + "-result"
    return html.Div([
        dcc.Upload(
            id=upload_id,
            children=html.Div([
                'Drag and Drop or ',
                html.A('Select Files')
            ]),
            style={
                'width': '60%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '1px',
                'borderStyle': 'dashed',
                'borderRadius': '5px',
                'textAlign': 'center',
                'marginLeft': '10px',
            },
            # Allow multiple files to be uploaded
            multiple=False
        ),
        html.Label(id=label_id, style={
            'width': '60%',
            'textAlign': 'center',
            'font-size': 10,
            'color': 'green'})
    ])


input_item_types = html.Div([
    dbc.FormGroup(
        [
            dbc.Label("Choose one"),
            dbc.RadioItems(
                options=[
                    {"label": "Author Paper System", "value": 1},
                    {"label": "User Movie System", "value": 3},
                    {"label": "Other System", "value": 2},

                ],
                value=1,
                id="radioitems-upload-data-type",
                # inline=True,
            ),
        ]
    ),
    dbc.Button("Enter", id="select-upload-type-button"),
])

author_paper_upload = html.Div([
    dcc.Upload(
        id='author-paper-upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '70%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='output-data-upload'),
    html.Label(id='author-paper-upload-data-result', style={
        'width': '60%',
        'textAlign': 'center',
        'font-size': 10,
        'color': 'green'}),
    # dbc.Button('Submit', id = 'author-paper-submit'),
])

self_defined_upload_system = html.Div([
    html.Div([
        html.Label("Upload edge file",),
        html.Label("e.g. left node id, right node id", style={
                   'font-size': '12px', 'color': "grey", "marginLeft": '10px'})
    ]),
    generate_upload_box("self-defined-edge-upload"),

    html.Div([
        html.Label("Upload left node file"),
        html.Label("e.g. id, name", style={
                   'font-size': '12px', 'color': "grey", "marginLeft": '10px'})
    ]),
    generate_upload_box('self-defined-left-node'),
    html.Div([
        html.Label("Upload right node file"),
        html.Label("e.g. id, name", style={
                   'font-size': '12px', 'color': "grey", "marginLeft": '10px'})
    ]),
    generate_upload_box('self-defined-right-node'),
])


movie_upload_system = html.Div([
    html.Div([
        html.Label("Upload data file",),
        html.Label("e.g. user id, movie id", style={
                   'font-size': '12px', 'color': "grey", "marginLeft": '10px'})
    ]),
    generate_upload_box("movie-edge-upload"),

    html.Div([
        html.Label("Upload user file"),
        html.Label("e.g. id, name", style={
                   'font-size': '12px', 'color': "grey", "marginLeft": '10px'})
    ]),
    generate_upload_box('movie-left-node'),
    html.Div([
        html.Label("Upload movie file"),
        html.Label("e.g. id, name", style={
                   'font-size': '12px', 'color': "grey", "marginLeft": '10px'})
    ]),
    generate_upload_box('movie-right-node'),
])


submit_button = dbc.Button('Submit', id='upload-submit-button')

back_button = dbc.Button('Back', id='back-button', style={'marginLeft': '85%'})

warning_label = html.Label(id='submit-result-label', children=[], style={
    'color': 'red',
    'marginLeft': '20px'
})

upload_modal = html.Div([
    dcc.Store(id='select-upload-data-type'),
    dcc.Store(id='back-upload'),
    dcc.Store(id='current-upload-data'),  # store the upload file
    dcc.Store(id='self-data'),
    dcc.Store(id='author-paper-data'),
    dcc.Store(id='user-movie-data'),
    html.Div(
        [
            dbc.Button("Upload files", id="open"),
            dbc.Modal(
                [
                    dbc.ModalHeader([
                        dbc.Button("Close", id="close", style={
                            'marginLeft': '10%'}),
                    ]),
                    dbc.ModalBody(id='upload-data-type-section',
                                  children=[input_item_types]),
                ],
                id="modal",
                style={'marginTop': "50px"}
            ),
        ]),
],)

######################################################################

Left_col = dbc.Jumbotron(
    [
        upload_modal,
        # html.Label("Drag or drop a file", className="lead"),
        dcc.Upload(
            id="datatable-upload",
            children=html.Div(
                ["Upload"]
            ),
            style={
                "width": "60%",
                "height": "60px",
                "lineHeight": "60px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "10px",
                "textAlign": "center",
                # "margin": "20px",
                "display": "None",
            },
            multiple=False,
            className="dcc_control",
        ),
        dash_table.DataTable(id='datatable-upload-container'),
        html.Label("Select a node", className="lead",
                   style={"marginTop": 50},),
        dcc.Input(id='input-box', type='text',
                  style={"width": "90%", 'marginBottom': '20px'}),
        html.Div(id='output-container-button'),

        ################# select bitruss/abcore ##################
        html.Div([
            # dbc.Label("Choose one"),
            dbc.RadioItems(
                options=[
                    {"label": "Bitruss", "value": 1, },
                    {"label": u"(\u03B1 , \u03B2) - core",
                        "value": 2, },
                ],
                value=1,
                id="select-bitruss-abcore",
                style={'display': 'None'}
            ),
        ], style={'marginBottom': '20px'}),




        ################# select bitruss/abcore ##################
        html.Div(id='bitruss-section', children=[
            # html.Label("Bitruss number", className="lead",
                    #    style={"marginTop": 50},),
            html.Div(id='bitruss_value',),
            dcc.Slider(
                id='wing-number',
                min=0,
                value=0,
                step=1,
                className="dcc_control",
                disabled=True,
            ),


        ]),


        html.Div(id='abcore-section', children=[
            # html.H5(u"(\u03B1 , \u03B2) - core"),
            html.Div([
                html.Label(u"\u03B1 :", style={"display": 'inline-block'}),
                html.Div(id='alpha_value', style={"display": 'inline-block'}),
                dcc.Slider(id='alpha',
                           min=0,
                           max=5,
                           value=0,
                           step=1,
                           disabled=True,),
            ], style={'marginBottom': 10}),

            html.Label(u"\u03B2 :", style={"display": 'inline-block'}),
            html.Div(id='beta_value', style={"display": 'inline-block'}),
            dcc.Slider(id='beta',
                       min=0,
                       max=5,
                       value=0,
                       step=1,
                       disabled=True),
        ], style={'display': 'none'}),


        html.Div(
            id='compare_section',
            children=[
                dcc.Store(id='compare-value-data'),
                dbc.Checklist(
                    options=[
                        {'label': 'Compare', 'value': 1},
                    ],
                    value=0,
                    id='if_compare',
                    inline=True,
                    switch=True,
                ),

                html.Div(
                    id='compare_graph_no_section',
                    children=[
                        dbc.RadioItems(
                            options=[
                                {"label": "Left", "value": 1},
                                {"label": "Right", "value": 2},
                            ],
                            value=1,
                            id="compare_graph_no",
                            inline=True,
                        ),
                    ], style={'display': 'none'}),
            ], style={'display': 'none', 'marginTop': "40px"}),


    ]
)

##################### upload modal callbacks #######################


def read_download_content(contents, names):
    data = contents.encode("utf8").split(b";base64,")[1]
    delete_files()
    with open('./read_file/'+names, "wb") as fp:
        fp.write(base64.decodebytes(data))
    data = base64.decodebytes(data).decode("utf-8")
    return data


Submit_click = False
Submit_click_label = False


@app.callback(
    Output("modal", "is_open"),
    [Input("open", "n_clicks"), Input("close", "n_clicks"),
     Input("current-upload-data", "data")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, data, is_open):
    global Submit_click
    if data is not None and data['result'] == None and Submit_click:
        Submit_click = False
        raise PreventUpdate
    Submit_click = False
    if n1 or n2 or data:
        return not is_open
    return is_open


@app.callback(
    Output('select-upload-data-type', 'data'),
    [Input('select-upload-type-button', 'n_clicks')],
    [State('radioitems-upload-data-type', 'value')]
)
def store_select_upload_data(n_clicks, value):
    if value is not None and n_clicks is not None:
        type = "author-paper"
        if value == 2:
            type = "self-defined"
        if value == 3:
            type = 'user-movie'

        return {'select_type': type}
    raise PreventUpdate


Back = False


@app.callback(
    Output('upload-data-type-section', 'children'),
    [Input('select-upload-data-type', 'data'),
     Input('back-upload', 'data')]
)
def display_correponding_data_type_section(data, back):
    global Back
    if back is not None and Back == True:
        Back = False
        return [input_item_types]
    if data is None:
        raise PreventUpdate
    if data['select_type'] == 'author-paper':
        return [author_paper_upload, submit_button, warning_label, back_button]
    if data['select_type'] == 'self-defined':
        return [self_defined_upload_system, submit_button, warning_label, back_button]
    if data['select_type'] == 'user-movie':
        return [movie_upload_system, submit_button, warning_label, back_button]

    raise PreventUpdate


@app.callback(
    Output('submit-result-label', 'children'),
    [Input('current-upload-data', 'data'), ],
)
def display_warning_or_not(data):
    if data is None:
        raise PreventUpdate
    global Submit_click_label

    if data['result'] == None and Submit_click_label:
        Submit_click_label = False
        return "Incorrect Data"
    Submit_click_label = False
    return ""


@app.callback(
    Output('back-upload', 'data'),
    [Input('back-button', 'n_clicks'), ]
)
def store_back_info(n_clicks):
    if n_clicks is not None:
        global Back
        Back = True
        return {'Back': True}
    raise PreventUpdate


def parse_contents(contents):
    _, content_string = contents.split(',')
    # content_string = unicode(str, errors='replace')
    decoded = base64.b64decode(content_string).decode('utf-8', 'ignore')

    return decoded


result_labels_pre = ["self-defined-edge-upload", 'self-defined-left-node', 'self-defined-right-node',
                     'author-paper-upload-data', 'movie-edge-upload', 'movie-left-node', 'movie-right-node']
Trigger_submit_all = [False]*len(result_labels_pre)


@app.callback(
    Output('current-upload-data', 'data'),
    [Input('upload-submit-button', 'n_clicks')],
    [State('select-upload-data-type', 'data'),
     State('self-data', 'data'),
     State('author-paper-data', 'data'),
     State('user-movie-data', 'data')]
)
def display_submit(n_clicks, data, self_data, author_paper_data, user_movie_data):
    global Submit_click
    global Submit_click_label
    global New_File_compare

    Submit_click = True
    Submit_click_label = True

    if n_clicks is None or data is None:
        raise PreventUpdate
    # return [html.Label([n_clicks, data['select_type']])]
    content = None

    global New_File
    New_File = True

    result = None

    if author_paper_data is not None and data['select_type'] == 'author-paper':
        data_content = author_paper_data['content']
        delete_all(meta, engine)

        name = author_paper_data['filename']
        result = process_data(data_content, name, meta, engine)

    if self_data is not None and data['select_type'] == 'self-defined':
        delete_all(meta, engine)
        result = process_self_import(self_data['edge'],
                                     self_data['left'], self_data['right'], meta, engine)
        content = {
            'edge': self_data['edge'], 'left': self_data['left'], 'right': self_data['right']}

    if user_movie_data is not None and data['select_type'] == 'user-movie':
        delete_all(meta, engine)
        result = process_movie_self_import(user_movie_data['edge'],
                                           user_movie_data['left'], user_movie_data['right'], meta, engine)
        content = {
            'edge': user_movie_data['edge'], 'left': user_movie_data['left'], 'right': user_movie_data['right']}

    if result is not None:
        global result_labels_pre
        New_File_compare = True
        Trigger_submit_all = [True]*len(result_labels_pre)
    return {'type': data['select_type'], 'content': content, 'result': result}


@app.callback(
    Output('author-paper-data', 'data'),
    [Input('author-paper-upload-data', 'contents'),
     Input('author-paper-upload-data', 'filename')]
)
def store_author_paper_data(contents, filenames):
    if contents is None:
        raise PreventUpdate
    content = read_download_content(contents, filenames)
    name = "./read_file/" + filenames
    data = {}
    data['content'] = content
    data['filename'] = name
    return data


@app.callback(
    Output('self-data', 'data'),
    [Input('self-defined-edge-upload', 'contents'),
     Input('self-defined-left-node', 'contents'),
     Input('self-defined-right-node', 'contents')]
)
def store_self_data(edge, left, right):
    if edge is None or left is None or right is None:
        raise PreventUpdate
    data = {}

    data['edge'] = parse_contents(edge)
    data['left'] = parse_contents(left)
    data['right'] = parse_contents(right)

    return data


@app.callback(
    Output('user-movie-data', 'data'),
    [Input('movie-edge-upload', 'contents'),
     Input('movie-left-node', 'contents'),
     Input('movie-right-node', 'contents')]
)
def store_self_data(edge, left, right):
    if edge is None or left is None or right is None:
        raise PreventUpdate
    data = {}

    data['edge'] = parse_contents(edge)
    data['left'] = parse_contents(left)
    data['right'] = parse_contents(right)

    return data


for c, i in enumerate(result_labels_pre):
    ul_id = i + '-result'

    @app.callback(
        Output(ul_id, 'children'),
        [Input(i, 'contents'),
         Input('current-upload-data', 'data')]
    )
    def display_upload_result(contents, upload_data, index=c):
        global Trigger_submit_all
        if contents is None:
            return []
        if Trigger_submit_all[index]:
            Trigger_submit_all[index] = False
            return []
        return "Uploaded!"
####################################################################


candidate_graph = []
candidate_data = []
max_graph_no = 1

for i in range(max_graph_no):
    my_style = {}
    html_style = {}

    my_style = {'display': 'none'}
    candidate_graph.append(
        dbc.Col(id='plot-data-col-' + str(i), children=[
            dcc.Loading(id='plot-data-part-' + str(i), children=[
                dcc.Graph(
                        id='plot-data-' + str(i),
                        figure={'data': []},
                        # style={'display': 'none'}
                        )
            ], loading_state={'is_loading': False}, type='default')
        ], width=6, style={'display': 'none'})


    )
    candidate_data.append(
        dcc.Store(id='graph-data-' + str(i)),
    )


graph_plot = [
    dbc.CardHeader(html.H5("Bipartite Graph")),
    dbc.CardBody(
        [
            # html.Div([
            dbc.Row([
                html.Div([
                    dcc.Store(id='graph-data'),

                    dcc.Store(id='initial-data'),

                    # ] + candidate_data,
                ] + candidate_data,),

                dbc.Col(
                    id="first-graph-col", children=[
                        dcc.Loading(
                            children=[
                                dcc.Graph(id="my-graph",
                                          style={'display': 'none'},
                                          figure={"data": [], }
                                          ),
                            ],
                            loading_state={'is_loading': False},
                            type='default', style={'width': '100%'}),
                    ], width=12, ),


            ] + candidate_graph,
                justify='start',
                style={'width': "100%", }),

        ],
    ),
]

data_plot = [

    dbc.CardBody(
        [
            dbc.Row([
                dbc.Col(
                    html.Div([

                        dcc.Graph(
                            id='degree-graph',
                            figure={'data': []},

                        ),
                    ], style={'width': '400px'})

                ),
                dbc.Col(
                    html.Div([
                        dcc.Graph(
                            id='tag-cloud',
                            figure={'data': []},
                        ),
                    ], style={'width': '600px'})

                )
            ]),
            dbc.Row([
                # dbc.Col(
                    html.Div(
                        id='authortable',
                        style={'width': '45%',
                               'marginRight': 35, 'marginLeft': 35},
                    ),
                    # ),
                    # dbc.Col(
                    html.Div(
                        id='papertable',
                        style={'width': '45%'},
                    ),
                    # ),

                    ])
        ]
    )
]

buf_count_col = [
    dbc.Card(
        [
            dbc.CardHeader(html.H5('Bipartite clustering coefficient')),
            dbc.CardBody(
                id='bcc_count',
                children=[
                    html.H5(''),
                ]),
        ],
        style={'marginBottom': 40},
    ),
    dbc.Card(
        [
            dbc.CardHeader(html.H5('No. of Butterflies')),
            dbc.CardBody(
                id='butterfly_count',
                children=[
                    html.H5(''),
                ]),
        ],
        style={'marginBottom': 45},
    ),

]


# app.layout = html.Div(children=[
#     body])
app.layout = html.Div(
    children=[
        dbc.Row([
            dbc.Col(Left_col, width=2),
            dbc.Col(dbc.Card(graph_plot), width=7),
            dbc.Col(buf_count_col, width=2)
        ], style={"marginTop": 30, "marginBottom": 30, }, justify="center"),
        dbc.Container([
            dbc.Card(data_plot, id='data_part',
                     style={'visibility': 'hidden'}),
        ])

    ]
)


@app.callback(Output('data_part', 'style'),
              [Input('graph-data', 'data')])
def update_card(data):
    if data is None:
        raise PreventUpdate

    return {'visibility': 'visible'}

@app.callback(Output('bitruss_value', 'children'),
              [Input('wing-number', 'value')])
def update_card(data):
    if data is None:
        raise PreventUpdate

    return html.Label(data, className="lead", style={'marginLeft': '16px'},)


@app.callback(Output('datatable-upload-container', 'data'),
              [Input('datatable-upload', 'filename'),
               Input('datatable-upload', 'contents')],
              [State('datatable-upload', 'last_modified')])
def update_output(uploaded_filenames, uploaded_file_contents, last_modified):
    global New_File
    New_File = True

    if uploaded_file_contents is not None:
        data = uploaded_file_contents[0].encode("utf8").split(b";base64,")[1]
        delete_all(meta, engine)
        delete_files()
        with open('./read_file/'+uploaded_filenames[0], "wb") as fp:
            fp.write(base64.decodebytes(data))

        data = base64.decodebytes(data).decode("utf-8")
        # return [{'processed_data':process_data(data,num_nodes,uploaded_filenames[0],meta,engine)}]
        # read_xml_to_db(data,meta,engine)
        name = './read_file/'+uploaded_filenames[0]
        process_data(data, name, meta, engine)
        return [{'data': 'done'}]

    raise PreventUpdate


@app.callback(
    Output('bitruss-section', 'style'),
    [Input('select-bitruss-abcore', 'value')]
)
def display_bitruss_section(select_model):
    if select_model is None:
        raise PreventUpdate
    if select_model == 2:
        return {'display': 'None'}


@app.callback(
    Output('abcore-section', 'style'),
    [Input('select-bitruss-abcore', 'value')]
)
def display_abcore_section(select_model):
    if select_model is None:
        raise PreventUpdate
    if select_model == 1:
        return {'display': 'None'}


@app.callback(Output('my-graph', 'style'),
              [Input('my-graph', 'figure')],
              [State('graph-data-0', 'data')]
              )
def update_style(figure, graph_data_0):

    if figure == {}:
        return {'display': 'none'}
    if figure['data'] == []:
        return {'display': 'none'}
    # return {'display':'block'}
    # if data_0 is not None:
    #     if "compare" in data_0.keys() and data_0['compare'] is True:
    #         return {'width': '50%'}

    # if 'compare' in graph_data_0.keys() and graph_data_0['compare'] == False:
    #     return {'width': '100%'}

    return {'width': '100%'}


# @app.callback(
#     Output('graph-data-0', 'data'),
#     [Input('if_compare', 'value')],
#     [State('graph-data', 'data')]
# )
# def store_graph_1(value, data):
#     if value is None or data is None:
#         raise PreventUpdate
#     if value == [1]:
#         data['compare'] = True
#         return data
#     raise PreventUpdate


@app.callback(
    Output('compare_graph_no_section', 'style'),
    [Input('if_compare', 'value')]
)
def show_graph_no(compare_value):
    if compare_value is None:
        raise PreventUpdate
    if compare_value == [] or compare_value == 0:
        return {'display': 'none'}
    if compare_value == [1]:
        return {}
    raise PreventUpdate


@app.callback(
    Output('if_compare', 'value'),
    [Input('initial-data', 'data')]
)
def set_if_compare(data):
    if data is None:
        raise PreventUpdate
    return 0


@app.callback(Output('wing-number', 'disabled'),
              [Input('my-graph', 'figure'),
               Input('plot-data-0', 'figure'),
               Input('select-bitruss-abcore', 'value')])
def update_wing_number_style(figure, figure_0, select_model):
    if figure == {} and figure_0 == {}:
        return True
    # if select_model == 2:
    #     return True
    # # if figure['data'] == []:
    # #     return True
    # return False


@app.callback(
    Output('compare_section', 'style'),
    [Input('initial-data', 'data')]
)
def show_compare_section(data):
    if data is None:
        raise PreventUpdate
    return {}


@app.callback(Output('my-graph', 'figure'),
              #   [Input('initial-data','data'),
              [Input('graph-data', 'data'), ],
              [State('select-upload-data-type', 'data'), ]
              )
def display_figure(graph_data, back_data):
    global New_File
    global Trigger_compare
    if Trigger_compare:
        Trigger_compare = False

        raise PreventUpdate

    data = None
    if graph_data is not None:
        data = graph_data

    if data is None:
        raise PreventUpdate

    icon = False
    if back_data['select_type'] == 'author-paper':
        icon = True

    # print(graph_data['left'])
    if len(graph_data['left']) == 0 or len(graph_data['right']) == 0 or len(graph_data['edges']) == 0:
        s = go.Scatter(x=[0, 1, ], y=[0, 1, ],
                       mode='markers', marker_color='white')
        return {
            'data': [s],
            'layout': {
                'annotations': [
                    dict(
                        x=5,
                        y=5,
                        xref='x',
                        yref='y',
                        text="No such graph exists",
                        showarrow=False,
                        font=dict(size=20),
                    )
                ],
                'xaxis': {
                    'range': [0, 10],
                    'fixedrange': True,
                    'showgrid': False,
                    'zeroline': False,
                    'showticklabels': False
                },
                'yaxis': {
                    'range': [0, 10],
                    'fixedrange': True,
                    'showgrid': False,
                    'zeroline': False,
                    'showticklabels': False
                }
            }
        }

    graph = construct_graph_db(graph_data['left'], graph_data['right'],
                               graph_data['edges'], meta, engine, graph_data['color_list'], 1, 2, icon)
    return graph


# @app.callback(Output('input-box', 'value'),
#               [Input('initial-data', 'data'), ],
#               )
# def change_input_box(data):
#     if data is None:
#         raise PreventUpdate
#     return ""

@app.callback(Output('input-box', 'value'),
              [Input('initial-data', 'data'),
               Input('compare-value-data', 'data'),
               ],
              [State('graph-data', 'data'),
               State('graph-data-0', 'data'), ])
def change_input_box(data, compare_data, graph_data, graph_data_0, ):
    global New_File

    if compare_data is not None and graph_data is not None and not New_File:

        if compare_data['compare'] == 1:
            if graph_data['node'] == None:
                return ""
            return graph_data['node']

        if compare_data['compare'] == 2:
            if 'node' in graph_data_0 and graph_data_0['node'] != None:
                return graph_data_0['node']
            else:
                return ""

    raise PreventUpdate


@app.callback(Output('wing-number', 'max'),
              [Input('initial-data', 'data'),
               Input('select-bitruss-abcore', 'value')])
# Input('graph-data','data')])
def change_max_wing_number(data, select_model):
    if data is None:
        raise PreventUpdate
    if 'max_wing' not in data.keys():
        raise PreventUpdate

    return data['max_wing']


@app.callback(Output('wing-number', 'marks'),
              [Input('initial-data', 'data'), ])
def display_wing_number(data):
    if data is None:
        raise PreventUpdate
    if 'max_wing' not in data.keys():
        raise PreventUpdate

    max_wing = data['max_wing']
    if max_wing < 5:
        return {i: '{}'.format(i) for i in range(data['max_wing']+1)}
    interval = (int)(max_wing/5)
    result = {i*interval: '{}'.format(i*interval) for i in range(5)}
    result[max_wing] = str(max_wing)
    return result


@app.callback(
    Output('compare_graph_no', 'value'),
    [Input('current-upload-data', 'data'),
     Input('if_compare', 'value')]
)
def reset_compare_graph_no(data, if_compare):
    if data is not None and data['result'] is not None:
        return 1
    if if_compare is not None and (if_compare == 0 or if_compare == []):
        return 1
    raise PreventUpdate


@app.callback(Output('wing-number', 'value'),
              [Input('initial-data', 'data'),
               Input('compare_graph_no', 'value'),
               Input('select-bitruss-abcore', 'value')],
              [State('graph-data', 'data'),
               State('graph-data-0', 'data'),
               State('if_compare', 'value')])
def display_max_wing_number(data, compare_no, select_model, graph_data, graph_data_0, if_compare):
    global New_File

    if compare_no is not None and graph_data is not None and not New_File:
        if compare_no == 1 or if_compare == [] or if_compare == 0:
            return graph_data['wing_number']

        if compare_no == 2:
            if 'wing_number' in graph_data_0.keys():
                return graph_data_0['wing_number']

    if data is None:
        raise PreventUpdate

    if 'max_wing' not in data.keys():
        raise PreventUpdate

    return data['max_wing']


@app.callback(Output('tag-cloud', 'figure'),
              [Input('graph-data', 'data'),
               Input('graph-data-0', 'data'),
               Input('compare_graph_no', 'value')],
              [State('if_compare', 'value')]
              )
def generate_tag_cloud(graph_data, graph_data_0, compare_no, if_compare):
    data = graph_data

    if data is None:
        raise PreventUpdate

    if not (if_compare == [] or if_compare == 0):
        if compare_no is not None and compare_no == 2:
            data = graph_data_0

    if data['right'] == []:
        return {
            'data': [],
            'layout': go.Layout(
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
                    },
                    "margin": dict(t=20, b=20, l=10, r=10, pad=4),
                    "hovermode": "closest",
                }
            )
        }

    # name = get_node_list_name(data['right'], meta, engine)
    name = get_right_node_list_name(data['right'], meta, engine)
    text = " ".join(name.values())
    text = ''.join([i for i in text if i.isalpha() or i == " "])
    words = text.split()
    counter = Counter(words)
    most = counter.most_common(100)
    words = ' '.join([i[0] for i in most])

    return generate_word_cloud(words)


@app.callback(Output('degree-graph', 'figure'),
              [Input('graph-data', 'data'),
               Input('graph-data-0', 'data'),
               Input('compare_graph_no', 'value')],
              [State('if_compare', 'value'), ]
              )
def degree_plot(graph_data, graph_data_0, compare_no, if_compare):
    data = graph_data

    if data is None:
        raise PreventUpdate

    if not (if_compare == [] or if_compare == 0):
        if compare_no is not None and compare_no == 2:
            data = graph_data_0

    y = degree_calculate(data['left'], data['right'], data['edges'])

    layout = go.Layout(

        title={'text': 'Degree',
               'font': {'size': 20}
               },
    )
    y = [round(i, 3) for i in y]

    fig = go.Figure([go.Bar(x=['avg', 'max', 'min'], y=y, text=y,
                            textposition='auto', hoverinfo='text', hovertext=[]), ], layout=layout)
    return fig


@app.callback(Output('authortable', 'children'),
              [Input('graph-data', 'data'),
               Input('graph-data-0', 'data'),
               Input('compare_graph_no', 'value')],
              [State('if_compare', 'value'),
               State('select-upload-data-type', 'data')]
              )
def generate_datatable(graph_data, graph_data_0, compare_no, if_compare, select_data):
    data = graph_data

    title = 'Author'

    if data is None:
        raise PreventUpdate

    if not (if_compare == [] or if_compare == 0):
        if compare_no is not None and compare_no == 2:
            data = graph_data_0

    if select_data['select_type'] != 'author-paper':
        title = 'Left'
    if select_data['select_type'] == 'user-movie':
        title = "User"

    node_data = generate_author_table(
        data['left'], data['right'], data['edges'], meta, engine)

    return dash_table.DataTable(
        id='author_table',
        style_data={
            'whiteSpace': 'normal',
        },
        columns=[{'name': 'ID', 'id': 'ID'}, {'name': title,
                                              'id': 'Author'}, {'name': 'Degree', 'id': 'Degree'}],
        data=node_data,
        fixed_rows={'headers': True},
        style_cell={
            'overflow': 'hidden',
            'textOverflow': 'ellipsis',
            'maxWidth': '450px',
            'textAlign': 'center',
        },
        style_table={
            # 'minwidth':'450',
            'maxHeight': '500px',
            'overflowY': 'scroll',
        },
        sort_action='native',
        style_cell_conditional=[
                    {
                        'if': {'column_id': 'Degree'},
                        'width': '80px',
                    },
            {
                        'if': {'column_id': 'ID'},
                        'width': '60px',
                    },
        ],
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },

    )


@app.callback(Output('papertable', 'children'),
              [Input('graph-data', 'data'),
               Input('graph-data-0', 'data'),
               Input('compare_graph_no', 'value')],
              [State('if_compare', 'value'),
               State('select-upload-data-type', 'data')])
def generate_datatable(graph_data, graph_data_0, compare_no, if_compare, select_data):
    data = graph_data

    if data is None:
        raise PreventUpdate

    title = 'Paper'
    if not (if_compare == [] or if_compare == 0):
        if compare_no is not None and compare_no == 2:
            data = graph_data_0

    if select_data['select_type'] != 'author-paper':
        title = 'Right'
    if select_data['select_type'] == 'user-movie':
        title = "Movie"

    node_data = generate_paper_table(
        data['left'], data['right'], data['edges'], meta, engine)

    return dash_table.DataTable(
        # id = 'paper_table',

        style_data={
            'whiteSpace': 'normal',
            # 'height': 'auto',
        },
        columns=[{'name': 'ID', 'id': 'ID'}, {'name': title,
                                              'id': 'Paper'}, {'name': 'Degree', 'id': 'Degree'}],
        data=node_data,

        style_cell={
            'maxWidth': '200px',
            'textAlign': 'center',
        },

        style_table={
            'maxHeight': '500px',
            'overflowY': 'scroll',
        },

        sort_action='native',
        fixed_rows={'headers': True},
        style_cell_conditional=[
            {
                'if': {'column_id': 'Degree'},
                'width': '80px',
            },
            {
                'if': {'column_id': 'ID'},
                'width': '60px',
            },
        ],
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': 'rgb(248, 248, 248)'
            }
        ],
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
    )


@app.callback(Output('butterfly_count', 'children'),
              [Input('graph-data', 'data'),
               Input('graph-data-0', 'data'),
               Input('compare_graph_no', 'value')],
              [State('if_compare', 'value')])
def display_butterfly_count(graph_data, graph_data_0, compare_no, if_compare):
    data = graph_data

    if data is None:
        raise PreventUpdate

    if not (if_compare == [] or if_compare == 0):
        if compare_no is not None:
            if compare_no == 2:
                data = graph_data_0

    c = 0
    if 'bf_count' in data.keys():
        c = data['bf_count']

    return html.H5(str(c))


@app.callback(Output('bcc_count', 'children'),
              [Input('graph-data', 'data'),
               Input('graph-data-0', 'data'),
               Input('compare_graph_no', 'value')],
              [State('if_compare', 'value')])
def display_butterfly_count(graph_data, graph_data_0, compare_no, if_compare):
    data = graph_data

    if data is None:
        raise PreventUpdate

    if not (if_compare == [] or if_compare == 0):
        if compare_no is not None:
            if compare_no == 2:
                data = graph_data_0

    c = 0
    if 'bcc_count' in data.keys():
        c = data['bcc_count']
    c = round(c, 3)
    return html.H5(str(c))


@app.callback(Output('initial-data', 'data'),
              [Input('datatable-upload-container', 'data'),
               Input("current-upload-data", "data")])
def initial_graph(data, modal_data):
    if data is None and modal_data is None:
        raise PreventUpdate
    if modal_data['result'] == None:
        raise PreventUpdate
    global Exisiting_Graph
    global New_File
    global color_list
    global prev_wing_no

    graph_data = {}

    max_wing = get_max_hier(meta, engine)
    graph_data['max_wing'] = max_wing

    Exisiting_Graph = True
    color_list = colors(max_wing+1)
    graph_data['color_list'] = color_list
    prev_wing_no = graph_data['max_wing']
    # graph_data['max_alpha'] = get_max_alpha(meta, engine)
    # graph_data['max_beta'] = get_max_beta(meta, engine)

    return graph_data


@app.callback(Output('graph-data', 'data'),
              [
              Input('input-box', 'value'),
              Input('wing-number', 'value'),
              Input('alpha', 'value'),
              Input('beta', 'value'),
              Input('if_compare', 'value'),
              Input('compare_graph_no', 'value'),
              Input('select-bitruss-abcore', 'value')],
              [State('graph-data', 'data')])
def display_graph(node_value, wing_number, alpha, beta, if_compare, compare_graph_no, select_model, g_data):
    global Exisiting_Graph
    global New_File
    global color_list
    global prev_wing_no
    g = None

    if alpha is not None and beta is not None:
        alpha = int(alpha)
        beta = int(beta)

    compare = False
    if if_compare is not None and if_compare == [1]:
        compare = True

    if compare and compare_graph_no is not None and compare_graph_no == 2 and not New_File:
        raise PreventUpdate

    input_data = {
        'meta': meta,
        'engine': engine,
        'node': node_value,
        'wing_number': wing_number,
        'color_list': color_list,
        'alpha': alpha,
        'beta': beta,

        'compare': compare,

        'max_alpha': None,
        'max_beta': None,

        'alpha_change': False,
        'beta_change': False,
        'node_change': False,
        'wing_number_change': False,
        'model': select_model,
    }

    if New_File is False:
        if g_data != None:
            if 'alpha' in g_data.keys() and g_data['alpha'] != alpha:
                input_data['alpha_change'] = True
            if 'beta' in g_data.keys() and g_data['beta'] != beta:
                input_data['beta_change'] = True
            if 'wing_number' in g_data.keys() and g_data['wing_number'] != wing_number:
                input_data['wing_number_change'] = True
            if 'node' in g_data.keys() and g_data['node'] != node_value:
                input_data['node_change'] = True
            if 'max_alpha' in g_data.keys():
                input_data['max_alpha'] = g_data['max_alpha']
            if 'max_beta' in g_data.keys():
                input_data['max_beta'] = g_data['max_beta']
        else:
            input_data['alpha_change'] = True
            input_data['beta_change'] = True
            input_data['wing_number_change'] = True
            input_data['node_change'] = True

    if Exisiting_Graph:
        graph_data = wing_node_select(input_data)
        if graph_data is None:
            New_File = False

            raise PreventUpdate

        if New_File:
            input_data['max_alpha'], input_data['max_beta'] = get_total_max_alpha_beta(
                meta, engine)

        added = input_data.copy()
        added.pop('meta', None)
        added.pop('engine', None)
        graph_data.update(added)

        bf, bcc = count_butterfly(
            graph_data['left'], graph_data['right'], graph_data['edges'])

        graph_data['bf_count'] = bf
        graph_data['bcc_count'] = bcc
        # graph_data['bf_count'] = 1
        # graph_data['bcc_count'] = 2
        New_File = False
        return graph_data

    New_File = False

    raise PreventUpdate


@app.callback(Output('graph-data-0', 'data'),
              [
              Input('input-box', 'value'),
              Input('wing-number', 'value'),
              Input('alpha', 'value'),
              Input('beta', 'value'),
              Input('if_compare', 'value'),
              Input('compare_graph_no', 'value'),
              Input('select-bitruss-abcore', 'value')],
              [State('graph-data-0', 'data'),
               State('graph-data', 'data')])
def display_graph(node_value, wing_number, alpha, beta, if_compare, compare_graph_no, select_model, g_data, data):
    global Exisiting_Graph
    global New_File
    global color_list
    global prev_wing_no
    global First_compare_0
    g = None

    if alpha is not None and beta is not None:
        alpha = int(alpha)
        beta = int(beta)

    if if_compare == [] or if_compare == 0:
        return {'compare': False}

    # just trigger the compare
    if g_data == {'compare': False} and if_compare == [1]:
        data['compare'] = True
        First_compare_0 = True
        return data

    if g_data is None and if_compare == [1]:
        data['compare'] = True
        First_compare_0 = True
        return data

    compare = False
    if if_compare is not None and if_compare == [1]:
        compare = True

    if compare and compare_graph_no is not None and compare_graph_no == 1:
        raise PreventUpdate

    input_data = {
        'meta': meta,
        'engine': engine,
        'node': node_value,
        'wing_number': wing_number,
        'color_list': color_list,
        'alpha': alpha,
        'beta': beta,

        'compare': compare,

        'max_alpha': data['max_alpha'],
        'max_beta': data['max_beta'],

        'alpha_change': False,
        'beta_change': False,
        'node_change': False,
        'wing_number_change': False,
        'model': select_model,
    }

    if g_data != None:
        if 'alpha' in g_data.keys() and g_data['alpha'] != alpha:
            input_data['alpha_change'] = True
        if 'beta' in g_data.keys() and g_data['beta'] != beta:
            input_data['beta_change'] = True
        if 'wing_number' in g_data.keys() and g_data['wing_number'] != wing_number:
            input_data['wing_number_change'] = True
        if 'node' in g_data.keys() and g_data['node'] != node_value:
            input_data['node_change'] = True
        if 'max_alpha' in g_data.keys():
            input_data['max_alpha'] = g_data['max_alpha']
        if 'max_beta' in g_data.keys():
            input_data['max_beta'] = g_data['max_beta']
    else:
        input_data['alpha_change'] = True
        input_data['beta_change'] = True
        input_data['wing_number_change'] = True
        input_data['node_change'] = True

    if Exisiting_Graph:
        graph_data = wing_node_select(input_data)
        if graph_data is None:
            raise PreventUpdate

        added = input_data.copy()
        added.pop('meta', None)
        added.pop('engine', None)
        graph_data.update(added)

        bf, bcc = count_butterfly(
            graph_data['left'], graph_data['right'], graph_data['edges'])

        graph_data['bf_count'] = bf
        graph_data['bcc_count'] = bcc

        return graph_data

    raise PreventUpdate
################# compare graphs #######################


@app.callback(
    Output('plot-data-0', 'style'),
    [Input('if_compare', 'value'), ]
)
def turn_off_plot_data_0(if_compare):
    if if_compare == [] or if_compare == 0:
        return {'display': 'none'}
    return {}


@app.callback(
    # Output('plot-data-0', 'style'),
    Output('plot-data-col-0', 'style'),
    # [Input('graph-data-0', 'data')],
    [Input('graph-data-0', 'data'),
     Input('if_compare', 'value'),
     Input('first-graph-col', 'width')],
)
def show_compare_graph(data, if_compare, width):
    # def show_compare_graph(data):
    if if_compare == 0 or if_compare == []:
        return {'display': 'none'}

    if "compare" in data.keys() and data['compare'] is True:
        return {"width": '100%'}

    return {'display': 'none'}


@app.callback(
    Output('plot-data-0', 'figure'),
    [Input('graph-data-0', 'data'), ],
    [State('select-upload-data-type', 'data'),
     State('compare-value-data', 'data')]
)
def display_figure_1(graph_data, back_data, compare_data):
    global New_File
    global Trigger_compare_0
    global First_compare_0
    if Trigger_compare_0 and not First_compare_0:
        Trigger_compare_0 = False
        raise PreventUpdate

    if graph_data is None:
        raise PreventUpdate

    if 'compare' in graph_data.keys() and graph_data['compare'] is False:
        raise PreventUpdate

    icon = False
    if back_data['select_type'] == 'author-paper':
        icon = True
    First_compare_0 = False

    if len(graph_data['left']) == 0 or len(graph_data['right']) == 0 or len(graph_data['edges']) == 0:
        s = go.Scatter(x=[0, 1, ], y=[0, 1, ],
                       mode='markers', marker_color='white')
        return {
            'data': [s],
            'layout': {
                'annotations': [
                    dict(
                        x=5,
                        y=5,
                        xref='x',
                        yref='y',
                        text="No such graph exists",
                        showarrow=False,
                        font=dict(size=20),
                    )
                ],
                'xaxis': {
                    'range': [0, 10],
                    'fixedrange': True,
                    'showgrid': False,
                    'zeroline': False,
                    'showticklabels': False
                },
                'yaxis': {
                    'range': [0, 10],
                    'fixedrange': True,
                    'showgrid': False,
                    'zeroline': False,
                    'showticklabels': False
                }
            }
        }

    graph = construct_graph_db(graph_data['left'], graph_data['right'],
                               graph_data['edges'], meta, engine, graph_data['color_list'], 1, 2, icon)
    return graph


@app.callback(
    Output('plot-data-col-0', 'width'),
    [Input('first-graph-col', 'width')],
)
def change_col_0(width):
    # if "compare" in data.keys() and data['compare'] is True:
    #     return 6
    # print("change something", style)
    # if style != {'display': 'none'}:
        # return {'width': '48%', 'display': 'inline-block'}
        #     print("width is 6 rn")
        # return 6
    # raise PreventUpdate
    if width == 6:
        return 6


@app.callback(
    Output('first-graph-col', 'width'),
    [Input('if_compare', 'value'), ]
    #  Input('plot-data-col-0', 'style')],
)
def change_col_first(if_compare):
    # if "compare" in data.keys() and data['compare'] is True:
    #     return 6
    # if 'compare' in data.keys() and data['compare'] == False:
    #     return 12
    if (if_compare == [] or if_compare == 0):
        return 12
        # return {'width': '100%'}
    if if_compare == [1]:
        return 6
        # return {'width': '48%', 'display': 'inline-block'}

    raise PreventUpdate

########################## alpha-beta-core ############


@app.callback(
    Output('alpha', 'disabled'),
    [Input('my-graph', 'figure'),
     Input('plot-data-0', 'figure'),
     Input('select-bitruss-abcore', 'value')]
)
def update_alpha_slider(figure, figure_0, select_model):
    if figure == {} and figure_0 == {}:
        return True
    # if select_model == 1:
    #     return True
    # if figure['data'] == []:
    #     return True
    # return False


@app.callback(
    Output('beta', 'disabled'),
    [Input('my-graph', 'figure'),
     Input('plot-data-0', 'figure'),
     Input('select-bitruss-abcore', 'value')]
)
def update_beta_slider(figure, figure_0, select_model):
    if figure == {} and figure_0 == {}:
        return True
    # if select_model == 1:
    #     return True
    # if figure['data'] == []:
    #     return True
    # return False


@app.callback(
    Output('compare-value-data', 'data'),
    [Input('compare_graph_no', 'value'),
     Input('if_compare', 'value')],
    [State('compare-value-data', 'data')]
)
def store_compare_data(compare_no, if_compare, prev_comp_data):
    global New_File_compare
    if compare_no is None or if_compare is None:

        raise PreventUpdate

    if not New_File_compare:  # dont trigger change in the first time
        global Trigger_compare_alpha
        global Trigger_compare_beta
        global Trigger_compare_0
        global Trigger_compare
        global Trigger_select_value

        Trigger_compare_alpha = True
        Trigger_compare_beta = True

        if if_compare == [1]:
            Trigger_compare = True
            Trigger_compare_0 = True
        Trigger_select_value = True
    else:
        New_File_compare = False
        return {'compare': 1, "if_compare": if_compare}

    # if prev_comp_data is not None:
    #     if prev_comp_data['if_compare'] == [] or prev_comp_data['if_compare'] == 0 and if_compare == [1]:
    #         global
    # compare_value = 0
    if if_compare == [] or if_compare == 0 or compare_no == 1:
        return {'compare': 1, "if_compare": if_compare}

    if compare_no == 2:
        return {'compare': 2, "if_compare": if_compare}

    raise PreventUpdate


@app.callback(
    Output('alpha', 'value'),
    [
        Input('compare-value-data', 'data'),
        Input('select-bitruss-abcore', 'value')],
    [State('graph-data', 'data'),
     State('graph-data-0', 'data')]
)
def reset_alpha_value(compare_data, select_value, graph_data, graph_data_0):
    if graph_data is None:
        raise PreventUpdate

    data = graph_data

    global Trigger_compare_alpha
    if Trigger_compare_alpha:
        Trigger_compare_alpha = False
        if compare_data['compare'] == 1:
            return graph_data['alpha']
        if compare_data['compare'] == 2:
            if 'alpha' in graph_data_0.keys():
                return graph_data_0['alpha']

    if compare_data['compare'] == 2:
        data = graph_data_0

    if select_value == 1:
        return 0

    if select_value == 2:
        if data['max_alpha'] > data['max_beta']:
            return data['max_alpha']

    return 0


@app.callback(Output('alpha', 'max'),
              [Input('initial-data', 'data'),
               Input('my-graph', 'figure'),
               Input('plot-data-0', 'figure'),
               Input('compare_graph_no', 'value')],
              [State('graph-data', 'data'),
               State('graph-data-0', 'data'),
               State('if_compare', 'value')])
def change_max_alpha(initial_data, figure, figure_0, compare_no, graph_data, graph_data_0, if_compare):
    data = graph_data
    if data is None:
        raise PreventUpdate

    if not (if_compare == [] or if_compare == 0):
        if compare_no is not None:
            if compare_no == 2:
                data = graph_data_0

    # if data['wing_number_change'] or data['node_change']:

    return data['max_alpha']
    # raise PreventUpdate


@app.callback(Output('beta', 'max'),
              [Input('initial-data', 'data'),
               Input('my-graph', 'figure'),
               Input('plot-data-0', 'figure'),
               Input('compare_graph_no', 'value')],
              [State('graph-data', 'data'),
               State('graph-data-0', 'data'),
               State('if_compare', 'value')])
def change_max_alpha(initial_data, figure, figure_0, compare_no, graph_data, graph_data_0, if_compare):
    data = graph_data
    if data is None:
        raise PreventUpdate

    if not (if_compare == [] or if_compare == 0):
        if compare_no is not None:
            if compare_no == 2:
                data = graph_data_0

    # if data['wing_number_change'] or data['node_change']:

    return data['max_beta']


@app.callback(
    Output('beta', 'value'),
    [
        Input('compare-value-data', 'data'),
        Input('select-bitruss-abcore', 'value')],
    [State('graph-data', 'data'),
     State('graph-data-0', 'data')]
)
def reset_beta_value(compare_data, select_value, graph_data, graph_data_0):
    if graph_data is None:
        raise PreventUpdate

    data = graph_data

    global Trigger_compare_beta
    if Trigger_compare_beta:
        Trigger_compare_beta = False
        if compare_data['compare'] == 1:

            return graph_data['beta']
        if compare_data['compare'] == 2:
            if 'beta' in graph_data_0.keys():

                return graph_data_0['beta']

    if compare_data['compare'] == 2:
        data = graph_data_0

    if select_value == 1:

        return 0

    if select_value == 2:

        if data['max_alpha'] < data['max_beta']:
            return data['max_beta']

    return 0


@app.callback(Output('alpha', 'marks'),
              [Input('alpha', 'max')])
def display_alpha_number(max_number):
    if max_number is not None:
        return process_slider_mark(max_number)
    raise PreventUpdate


@app.callback(Output('beta', 'marks'),
              [Input('beta', 'max')])
def display_beta_number(max_number):
    if max_number is not None:
        return process_slider_mark(max_number)
    raise PreventUpdate

@app.callback(Output('alpha_value', 'children'),
              [Input('alpha', 'value')])
def update_alpha_value(data):
    if data is None:
        raise PreventUpdate

    return html.P(data, style={'marginLeft': '16px'},)

@app.callback(Output('beta_value', 'children'),
              [Input('beta', 'value')])
def update_beta_value(data):
    if data is None:
        raise PreventUpdate

    return html.P(data, style={'marginLeft': '16px'},)

# select model


@app.callback(
    Output('select-bitruss-abcore', 'style'),
    [Input('my-graph', 'figure')]
)
def display_select_bitruss_abcore(figure):
    if figure is None or figure is {}:
        return {'display': 'None'}
    return {}

# global just_close_compare = False


@app.callback(
    Output('select-bitruss-abcore', 'value'),
    [Input('compare-value-data', 'data'), ],
    [State('if_compare', 'value'),
     State('graph-data', 'data'),
     State('graph-data-0', 'data')]
)
def select_bitruss_value_change(compare_data, if_compare, graph_data, graph_data_0):
    global Trigger_select_value

    data = graph_data
    if compare_data['compare'] == 2:
        data = graph_data_0

    if data is None:
        return 1

    if Trigger_select_value:
        Trigger_select_value = False
        if 'model' in data.keys():
            return data['model']
    return 1


def process_slider_mark(max_value):
    if max_value < 5:
        return {i: '{}'.format(i) for i in range(max_value+1)}
    interval = (int)(max_value/5)
    result = {i*interval: '{}'.format(i*interval) for i in range(5)}
    result[max_value] = str(max_value)
    return result


server = app.server


if __name__ == '__main__':
    app.run_server(debug=True)
