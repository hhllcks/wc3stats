import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

# TODO remove hacky hack
import sys
from io import StringIO 

ALL_RACES = {
    'random': {
        'color': '#D6D6D6',
        'color_dark': '#C2C2C2',
        'color_light': '#EBEBEB',
    },
    'human': {
        'color': '#2727FF',
        'color_dark': '#0000F3',
        'color_light': '#5A5AFF',
    },
    'orc': {
        'color': '#228B22',
        'color_dark': '#186218',
        'color_light': '#2CB42C',
    },
    'undead': {
        'color': '#646464',
        'color_dark': '#515151',
        'color_light': '#787878',
    },
    'nightelf': {
        'color': '#800080',
        'color_dark': '#4D004D',
        'color_light': '#B300B3',
    },
}
WEEKDAYS = {
    '0': 'Monday',
    '1': 'Tuesday',
    '2': 'Wednesday',
    '3': 'Thursday',
    '4': 'Friday',
    '5': 'Saturday',
    '6': 'Sunday'
}

def get_stats_layout(stats):
    tabs = []
    content = [] 
    races = sorted(list(stats.keys()))
    if(len(races)>0):
        for race in races:
            tabs.append(
                dcc.Tab(label=race.title(), value=race)
            )
            content.append(
                html.Div(id=race + '-content', style={'display': 'none'},
                    children=get_race_content(stats[race], race)
                )
            )

        layout = html.Div([
            dcc.Tabs(id="tabs", value=races[0], children=tabs),
            html.Div(id='tabs-content',children=content)
        ])

    return layout

def get_race_content(stats, mainrace):
    content = [
        dcc.Tabs(id=mainrace + "-tabs", value=mainrace + "-tab-total", children=[
            dcc.Tab(label="Total", value=mainrace + "-tab-total"),
            dcc.Tab(label="By Enemy Race", value=mainrace + "-tab-race"),
            dcc.Tab(label="By Map", value=mainrace + "-tab-map"),
        ])
    ]
    content.append(html.Div(id=mainrace + "-content-total", children=[
        generate_table_by_race(stats, "race"),
        generate_table_by_map(stats, "map"),
        generate_hours(stats, 'graph-hours-total'),
        generate_days(stats, 'graph-days-total')
    ]))
    content_race = []
    for race in list(ALL_RACES.keys()):
        if(race in stats['race']):
            content_race.append(html.Div(id=mainrace + "-content-" + race, children=[
                html.Header(html.H1(children=race.title())),
                generate_table_by_map(stats['race'][race], "maps"),
                generate_hours(stats['race'][race], 'graph-hours-' + race),
                generate_days(stats['race'][race], 'graph-days-' + race)
            ]))

    content.append(html.Div(id=mainrace+"-content-race", children=content_race))

    content_map = []
    for mapname in stats['map']:
        content_map.append(html.Div(id=mainrace + "-content-" + mapname, children=[
            html.Header(html.H1(children=mapname)),
            generate_table_by_race(stats['map'][mapname], "enemy_races"),
            generate_hours(stats['map'][mapname], 'graph-hours-' + mapname),
            generate_days(stats['map'][mapname], 'graph-days-' + mapname)
        ]))

    content.append(html.Div(id=mainrace+"-content-map", children=content_map))

    return content

def generate_table_by_race(stats, racekey):
    header = [html.Tr([
        html.Th('vs'),
        html.Th('Wins'),
        html.Th('Losses'),
        html.Th('Win %'),
        html.Th('Avg. Length'),
        html.Th('Avg. APM')
    ])]
    body = []

    for race in list(ALL_RACES.keys()):
        if(race in stats[racekey]):
            style = {
                'background-color':ALL_RACES[race]['color_light'],
                'padding': 1,
            }
            body.append(html.Tr([
                html.Td(race.title(),style=style),
                html.Td(stats[racekey][race]['w'],style=style),
                html.Td(stats[racekey][race]['l'],style=style),
                html.Td(f"{stats[racekey][race]['p']:.2%}",style=style),
                html.Td(stats[racekey][race]['avg_length'],style=style),
                html.Td(stats[racekey][race]['apm'],style=style),
            ]))

    style = {
        'padding': 1,
    }
    body.append(html.Tr([
        html.Td('Total',style=style),
        html.Td(stats['w'],style=style),
        html.Td(stats['l'],style=style),
        html.Td(f"{stats['p']:.2%}",style=style),
        html.Td(stats['avg_length'],style=style),
        html.Td(stats['apm'],style=style),
    ]))

    return html.Table(header+body,
        style={
            "margin-bottom": 20,
            "padding": 2},
    )

def generate_table_by_map(stats, mapkey):
    header = [html.Tr([
        html.Th('Map'),
        html.Th('Wins'),
        html.Th('Losses'),
        html.Th('Win %'),
        html.Th('Avg. Length'),
        html.Th('Avg. APM'),

    ])]
    body = []
    style = {
        'padding': 1,
    }

    for mapname in list(stats[mapkey].keys()):
        body.append(html.Tr([
            html.Td(mapname, style=style),
            html.Td(stats[mapkey][mapname]['w'], style=style),
            html.Td(stats[mapkey][mapname]['l'], style=style),
            html.Td(f'{stats[mapkey][mapname]["p"]:.2%}', style=style),
            html.Td(stats[mapkey][mapname]['avg_length'], style=style),
            html.Td(stats[mapkey][mapname]['apm'], style=style),
        ]))

    body.append(html.Tr([
        html.Td('Total', style=style),
        html.Td(stats['w'], style=style),
        html.Td(stats['l'], style=style),
        html.Td(f'{stats["p"]:.2%}', style=style),
        html.Td(stats['avg_length'], style=style),
        html.Td(stats['apm'], style=style),
    ]))

    return html.Table(header+body,
        style={
            "margin-bottom": 20,
            "padding": 2
        },
    )

def generate_hours(stats, id):
    x = list(stats['hours'].keys())
    p = []
    m = []
    empty_trace = []
    for hour in stats['hours']:
        p.append(stats['hours'][hour]['p'] * 100)
        m.append(stats['hours'][hour]['w'] + stats['hours'][hour]['l'])
        empty_trace.append(0)

    return dcc.Graph(
        figure=go.Figure(
            data=[
                go.Bar(
                    x=x,
                    y=p,
                    name='Win %',
                ),
                go.Bar(
                    x=x,
                    y=empty_trace, 
                    hoverinfo='none', 
                    showlegend=False
                ),
                go.Bar(
                    x=x,
                    y=empty_trace,
                    yaxis='y2', 
                    hoverinfo='none', 
                    showlegend=False
                ),
                go.Bar(
                    x=x,
                    y=m,
                    name='# of Games',
                    yaxis='y2'
                )
            ],
            layout=go.Layout(
                title='Win % by hour',
                yaxis=dict(
                    title='Percent'
                ),
                yaxis2=dict(
                    title='# of Games',
                    side='right',
                    overlaying='y'
                ),
                showlegend=True,
                legend=go.Legend(
                    x=0,
                    y=1.0
                ),
                margin=go.layout.Margin(l=40, r=0, t=40, b=30)
            )
        ),
        style={'height': 300}, 
        id=id
    )

def generate_days(stats, id):
    x = []
    p = []
    m = []
    empty_trace = []
    for day in stats['days']:
        x.append(WEEKDAYS[day])
        p.append(stats['days'][day]['p'] * 100)
        m.append(stats['days'][day]['w'] + stats['days'][day]['l'])
        empty_trace.append(0)

    return dcc.Graph(
        figure=go.Figure(
            data=[
                go.Bar(
                    x=x,
                    y=p,
                    name='Win %',
                ),
                go.Bar(
                    x=x,
                    y=empty_trace, 
                    hoverinfo='none', 
                    showlegend=False
                ),
                go.Bar(
                    x=x,
                    y=empty_trace,
                    yaxis='y2', 
                    hoverinfo='none', 
                    showlegend=False
                ),
                go.Bar(
                    x=x,
                    y=m,
                    name='# of Games',
                    yaxis='y2'
                )
            ],
            layout=go.Layout(
                title='Win % by weekday',
                yaxis=dict(
                    title='Percent'
                ),
                yaxis2=dict(
                    title='# of Games',
                    side='right',
                    overlaying='y'
                ),
                showlegend=True,
                legend=go.Legend(
                    x=0,
                    y=1.0
                ),
                margin=go.layout.Margin(l=40, r=0, t=40, b=30)
            )
        ),
        style={'height': 300}, 
        id=id
    )