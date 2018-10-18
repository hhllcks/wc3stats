import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

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
    '0': 'Mon',
    '1': 'Tue',
    '2': 'Wed',
    '3': 'Thu',
    '4': 'Fri',
    '5': 'Sat',
    '6': 'Sun'
}

def get_stats_content(stats, rep_list):
    # overall_pane, overall_tab = get_overall_content(stats)
    race_panes, race_tabs = get_by_race_content(stats)
    race_tab = {
        "element_id": "race-tab",
        "items": race_tabs,
        "text": "By Race",
        "type": "dropdown"
    }
    # mape_panes, map_tabs = get_by_map_content(stats)
    # map_tab = {
    #     "element_id": "map-tab",
    #     "items": map_tabs,
    #     "text": "By Map",
    #     "type": "dropdown"
    # }
    fgl_pane, fgl_tab = get_fgl(rep_list)

    tabs = [race_tab, fgl_tab]
    panes = race_panes + [fgl_pane]
    navbar = get_navbar(tabs)
    panes = get_panes(panes)
    return navbar + panes

def get_overall_content(stats):
    return ""

def get_by_race_content(stats):
    panes = []
    tabs = []
    for race in list(ALL_RACES.keys()):
        if race in stats:
            race_pane, race_tab = _get_race_content(stats[race], race)
            panes.append(race_pane)
            tabs.append(race_tab)
    return (panes, tabs)

def _get_race_content(stats, racekey):
    html = f"<div class='card m-3'>{_get_race_content_race_header(stats,racekey)}<div>" + _get_race_content_race_body(stats, racekey) + "</div></div>"
    html = html + f"<div class='card m-3'>{_get_race_content_map_header(stats,racekey)}<div>" + _get_race_content_map_body(stats, racekey) + "</div></div>"
    
    return ({
        "element_id": f"race-{racekey}", 
        "content": html,
        "active": False
    },{
        "element_id": f"race-{racekey}-item",
        "href": f"race-{racekey}",
        "text": racekey.title(),
    })
    
def _get_race_content_race_header(stats, racekey):
    dropdown_items = _get_dropdown_item(f'race-{racekey}-map-dropdown-all', f"tab-table-{racekey}-by-race","All Maps", "listenToClick", f"data-header-text='By enemy race' data-header-id='race{racekey.title()}RaceHeader'")
    for mapname in stats['map']:
        dropdown_items = dropdown_items + _get_dropdown_item(f'race-{racekey}-map-dropdown-{mapname}', f"tab-table-{racekey}-by-race-{mapname}",ALL_MAPS[mapname], "listenToClick", f"data-header-text='By enemy race on {ALL_MAPS[mapname]}' data-header-id='race{racekey.title()}RaceHeader'")

    html = f"<div class='card-header'><div class='d-flex align-items-center justify-content-between'><div id='race{racekey.title()}RaceHeader'>By enemy race</div><ul class='nav nav-pills' role='tablist'><li class='nav-item dropdown'><a class='nav-link dropdown-toggle active' data-toggle='dropdown' href='#' role='button'>Filter by map</a><div class='dropdown-menu'>{dropdown_items}</li></ul></div></div>"

    return html

def _get_race_content_race_body(stats, racekey):
    html = f"<div class='tab-content' id='tabContent-{racekey}-race'>"

    html = html + _get_tab_pane(f"tab-table-{racekey}-by-race", _get_table_by_race(stats, f"table-{racekey}-by-race"), True)

    for mapname in stats['map']:
        html = html + _get_tab_pane(f"tab-table-{racekey}-by-race-{mapname}",_get_table_by_race(stats['map'][mapname], f"table-{racekey}-by-race-{mapname}"), False)

    html = html + "</div>"

    return html

def _get_race_content_map_header(stats, racekey):
    dropdown_items = _get_dropdown_item(f'race-{racekey}-race-dropdown-all', f"tab-table-{racekey}-by-map","All Races", "listenToClick", f"data-header-text='By Map' data-header-id='race{racekey.title()}MapHeader'")
    for race in stats['race']:
        dropdown_items = dropdown_items + _get_dropdown_item(f'race-{racekey}-race-dropdown-{race}', f"tab-table-{racekey}-by-map-{race}",race.title(), "listenToClick", f"data-header-text='By Map against {race.title()}' data-header-id='race{racekey.title()}MapHeader'")

    html = f"<div class='card-header'><div class='d-flex align-items-center justify-content-between'><div id='race{racekey.title()}MapHeader'>By map</div><ul class='nav nav-pills' role='tablist'><li class='nav-item dropdown'><a class='nav-link dropdown-toggle active' data-toggle='dropdown' href='#' role='button'>Filter by enemy race</a><div class='dropdown-menu'>{dropdown_items}</li></ul></div></div>"

    return html

def _get_race_content_map_body(stats, racekey):
    html = f"<div class='tab-content' id='tabContent-{racekey}-map'>"

    html = html + _get_tab_pane(f"tab-table-{racekey}-by-map", _get_table_by_map(stats, f"table-{racekey}-by-map"), True)

    for race in stats['race']:
        html = html + _get_tab_pane(f"tab-table-{racekey}-by-map-{race}",_get_table_by_map(stats['race'][race], f"table-{racekey}-by-map-{race}"), False)

    html = html + "</div>"

    return html

def get_by_map_content(stats):
    panes = []
    tabs = []
    for mapname in list(ALL_MAPS.keys()):
        if mapname in stats:
            map_pane, map_tab = _get_map_content(stats[mapname], mapname)
            panes.append(map_pane)
            tabs.append(map_tab)
    return (panes, tabs)

def _get_map_content(stats, mapname):
    html = _get_table_by_map(stats, "abc")
    return ({
        "element_id": f"map-{mapname}", 
        "content": html,
        "active": False
    },{
        "element_id": f"map-{mapname}-tab",
        "href": f"map-{mapname}",
        "text": ALL_MAPS[mapname],
    })
def _get_table_by_map(stats, table_id):
    html = f"<table id='{table_id}' class='table table-striped table-hover table-sm datatable' style='width:100%'><thead><tr><th>Map</th><th>Wins</th><th>Losses</th><th>Win %</th><th>Avg. Length</th><th>Avg. APM</th></tr></thead><tbody>"

    if 'map' in stats:
        map_dict = 'map'
    if 'maps' in stats:
        map_dict = 'maps'

    for mapname in list(ALL_MAPS.keys()):
        if mapname in stats[map_dict]:
            html = html + f"<tr><td>{ALL_MAPS[mapname]}</td><td>{stats[map_dict][mapname]['w']}</td><td>{stats[map_dict][mapname]['l']}</td><td>{stats[map_dict][mapname]['p']:.2%}</td><td>{stats[map_dict][mapname]['avg_length']}</td><td>{stats[map_dict][mapname]['apm']}</td></tr>"

    html = html + f"<tr><td>Total</td><td>{stats['w']}</td><td>{stats['l']}</td><td>{stats['p']:.2%}</td><td>{stats['avg_length']}</td><td>{stats['apm']}</td></tr>"

    html = html + "</tbody></table>"
    return html

def _get_table_by_race(stats, table_id):
    html = f"<table id='{table_id}' class='table table-striped table-hover table-sm datatable' style='width:100%'><thead><tr><th>vs</th><th>Wins</th><th>Losses</th><th>Win %</th><th>Avg. Length</th><th>Avg. APM</th></tr></thead><tbody>"

    if 'race' in stats:
        race_dict = 'race'
    if 'enemy_races' in stats:
        race_dict = 'enemy_races'

    for race in list(ALL_RACES.keys()):
        if race in stats[race_dict]:
            html = html + f"<tr><td>{race.title()}</td><td>{stats[race_dict][race]['w']}</td><td>{stats[race_dict][race]['l']}</td><td>{stats[race_dict][race]['p']:.2%}</td><td>{stats[race_dict][race]['avg_length']}</td><td>{stats[race_dict][race]['apm']}</td></tr>"

    html = html + f"<tr><td>Total</td><td>{stats['w']}</td><td>{stats['l']}</td><td>{stats['p']:.2%}</td><td>{stats['avg_length']}</td><td>{stats['apm']}</td></tr>"

    html = html + "</tbody></table>"
    return html

def get_fgl(rep_list):
    if len(rep_list) > 30:
        datatable_class = "datatablePaging"
    else:
        datatable_class = "datatable"

    html = "<table id='table_fgl' class='table table-striped table-hover table-sm " + datatable_class + "' style='width:100%'><thead><tr><th>Game Date</th><th>Map</th><th>Race</th><th>Enemy Race</th><th>Player</th><th>Result</th><th>Length</th><th>APM</th><th>Enemy APM</th></tr></thead><tbody>"

    for rep in rep_list:
        if rep['won']:
            result = 'Win'
        else:
            result = 'Loss'

        enemy_player_names = []
        enemy_player_apm = []
        for p in list(rep['enemy_players'].values()):
            enemy_player_names.append(p['name'])
            enemy_player_apm.append(str(int(p['apm'])))

        html = html + f"<tr><td>{rep['datetime']:%m/%d/%Y %H:%M:%S}</td><td>{ALL_MAPS[rep['map']]}</td><td>{rep['race'].title()}</td><td>{', '.join([x.title() for x in list(rep['enemy_race'])])}</td><td>{', '.join(enemy_player_names)}</td><td>{result}</td><td>{rep['length_formatted']}</td><td>{int(rep['apm'])}</td><td>{', '.join(enemy_player_apm)}</td></tr>"

    html = html + "</tbody></table>"
    return ({
        "element_id": "fgl", 
        "content": html,
        "active": False
    },{
        "element_id": "fgl-tab",
        "href": "fgl",
        "text": "Full Game List",
        "active": False,
        "type": "tab",
    })

def get_panes(panes):
    html = "<div class='tab-content'>"

    for pane in panes:
        html = html + _get_tab_pane(pane['element_id'], pane['content'], pane['active'])

    return html + "</div>"

def _get_tab_pane(element_id, content, active):
    if active:
        active_string = " show active"
    else:
        active_string = ""
    return f"<div class='tab-pane fade{active_string}' id='{element_id}' role='tabpanel'>{content}</div>"
            
def get_navbar(tabs):
    navbar = "<ul class='nav nav-tabs' role='tablist'>"

    for tab in tabs:
        if tab['type'] == "dropdown":
            navbar = navbar + _get_dropdown_tab(tab['element_id'], tab['items'], tab['text'])
        else:
            navbar = navbar + _get_tab(tab['element_id'], tab['href'], tab['text'], tab['active'])
    
    return navbar + "</ul>"

def _get_tab(element_id, href, text, active):
    if active:
        active_string = " active"
    else:
        active_string = ""
    return f"<li class='nav-item'><a class='nav-link{active_string}' data-toggle='tab' href='#{href}' id='{element_id}' role='tab'>{text}</a></li>"

def _get_dropdown_tab(element_id, items, text):
    item_string = ""
    for item in items:
        item_string = item_string + _get_dropdown_item(item['element_id'], item['href'], item['text'])

    return f"<li class='nav-item dropdown'><a class='nav-link dropdown-toggle' data-toggle='dropdown' href='#' role='button'>{text}</a><div class='dropdown-menu'>{item_string}</div></li>"

def _get_dropdown_item(element_id, href, text, additionalClasses="", customData=""):
    return f"<a class='dropdown-item {additionalClasses}' role='tab' {customData} data-toggle='tab' id='{element_id}' href='#{href}'>{text}</a>"

# OLD DASH LAYOUT
def get_stats_layout(stats, rep_list):
    tabs = []
    content = [] 
    races = sorted(list(stats.keys()))
    if(len(races)>0):
        for race in races:
            tabs.append(
                dcc.Tab(label=race.title(), value=race)
            )
            content.append(
                html.Div(id=race + '-content',
                    children=get_race_content(stats[race], race)
                )
            )

        tabs.append(
            dcc.Tab(label="Full Game List", value="list")
        )
        content.append(
            html.Div(id='full-game-list-content',
                children=get_full_game_list_content(rep_list)
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
        generate_table_by_map(stats, "map"),
        html.Div(children=[
                html.Div(generate_hours(stats, 'graph-hours-total'),style={"display": "inline-block"}),
                html.Div(generate_days(stats, 'graph-days-total'),style={"display": "inline-block"}),
            ],
            style={'width':"100%", "display": "inline-block"},
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
                        html.Div(generate_lengths(stats['race'][race], 'graph-lengths-' + race),style={"display": "inline-block"}),
                        html.Div(generate_hours(stats['race'][race], 'graph-hours-' + race),style={"display": "inline-block"}),
                        html.Div(generate_days(stats['race'][race], 'graph-days-' + race),style={"display": "inline-block"}),
                    ],
                    style={'width':"100%", "display": "inline-block"},
                )
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
            html.Div(children=[
                    html.Div(generate_lengths(stats['map'][mapname], 'graph-lengths-' + mapname),style={"display": "inline-block"}),
                    html.Div(generate_hours(stats['map'][mapname], 'graph-hours-' + mapname),style={"display": "inline-block"}),
                    html.Div(generate_days(stats['map'][mapname], 'graph-days-' + mapname),style={"display": "inline-block"}),
                ],
                style={'width':"100%", "display": "inline-block"},
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

def generate_lengths(stats, id):
    x = ['0-10 min', '10-20 min', '20-30 min', '> 30 min']
    p = []

    p.append(stats['0to10']['p'] * 100)
    p.append(stats['10to20']['p'] * 100)
    p.append(stats['20to30']['p'] * 100)
    p.append(stats['30up']['p'] * 100)

    return dcc.Graph(
        figure=go.Figure(
            data=[
                go.Bar(
                    x=x,
                    y=p,
                    name='Win %',
                ),
            ],
            layout=go.Layout(
                title='Win % by length',
                yaxis=dict(
                    title='Percent',
                    rangemode='tozero',
                    showgrid=False,
                ),
                showlegend=True,
                legend=go.layout.Legend(
                    x=0,
                    y=1.0
                ),
                margin=go.layout.Margin(l=40, r=40, t=30, b=40),
                autosize=True,
            )
        ),
        id=id,
        # className="col",
        style={'height':200, 'width': 500},
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
                margin=go.layout.Margin(l=40, r=40, t=30, b=40),
                autosize=True,
            )
        ),
        id=id,
        # className="col",
        style={'height':200, 'width': 500},
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
                margin=go.layout.Margin(l=40, r=40, t=30, b=40),
                autosize=True,
            )
        ),
        id=id,
        # className="col",
        style={'height':200, 'width': 500},
    )

def get_full_game_list_content(rep_list):
    header = [html.Tr([
        html.Th('Game Date'),
        html.Th('Map'),
        html.Th('Race'),
        html.Th('Enemy Race'),
        html.Th('Player'),
        html.Th('Result'),
        html.Th('Length'),
        html.Th('APM'),
        html.Th('Enemy APM')
    ])]
    body = []

    for rep in rep_list:
        if rep['won']:
            result = 'Win'
            style = {
                'background-color': '#E5FBE5',
                'padding': 1,
            }
        else:
            result = 'Loss'
            style = {
                'background-color': '#FFF1D8',
                'padding': 1,
            }


        enemy_player_names = []
        enemy_player_apm = []
        for p in list(rep['enemy_players'].values()):
            enemy_player_names.append(p['name'])
            enemy_player_apm.append(str(int(p['apm'])))

        body.append(html.Tr([
            html.Td(f'{rep["datetime"]:%m/%d/%Y %H:%M:%S}',style=style),
            html.Td(ALL_MAPS[rep['map']],style=style),
            html.Td(rep['race'].title(),style=style),
            html.Td(", ".join([x.title() for x in list(rep['enemy_race'])]),style=style),
            html.Td(", ".join(enemy_player_names),style=style),
            html.Td(result,style=style),
            html.Td(rep['length_formatted'],style=style),
            html.Td(int(rep['apm']),style=style),
            html.Td(", ".join(enemy_player_apm),style=style),
        ]))

    return html.Table(header+body,
        style={
            "margin-bottom": 20,
            "padding": 2
        },
        className="table",
    )