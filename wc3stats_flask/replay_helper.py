import os
import datetime
from .w3g import File
import json

path_to_replays = '/Users/hen/Boxcryptor/Google Drive/W3'

race = {
    'nightelf': 'Nightelf',
    'orc': 'Orc',
    'human': 'Human',
    'undead': 'Undead',
    'random': 'Random'
}

modes = {
    '1on1': '1on1',
    'team': 'ladder team game' 
}

def yieldFiles(p):
    if isinstance(p, str):
        for dirpath,_,filenames in os.walk(p):
            for f in filenames:
                if f.endswith(".w3g"):
                    yield os.path.abspath(os.path.join(dirpath, f))
    else:
        for f in p:
            print()
            yield f

def parse_slot_records(slot_records):
    slot_records_dict = {}
    for slot in slot_records:
        slot_records_dict[slot.player_id] = slot
    return slot_records_dict

def parse_players(players, slots):
    player_arr = []
    for player in players:
        slot = slots[player.id]
        player_arr.append({
            'id': player.id,
            'name': player.name,
            'race': player.race,
            'team': slot.team,
            'color': slot.color,
            'handicap': slot.handicap
        })
    return player_arr

def format_map(filename):
    mapname = filename[(filename.rfind(")")+1):(len(filename)-filename[::-1].rfind(".")-1)]
    mapname = mapname[:(len(mapname)-mapname[::-1].rfind("-")-1)]
    mapname = mapname[:(len(mapname)-mapname[::-1].rfind("_")-1)]
    return mapname

def format_length(ms):
    x = int(ms / 1000)
    seconds = x % 60
    if(seconds < 10):
        seconds = "0" + str(seconds)
    x /= 60
    minutes = int(x) % 60
    if(minutes < 10):
        minutes = "0" + str(minutes)
    x /= 60
    hours = int(x) % 24
    if(hours < 10):
        hours = "0" + str(hours)
    return str(hours) + ":" + str(minutes) + ":" + str(seconds)

def load_single_replay(file, filename, date):
    try:
        rep = File(file)
        if rep.game_type == modes['1on1'] and rep.game_name == 'BNet':
            slots = parse_slot_records(rep.slot_records)
            return {
                'game_name': rep.game_name,
                'players': parse_players(rep.players, slots),
                'player_count': rep.player_count,
                'length_formatted': format_length(rep.replay_length),
                'length': rep.replay_length,
                'game_type': rep.game_type,
                'map_file_name': rep.map_name,
                'map': format_map(rep.map_name),
                'apm_all': rep.player_apm(),
                'winner': rep.winner(),
                'winning_team': slots[rep.winner()].team,
                'filename': filename,
                'datetime': datetime.datetime.fromtimestamp(date)
            }
    except (IndexError, KeyError, ValueError, RuntimeError):
         print(filename)

# def load_replays(p):
#     replays = []

#     for f in yieldFiles(p):
#         try:
#             rep = File(f)
#             if rep.game_type == modes['1on1']:
#                 slots = parse_slot_records(rep.slot_records)
#                 replays.append({
#                     'game_name': rep.game_name,
#                     'players': parse_players(rep.players, slots),
#                     'player_count': rep.player_count,
#                     'length_formatted': format_length(rep.replay_length),
#                     'length': rep.replay_length,
#                     'game_type': rep.game_type,
#                     'map_file_name': rep.map_name,
#                     'map': format_map(rep.map_name),
#                     'winner': rep.winner(),
#                     'winning_team': slots[rep.winner()].team,
#                     'filename': f,
#                     'datetime': datetime.datetime.fromtimestamp(os.path.getmtime(f))
#                 })
#         except (IndexError, KeyError, ValueError):
#             print(f)

#     return replays

def get_player(replay, player_aliases):
    for main_player_name in player_aliases:
        for p in replay['players']:
            if main_player_name == p['name']:
                return p
    return None

def get_enemy_players(replay, main_team):
    enemy_players = {}
    for p in replay['players']:
        if main_team != p['team']:
            enemy_players[p['id']] = p
    return enemy_players

def get_other_race(replay, player, bAlliedRace=None):
    players = replay['players']
    races = set()
    for p in players:
        if bAlliedRace==True:
            if player['id'] != p['id'] and player['team'] == p['team']:
                races.add(p['race'])
        else:
            if player['team'] != p['team']:
                races.add(p['race'])
                
    return list(races)

def enrich_replay_data(replays, player_aliases):
    enriched_replays = []
    for rep in replays:
        if rep['game_name'] == 'BNet':
            player = get_player(rep, player_aliases)
            if player is not None:
                new_rep = {
                    'game_name': rep['game_name'],
                    'players': rep['players'],
                    'player_count': rep['player_count'],
                    'length_formatted': rep['length_formatted'],
                    'length': rep['length'],
                    'game_type': rep['game_type'],
                    'map_file_name': rep['map_file_name'],
                    'map': rep['map'],
                    'apm_all': rep['apm_all'],
                    'winner': rep['winner'],
                    'winning_team': rep['winning_team'],
                    'filename': rep['filename'],
                    'datetime': rep['datetime'],
                    'hour': rep['datetime'].hour,
                    'weekday': rep['datetime'].weekday()
                }
                
                if player['id'] in rep['apm_all']:
                    new_rep['apm'] = rep['apm_all'][player['id']]
                else:
                    new_rep['apm'] = 0
                
                new_rep['won'] = True if rep['winning_team'] == player['team'] else False
                new_rep['race'] = player['race']
                new_rep['ally_race'] = get_other_race(rep, player, True)
                new_rep['enemy_race'] = get_other_race(rep, player, False)
                new_rep['enemy_players'] = get_enemy_players(rep, player['team'])
                for p in list(new_rep['enemy_players'].values()):
                    if p['id'] in rep['apm_all']:
                        new_rep['enemy_players'][p['id']]['apm'] = rep['apm_all'][p['id']]
                    else:
                        new_rep['enemy_players'][p['id']]['apm'] = 0
                
                enriched_replays.append(new_rep)
                
    return enriched_replays

def replay_match(rep, race, maps, ally_race, enemy_race, won):
    if race is not None and rep['race'] not in race:
        return False
    
    if maps is not None and rep['map'] not in maps:
        return False

    if ally_race is not None and len(ally_race - set(rep['ally_race'])) > 0:
        return False
        
    if enemy_race is not None and len(enemy_race - set(rep['enemy_race'])) > 0:
        return False
    
    if won is not None and rep['won'] != won:
        return False
    
    return True

def get_empty_stats_dict(dont_add_dicts=False):
    stats = {
        'w': 0,
        'l': 0,
        'p': 0.0,
        'avg_len': 0,
        'avg_length': "",
        '0to10': {
            'w': 0,
            'l': 0,
            'p': 0.0,
        },
        '10to20': {
            'w': 0,
            'l': 0,
            'p': 0.0,
        },
        '20to30': {
            'w': 0,
            'l': 0,
            'p': 0.0,
        },
        '30up': {
            'w': 0,
            'l': 0,
            'p': 0.0,
        },
        'apm': 0,
        'hours': {
            '0': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '1': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '2': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '3': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '4': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '5': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '6': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '7': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '8': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '9': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '10': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '11': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '12': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '13': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '14': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '15': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '16': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '17': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '18': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '19': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '20': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '21': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '22': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '23': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            }
        },
        'days': {
            '0': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '1': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '2': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '3': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '4': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '5': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            },
            '6': {
                'w': 0,
                'l': 0,
                'p': 0.0,
                'apm': 0,
            }
        }
    }
    if not dont_add_dicts:
        stats['race'] = {}
        stats['map'] = {}
        stats['race_on_map'] = {}
    return stats

def compute_stats_single_replay(rep, stats):
    # compute temp values
    temp_length = stats['avg_len'] * (stats['w']+stats['l'])
    temp_length = temp_length + rep['length']
    temp_apm = stats['apm'] * (stats['w']+stats['l'])
    temp_apm = temp_apm + rep['apm']        
    temp_apm_hour = stats['hours'][str(rep['hour'])]['apm'] * (stats['hours'][str(rep['hour'])]['w']+stats['hours'][str(rep['hour'])]['l'])
    temp_apm_hour = temp_apm_hour + rep['apm'] 
    temp_apm_day = stats['days'][str(rep['weekday'])]['apm'] * (stats['days'][str(rep['weekday'])]['w']+stats['days'][str(rep['weekday'])]['l'])
    temp_apm_day = temp_apm_day + rep['apm']
    
    # update wins/losses
    if rep['won']:
        wl_string = 'w'
    else:
        wl_string = 'l'

    stats[wl_string] += 1
    stats['hours'][str(rep['hour'])][wl_string] +=1
    stats['days'][str(rep['weekday'])][wl_string] +=1
    if rep['length']<600000:
        stats['0to10'][wl_string] +=1
        stats['0to10']['p'] = round(stats['0to10']['w'] / (stats['0to10']['w']+stats['0to10']['l']), 2)
    elif rep['length']<1200000:
        stats['10to20'][wl_string] +=1
        stats['10to20']['p'] = round(stats['10to20']['w'] / (stats['10to20']['w']+stats['10to20']['l']), 2)
    elif rep['length']<1800000:
        stats['20to30'][wl_string] +=1
        stats['20to30']['p'] = round(stats['20to30']['w'] / (stats['20to30']['w']+stats['20to30']['l']), 2)
    else:
        stats['30up'][wl_string] +=1
        stats['30up']['p'] = round(stats['30up']['w'] / (stats['30up']['w']+stats['30up']['l']), 2)
        
    # replay length
    stats['avg_len'] = temp_length // (stats['w']+stats['l'])
    stats['avg_length'] = format_length(stats['avg_len'])
    
    # win %
    stats['p'] = round(stats['w'] / (stats['w']+stats['l']), 2)
    stats['hours'][str(rep['hour'])]['p'] = round(stats['hours'][str(rep['hour'])]['w'] / (stats['hours'][str(rep['hour'])]['w']+stats['hours'][str(rep['hour'])]['l']), 2)
    stats['days'][str(rep['weekday'])]['p'] = round(stats['days'][str(rep['weekday'])]['w'] / (stats['days'][str(rep['weekday'])]['w']+stats['days'][str(rep['weekday'])]['l']), 2)    
        
    # apm
    stats['apm'] = temp_apm // (stats['w']+stats['l'])
    stats['hours'][str(rep['hour'])]['apm'] = temp_apm_hour // (stats['hours'][str(rep['hour'])]['w']+stats['hours'][str(rep['hour'])]['l'])
    stats['days'][str(rep['weekday'])]['apm'] = temp_apm_day // (stats['days'][str(rep['weekday'])]['w']+stats['days'][str(rep['weekday'])]['l'])
    
    enemy_race_string = ', '.join(rep['enemy_race'])
    
    if 'race' in stats:
        if enemy_race_string not in stats['race']:
            stats['race'][enemy_race_string] = get_empty_stats_dict(True)
            stats['race'][enemy_race_string]['enemy_race'] = rep['enemy_race']
        compute_stats_single_replay(rep, stats['race'][enemy_race_string])
    
    if 'map' in stats and not isinstance(stats['map'],str):
        if rep['map'] not in stats['map']:
            stats['map'][rep['map']] = get_empty_stats_dict(True)
        compute_stats_single_replay(rep, stats['map'][rep['map']])
    
    if 'race_on_map' in stats:
        race_on_map_string = enemy_race_string + " on " + rep['map']
        if race_on_map_string not in stats['race_on_map']:
            stats['race_on_map'][race_on_map_string] = get_empty_stats_dict(True)
            stats['race_on_map'][race_on_map_string]['map'] = rep['map']
            stats['race_on_map'][race_on_map_string]['enemy_race'] = rep['enemy_race']
        compute_stats_single_replay(rep, stats['race_on_map'][race_on_map_string])

def compute_stats(replays, race=None, maps=None, ally_race=None, enemy_race=None, won=None):
    stats = {}
    for rep in replays:
        if replay_match(rep, race, maps, ally_race, enemy_race, won):
            if rep['race'] not in stats:
                stats[rep['race']] = get_empty_stats_dict()
            compute_stats_single_replay(rep, stats[rep['race']])
    return stats

def get_replay_list(replays):
    return sorted(replays, key=lambda k: k['datetime'], reverse=True) 

def list_replay_names(replays, race=None, maps=None, ally_race=None, enemy_race=None, won=None):
    filenames = []
    for rep in replays:
        if replay_match(rep, race, maps, ally_race, enemy_race, won):
            filenames.append(rep['filename'])
    return filenames

def stats_post_processing(stats):
    for race in stats.keys():
        for rom in stats[race]['race_on_map'].keys():
            race_on_map = stats[race]['race_on_map'][rom]
            enemy_race_string = ', '.join(race_on_map['enemy_race'])
            if enemy_race_string in stats[race]['race']:
                if not 'maps' in stats[race]['race'][enemy_race_string]:
                     stats[race]['race'][enemy_race_string]['maps'] = {}
                stats[race]['race'][enemy_race_string]['maps'][race_on_map['map']] = race_on_map

            if race_on_map['map'] in stats[race]['map']:
                if not 'enemy_races' in stats[race]['map'][race_on_map['map']]:
                    stats[race]['map'][race_on_map['map']]['enemy_races'] = {}
                stats[race]['map'][race_on_map['map']]['enemy_races'][enemy_race_string] = race_on_map

            del race_on_map['map'] 
            del race_on_map['enemy_race']
        del stats[race]['race_on_map']
