import os
import replay_handler
import stats_layouter
import dash_core_components as dcc
import dash_html_components as html
import plotly.plotly as py
import plotly.graph_objs as go
from flask import Flask
from dash import Dash
from dash.dependencies import Input, Output, State
from dotenv import load_dotenv
from exceptions import ImproperlyConfigured

DOTENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(DOTENV_PATH)

if "DYNO" in os.environ:
    # the app is on Heroku
    debug = False
# google analytics with the tracking ID for this app
# external_js.append('https://codepen.io/jackdbd/pen/rYmdLN.js')
else:
    debug = True
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

app = Dash(name=app_name, server=server, csrf_protect=False)
app.config['suppress_callback_exceptions']=True
external_js = []

external_css = [
    # dash stylesheet
    "https://codepen.io/chriddyp/pen/bWLwgP.css",
    "https://fonts.googleapis.com/css?family=Raleway",
    "//maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css",
]

theme = {"font-family": "Raleway", "background-color": "#e0e0e0"}


def create_header():
    header_style = {"background-color": theme["background-color"], "padding": "1.5rem"}
    header = html.Header(html.H1(children=app_name, style=header_style))
    return header


def create_content():
    content = html.Div(
        children=[
            html.Div(
                id="input-container",
                children=[
                    dcc.Input(id='aliases', value='h3n', type='text', placeholder='Playername'),
                    dcc.Upload(
                        id='replayUpload',
                        children=html.Div([
                            'Drag and Drop or ', html.A('Select Replays')
                        ]),
                        style={
                            'width': '100%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderStyle': 'dashed',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                        # Allow multiple files to be uploaded
                        multiple=True,
                        disabled=True
                    )
                ],
                style={"margin-bottom": 20},
            ),
            html.Div(
                id='reset-container',
                children=[
                    html.Button('Reset', id='reset-button'),
                ],
                style={'display': 'none'}
            ),
            html.Div(id='stats-container')
        ],
        id="content",
        style={"width": "100%", "height": "100%"},
    )
    return content

def serve_layout():
    layout = html.Div(
        children=[create_header(), create_content()],
        className="container",
        style={"font-family": theme["font-family"]},
    )
    return layout


app.layout = serve_layout()
for js in external_js:
    app.scripts.append_script({"external_url": js})
for css in external_css:
    app.css.append_css({"external_url": css})


# callbacks
@app.callback(Output('replayUpload', 'disabled'),
              [Input('aliases', 'value')])
def update_upload(aliases):
    if aliases != '':
        return False
    else:
        return True

@app.callback(Output('stats-container', 'children'),
              [Input('aliases', 'value'),
               Input('replayUpload', 'contents'),
               Input('replayUpload', 'filename'),
               Input('replayUpload', 'last_modified')])

def update_output_div(aliases, list_of_contents, list_of_names, list_of_dates):
    if(list_of_names):
        replays = [replay_handler.load_replay(c, n, d) for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)]
        stats = replay_handler.get_statistics(replays, [aliases])
        return stats_layouter.get_stats_layout(stats)

@app.callback(Output('nightelf-content', 'style'),
              [Input('tabs', 'value')])
def render_content_nightelf(tab):
    if tab == 'nightelf':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('nightelf-content-total', 'style'),
              [Input('nightelf-tabs', 'value')])
def render_content_nightelf_total(tab):
    if tab == 'nightelf-tab-total':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('nightelf-content-race', 'style'),
              [Input('nightelf-tabs', 'value')])
def render_content_nightelf_race(tab):
    if tab == 'nightelf-tab-race':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('nightelf-content-map', 'style'),
              [Input('nightelf-tabs', 'value')])
def render_content_nightelf_map(tab):
    if tab == 'nightelf-tab-map':
        return {'display': 'block'}
    else:
        return {'display': 'none'}
        
@app.callback(Output('random-content', 'style'),
              [Input('tabs', 'value')])
def render_content_random(tab):
    if tab == 'random':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('random-content-total', 'style'),
              [Input('random-tabs', 'value')])
def render_content_random_total(tab):
    if tab == 'random-tab-total':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('random-content-race', 'style'),
              [Input('random-tabs', 'value')])
def render_content_random_race(tab):
    if tab == 'random-tab-race':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('random-content-map', 'style'),
              [Input('random-tabs', 'value')])
def render_content_random_map(tab):
    if tab == 'random-tab-map':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('orc-content', 'style'),
              [Input('tabs', 'value')])
def render_content_orc(tab):
    if tab == 'orc':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('orc-content-total', 'style'),
              [Input('orc-tabs', 'value')])
def render_content_orc_total(tab):
    if tab == 'orc-tab-total':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('orc-content-race', 'style'),
              [Input('orc-tabs', 'value')])
def render_content_orc_race(tab):
    if tab == 'orc-tab-race':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('orc-content-map', 'style'),
              [Input('orc-tabs', 'value')])
def render_content_orc_map(tab):
    if tab == 'orc-tab-map':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('human-content', 'style'),
              [Input('tabs', 'value')])
def render_content_human(tab):
    if tab == 'human':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('human-content-total', 'style'),
              [Input('human-tabs', 'value')])
def render_content_human_total(tab):
    if tab == 'human-tab-total':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('human-content-race', 'style'),
              [Input('human-tabs', 'value')])
def render_content_human_race(tab):
    if tab == 'human-tab-race':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('human-content-map', 'style'),
              [Input('human-tabs', 'value')])
def render_content_human_map(tab):
    if tab == 'human-tab-map':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('undead-content', 'style'),
              [Input('tabs', 'value')])
def render_content_undead(tab):
    if tab == 'undead':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('undead-content-total', 'style'),
              [Input('undead-tabs', 'value')])
def render_content_undead_total(tab):
    if tab == 'undead-tab-total':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('undead-content-race', 'style'),
              [Input('undead-tabs', 'value')])
def render_content_undead_race(tab):
    if tab == 'undead-tab-race':
        return {'display': 'block'}
    else:
        return {'display': 'none'}

@app.callback(Output('undead-content-map', 'style'),
              [Input('undead-tabs', 'value')])
def render_content_undead_map(tab):
    if tab == 'undead-tab-map':
        return {'display': 'block'}
    else:
        return {'display': 'none'}





# @app.callback(Output('input-container', 'style'), 
#               [Input('reset-button', 'n_clicks'),
#                Input('aliases', 'value'),
#                Input('replayUpload', 'contents'),
#                Input('replayUpload', 'filename'),
#                Input('replayUpload', 'last_modified')])
# def input_visibility(n_clicks, aliases, list_of_contents, list_of_names, list_of_dates):
#     if(list_of_names):
#         return {'display': 'none'}
#     if(n_clicks):
#         return {'display': 'block'}

# @app.callback(Output('reset-container', 'style'), 
#               [Input('reset-button', 'n_clicks'),
#                Input('aliases', 'value'),
#                Input('replayUpload', 'contents'),
#                Input('replayUpload', 'filename'),
#                Input('replayUpload', 'last_modified')])
# def reset_visibility(n_clicks, aliases, list_of_contents, list_of_names, list_of_dates):
#     if(list_of_names):
#         return {'display': 'block'}
#     if(n_clicks):
#         return {'display': 'none'}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run_server(debug=debug, port=port, threaded=True)
