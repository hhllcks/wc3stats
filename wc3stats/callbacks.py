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
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    return render_content_total

def create_race_tab_callback(race):
    def render_content_race(tab):
        if tab == f'{race}-tab-race':
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    return render_content_race

def create_map_tab_callback(race):
    def render_content_map(tab):
        if tab == f'{race}-tab-map':
            return {'display': 'block'}
        else:
            return {'display': 'none'}
    return render_content_map
