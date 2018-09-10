def create_mainrace_tab_callback(race):
    def render_content(tab):
        if tab == f'{race}':
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    return render_content

def create_total_tab_callback(race):
    def render_content_total(tab):
        if tab == f'{race}-tab-total':
            return {
                'display': 'block',
                'margin': 10,
            }
        else:
            return {'display': 'none'}
    return render_content_total

def create_race_tab_callback(race):
    def render_content_race(tab):
        if tab == f'{race}-tab-race':
            return {
                'display': 'block',
                'margin': 10,
            }
        else:
            return {'display': 'none'}
    return render_content_race

def create_map_tab_callback(race):
    def render_content_map(tab):
        if tab == f'{race}-tab-map':
            return {
                'display': 'block',
                'margin': 10,
            }
        else:
            return {'display': 'none'}
    return render_content_map

def create_race_tab_dropdown_callback(race):
    def render_content_race(value):
        if value == f'{race}':
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    return render_content_race

def create_map_tab_dropdown_callback(mapname):
    def render_content_map(value):
        if value == f'{mapname}':
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    return render_content_map

