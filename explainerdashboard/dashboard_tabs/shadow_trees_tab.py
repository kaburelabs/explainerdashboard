__all__ = ['ShadowTreesTab']

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_table

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from .dashboard_methods import *


class ShadowTreesTab:
    def __init__(self, explainer, standalone=False, tab_id="shadow_trees", title='Shadow Trees',
                 round=2, **kwargs):
        self.explainer = explainer
        self.standalone = standalone
        self.tab_id = tab_id
        self.title = title

        self.round = round
        self.kwargs = kwargs

        if self.standalone:
            self.label_selector = TitleAndLabelSelector(explainer, title=title)
        
        
    def layout(self):
        return dbc.Container([
            self.label_selector.layout() if self.standalone else None,
            # need to add dummy to make callbacks on tab change work:
            html.Div(id='tabs') if self.standalone else None, 
            shadow_trees_layout(self.explainer, round=self.round)
        ], fluid=True)
        
    def register_callbacks(self, app):
        if self.standalone:
            self.label_selector.register_callbacks(app)
        shadow_trees_callbacks(self.explainer, app, round=self.round)


def shadow_trees_layout(explainer, round=2, **kwargs):
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2('Predictions of individual decision trees.'),
                dbc.Form(
                    [
                        dbc.FormGroup(
                            [
                                dbc.Label("Index", className="mr-2"),
                                dbc.Input(id='tree-input-index', 
                                            placeholder="Fill in index here...",
                                            debounce=True),
                            ],
                            className="mr-3",
                        ),
                        dbc.Button("Random Index", color="primary", id='tree-index-button'),
                    ], inline=True),
                dcc.Store(id='tree-index-store'),
                html.H4('(click on a prediction to see decision path)'),
               # dcc.Loading(id="loading-trees-graph", 
                           # children=[
                                dcc.Graph(id='tree-predictions-graph'),
                                #]),  
            ], width={"size": 8, "offset": 2})
        ]), 
        dbc.Row([
            dbc.Col([
                html.Label('Decision path in decision tree:'),
                dcc.Markdown(id='tree-basevalue'),
                dash_table.DataTable(
                    id='tree-predictions-table',
                    style_cell={'fontSize':20, 'font-family':'sans-serif'},
                ),
            ], width={"size": 6, "offset": 3})
        ]), 
        dbc.Row([
            dbc.Col([
                 dcc.Loading(id="loading-tree-svg-graph", 
                            children=[html.Img(id='dtreeviz-svg')])
            ])
            
        ])
    ],  fluid=True)


def shadow_trees_callbacks(explainer, app, round=2, **kwargs):
    @app.callback(
        [Output('tree-predictions-table', 'data'),
         Output('tree-predictions-table', 'columns')],
        [Input('tree-predictions-graph', 'clickData')],
         # Input('label-store', 'data')], #this causes issues for some reason, only on this tab??
        [State('tree-index-store', 'data'),
         State('tabs', 'value')])
    def display_tree_click_data(clickdata, idx, tab):
        if clickdata is not None and idx is not None:
            model = int(clickdata['points'][0]['text'].split('tree no ')[1].split(':')[0]) if clickdata is not None else 0
            _, _, shadowtree_df = explainer.shadowtree_df_summary(model, idx, round=round)
            columns = [{'id': c, 'name': c} for c in  shadowtree_df.columns.tolist()]
            return (shadowtree_df.to_dict('records'), columns)
        raise PreventUpdate

    @app.callback(
        Output('dtreeviz-svg', 'src'),
        [Input('tree-predictions-graph', 'clickData'),
         #Input('label-store', 'data')#this causes issues for some reason, only on this tab??
         ],
        [State('tree-index-store', 'data'),
         State('tabs', 'value')])
    def display_click_data(clickData, idx, tab):
        if clickData is not None and idx is not None and explainer.graphviz_available:
            model = int(clickData['points'][0]['text'].split('tree no ')[1].split(':')[0]) 
            svg_encoded = explainer.decision_path_encoded(model, idx)
            return svg_encoded
        return ""

    @app.callback(
        Output('tree-predictions-graph', 'figure'),
        [Input('tree-index-store', 'data'),
         Input('label-store', 'data'),
         Input('tree-predictions-graph', 'clickData')],
        [State('tabs', 'value')]
    )
<<<<<<< HEAD
    def update_tree_graph(index, pos_label, clickdata, tab):
=======
    def update_tree_graph(index, pos_label, tab):
        explainer.pos_label=pos_label
>>>>>>> 5c623f400e54fea25a04f60bcc9229b0cc2a17d8
        if index is not None:
            highlight_tree = int(clickdata['points'][0]['text'].split('tree no ')[1].split(':')[0]) if clickdata is not None else None
            return explainer.plot_trees(index, highlight_tree=highlight_tree, round=round)
        return {}

    @app.callback(
        Output('tree-index-store', 'data'),
        [Input('tree-input-index', 'value')],
        [State('tabs', 'value')]
    )
    def update_tree_index_store(index, tab):
        if (explainer.idxs is None 
            and str(index).isdigit() 
            and int(index) >= 0
            and int(index) <= len(explainer)):
            return int(index)
        if (explainer.idxs is not None and index in explainer.idxs):
            return index
        return None

    @app.callback(
        Output('tree-input-index', 'value'),
        [Input('tree-index-button', 'n_clicks')],
        [State('tabs', 'value')]
    )
    def update_tree_input_index(n_clicks, tab):
        return explainer.random_index(return_str=True)