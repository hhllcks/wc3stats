import os
import random, threading, webbrowser
from .replay_handler import load_replay, get_statistics
from .stats_layouter import get_stats_layout, ALL_RACES, ALL_MAPS
from .callbacks import create_full_game_list_tab_callback, create_mainrace_tab_callback, create_total_tab_callback, create_race_tab_callback, create_map_tab_callback, create_race_tab_dropdown_callback, create_map_tab_dropdown_callback
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
import plotly.graph_objs as go
from flask import Flask
from dash import Dash
from dash.dependencies import Input, Output, State
from dotenv import load_dotenv
from .exceptions import ImproperlyConfigured

DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(DOTENV_PATH)

if "DYNO" in os.environ:
    # the app is on Heroku
    on_heroku = True
    multiple_files = False
else:
    on_heroku = False
    multiple_files = True
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(dotenv_path)

try:
   py.sign_in(os.environ["PLOTLY_USERNAME"], os.environ["PLOTLY_API_KEY"])
except KeyError:
   raise ImproperlyConfigured("Plotly credentials not set in .env")

app_name = "WC3 Stats"
server = Flask(app_name)

try:
    server.secret_key = os.environ["SECRET_KEY"]
except KeyError:
    raise ImproperlyConfigured("SECRET KEY not set in .env:")

metas = [
   {'name': 'viewport', 'content': 'width=device-width, initial-scale=1, shrink-to-fit=no'},
]
app = Dash(
    name=app_name, 
    server=server, 
    csrf_protect=False,
    meta_tags=metas,
)
# app.css.config.serve_locally = True
# app.scripts.config.serve_locally = True
app.config['suppress_callback_exceptions']=True
app.config['include_asset_files']=True
app.title = "WC3 Stats"

external_js = [
#     #"https://code.jquery.com/jquery-3.2.1.slim.min.js",
#     #"https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js",
#     #"https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"
]
external_css = [
#     # dash stylesheet
#     #"https://codepen.io/chriddyp/pen/bWLwgP.css",
#     "https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
#     "https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css",
]

theme = {"font-family": "Raleway", "background-color": "#e0e0e0"}

def create_header():
    header_style = {"background-color": theme["background-color"], "padding": "1.5rem"}
    header = html.Header(html.H3(children=app_name + " - Analyze your Warcraft 3 Replays", style=header_style))
    return header

def create_content():
    content = html.Div(
        children=[
            html.Div(
                id="input-container",
                children=[
                    html.Div(
                        children=[
                            #html.Label("Player Name", htmlFor="aliases"),
                            html.Small("Please enter name of the main player in the replays", className="form-text, text-muted"),
                            dcc.Input(id='aliases', value='', type='text', placeholder='',className="form-control"),
                        ],
                        className="form-group",
                    ),
                    dcc.Upload(
                        id='replayUpload',
                        children=html.Div([
                            'Drag and Drop or ', html.A('Select Replays')
                        ]),
                        accept='.w3g',
                        style={
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=multiple_files,
                        disabled=True,
                    ),
                    # html.Div(
                    #     id="confirm-content",
                    #     children=[
                    #         dcc.Markdown(id="upload-confirm-markdown"),
                    #         html.Button('Submit', id="upload-confirm-button"),
                    #     ],
                    # ),
                ],
                style={"margin-bottom": 20},
            ),
            html.Div(id='stats-container')
        ],
        id="content",
        style={"width": "100%", "height": "100%"},
    )
    return content

def serve_layout():
    layout = html.Div(
        children=[
            create_header(), 
            create_content()
        ],
        className="container-fluid",
    )
    return layout

# external files
for js in external_js:
    app.scripts.append_script({"external_url": js})
for css in external_css:
    app.css.append_css({"external_url": css})

# create layout
app.layout = serve_layout()

# callbacks
@app.callback(Output('replayUpload', 'disabled'),
              [Input('aliases', 'value')])
def update_upload(aliases):
    if aliases != '':
        return False
    else:
        return True


# @app.callback(Output('upload-confirm-markdown', 'children'),
#               [Input('replayUpload', 'filename')])
# def update_confirm_markdown(list_of_names):
#     if(list_of_names):
#         return [f' You are about to upload and analyse {len(list_of_names)} replays. This may take a while.']        

# @app.callback(Output('stats-container', 'children'),
#               [Input('upload-confirm-button', 'n_clicks')],
#               [State('aliases', 'value'),
#                State('replayUpload', 'contents'),
#                State('replayUpload', 'filename'),
#                State('replayUpload', 'last_modified')])

@app.callback(Output('stats-container', 'children'),
               [Input('replayUpload', 'contents'),
                Input('replayUpload', 'filename'),
                Input('replayUpload', 'last_modified')],
               [State('aliases', 'value')])

def update_output_div(list_of_contents, list_of_names, list_of_dates, aliases):
    # if(n_clicks > 0):
    if(list_of_names):
        replays = [load_replay(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        (stats, rep_list) = get_statistics(replays, [aliases])
        return get_stats_layout(stats, rep_list)

app.callback(Output('full-game-list-content', 'style'),
            [Input('tabs', 'value')])(
create_full_game_list_tab_callback())
for race in list(ALL_RACES.keys()):
    app.callback(Output(f'{race}-content', 'style'),
              [Input('tabs', 'value')])(
    create_mainrace_tab_callback(race))
    app.callback(Output(f'{race}-content-total', 'style'),
              [Input(f'{race}-tabs', 'value')])(
    create_total_tab_callback(race))
    app.callback(Output(f'{race}-content-race', 'style'),
              [Input(f'{race}-tabs', 'value')])(
    create_race_tab_callback(race))
    app.callback(Output(f'{race}-content-map', 'style'),
              [Input(f'{race}-tabs', 'value')])(
    create_map_tab_callback(race))
    for enemy_race in list(ALL_RACES.keys()):
        app.callback(Output(f'{race}-content-{enemy_race}', 'style'),
              [Input(f'{race}-race-dropdown', 'value')])(
        create_race_tab_dropdown_callback(enemy_race))

    for mapname in list(ALL_MAPS.keys()):
        app.callback(Output(f'{race}-content-{mapname}', 'style'),
              [Input(f'{race}-map-dropdown', 'value')])(
        create_map_tab_dropdown_callback(mapname))

def run():
    debug = False

    if debug == False and on_heroku == False:
        port = 5000 + random.randint(0, 999)
        url = f"http://127.0.0.1:{port}"
        threading.Timer(1.25, lambda: webbrowser.open(url) ).start()
    else:
        port = int(os.environ.get("PORT", 5000))
        url = f"http://127.0.0.1:{port}"

    app.run_server(debug=debug, port=port, threaded=True)

if __name__ == "__main__":
    run()