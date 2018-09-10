import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

# TODO remove hacky hack
import sys
from io import StringIO 

ALL_RACES = {
    'random': {
        'color': '#EBEBEB',
        'color_dark': '#E1E1E1',
        'color_light': '#F5F5F5',
    },
    'human': {
        'color': '#BCBCFF',
        'color_dark': '#0000F3',
        'color_light': '#E3E3FF',
    },
    'orc': {
        'color': '#E6F9E6',
        'color_dark': '#D6F5D6',
        'color_light': '#F6FDF6',
    },
    'undead': {
        'color': '#D0D0D0',
        'color_dark': '#C6C6C6',
        'color_light': '#DADADA',
    },
    'nightelf': {
        'color': '#FFDAFF',
        'color_dark': '#FFC7FF',
        'color_light': '#FFEEFF',
    },
}

ALL_MAPS = {
    "EchoIsles": "Echo Isles",
    "TwistedMeadows": "Twisted Meadows",
    "PlunderIsle": "Plunder Isle",
    "TurtleRock": "Turtle Rock",
    "NorthernIsles": "Northern Isles",
    "ConcealedHill": "Concealed Hill",
    "GnollWood": "Gnoll Wood",
    "Amazonia": "Amazonia",
    "LostTemple": "Lost Temple",
    "GlacialThaw": "Glacial Thaw",
    "MeltingValley": "Melting Valley",
    "SecretValley": "Secret Valley",
    "TheTwoRivers": "The Two Rivers",
    "TirisfalGlades": "Tirisfal Glades",
    "Adrenaline": "Adrenaline",
    "Avalanche": "Avalanche",
    "PhantomGrove": "Phantom Grove",
    "TerenasStand": "Terenas Stand",
    "LastRefuge": "Last Refuge",
    "SwampedTemple": "Swamped Temple",
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
        dcc.Tabs(
            id=mainrace + "-tabs", 
            value=mainrace + "-tab-total", 
            children=[
                dcc.Tab(label="Total", value=mainrace + "-tab-total"),
                dcc.Tab(label="By Enemy Race", value=mainrace + "-tab-race"),
                dcc.Tab(label="By Map", value=mainrace + "-tab-map"),
            ],
        )
    ]
    content.append(html.Div(id=mainrace + "-content-total", children=[
        generate_table_by_race(stats, "race"),
        html.Div(children=generate_graphs_by_race(stats, "race", mainrace + "-content-total-graph")),
        generate_table_by_map(stats, "map"),
        html.Div(children=[
                generate_hours(stats, 'graph-hours-total'),
                generate_days(stats, 'graph-days-total')
            ]
        )
    ]))
    content_race = []
    dropdownValues = []
    for race in list(ALL_RACES.keys()):
        if(race in stats['race']):
            dropdownValues.append({'label': race.title(), 'value': race})
            content_race.append(html.Div(id=mainrace + "-content-" + race, children=[
                generate_table_by_map(stats['race'][race], "maps"),
                html.Div(children=[
                    generate_hours(stats['race'][race], 'graph-hours-' + race),
                    generate_days(stats['race'][race], 'graph-days-' + race),
                ])
            ]))

    if(len(dropdownValues)>0):
        race_dropdown = dcc.Dropdown(
                id=mainrace + '-race-dropdown',
                options=dropdownValues,
                value=dropdownValues[0]['value'],
                clearable=False,
                searchable=False,
                style={"margin":2},
        )
        content_race = [race_dropdown] + content_race

    content.append(html.Div(id=mainrace+"-content-race", children=content_race))

    content_map = []
    dropdownValues = []
    for mapname in stats['map']:
        dropdownValues.append({'label': ALL_MAPS[mapname], 'value': mapname})
        content_map.append(html.Div(id=mainrace + "-content-" + mapname, children=[
            generate_table_by_race(stats['map'][mapname], "enemy_races"),
            html.Div(children=generate_graphs_by_race(stats['map'][mapname], "enemy_races", mainrace + "-content-" + mapname + "-graph")),
            html.Div(children=[
                    generate_hours(stats['map'][mapname], 'graph-hours-' + mapname),
                    generate_days(stats['map'][mapname], 'graph-days-' + mapname)
                ]
            )
        ]))

    if(len(dropdownValues)>0):
        map_dropdown = dcc.Dropdown(
                id=mainrace + '-map-dropdown',
                options=dropdownValues,
                value=dropdownValues[0]['value'],
                clearable=False,
                searchable=False,
                style={"margin":2},
        )
        content_map = [map_dropdown] + content_map

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
            "padding": 2
        },
        className="table",
    )

def generate_graphs_by_race(stats, racekey, id):
    x = []
    p = []
    l = []
    a = []
    for race in list(ALL_RACES.keys()):
        if race in stats[racekey]:
            x.append(race.title())
            p.append(stats[racekey][race]['p'])
            l.append(stats[racekey][race]['avg_len'] / 1000 / 60)
            a.append(stats[racekey][race]['apm'])

    if not x:
        return []

    return [
        # graph win%
        dcc.Graph(
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=x,
                        y=p,
                        name='Win %',
                    ),
                ],
                layout=go.Layout(
                    title='Win % by race',
                    yaxis=dict(
                        rangemode='tozero',
                        showgrid=False,
                    ),
                    legend=go.layout.Legend(
                        x=0,
                        y=1.0
                    ),
                    margin=go.layout.Margin(l=40, r=0, t=40, b=30),
                    autosize=True,
                )
            ),
            # style={
            #     "height": 200,
            # },
            # className="col",
            id=id + "_p",
        ),
        # graph length
        dcc.Graph(
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=x,
                        y=l,
                        name='Length',
                    ),
                ],
                layout=go.Layout(
                    title='Length by race',
                    yaxis=dict(
                        rangemode='tozero',
                        showgrid=False,
                    ),
                    legend=go.layout.Legend(
                        x=0,
                        y=1.0
                    ),
                    margin=go.layout.Margin(l=40, r=0, t=40, b=30),
                    autosize=True,
                )
            ),
            # style={
            #     "height": 200,
            # },
            # className="col",
            id=id + "_l",
        ),
        # graph apm
        dcc.Graph(
            figure=go.Figure(
                data=[
                    go.Bar(
                        x=x,
                        y=a,
                        name='APM',
                    ),
                ],
                layout=go.Layout(
                    title='APM by race',
                    yaxis=dict(
                        rangemode='tozero',
                        showgrid=False,
                    ),
                    legend=go.layout.Legend(
                        x=0,
                        y=1.0
                    ),
                    margin=go.layout.Margin(l=40, r=0, t=40, b=30),
                    autosize=True,
                )
            ),
            # style={
            #     "height": 200,
            # },
            # className="col",
            id=id + "_a",
        ),
    ]

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
            html.Td(ALL_MAPS[mapname], style=style),
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
        className="table",
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
                    showlegend=False,
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
                    title='Percent',
                    rangemode='tozero',
                    showgrid=False,
                ),
                yaxis2=dict(
                    title='# of Games',
                    side='right',
                    overlaying='y',
                    rangemode='tozero',
                    showgrid=False,
                ),
                showlegend=True,
                legend=go.layout.Legend(
                    x=0,
                    y=1.0
                ),
                margin=go.layout.Margin(l=40, r=0, t=40, b=30),
                autosize=True,
            )
        ),
        # style={'height': 300, 'width': "50%"}, 
        # className="col",
        id=id,
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
                    title='Percent',
                    rangemode='tozero',
                    showgrid=False,
                ),
                yaxis2=dict(
                    title='# of Games',
                    side='right',
                    overlaying='y',
                    rangemode='tozero',
                    showgrid=False,
                ),
                showlegend=True,
                legend=go.layout.Legend(
                    x=0,
                    y=1.0
                ),
                margin=go.layout.Margin(l=40, r=0, t=40, b=30),
                autosize=True,
            )
        ),
        # style={'height': 300, 'width': "50%"}, 
        # className="col",
        id=id,
    )