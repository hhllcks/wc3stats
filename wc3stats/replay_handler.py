from .replay_helper import enrich_replay_data, compute_stats, stats_post_processing, load_single_replay
import base64
import io
import re

def get_statistics(replays, aliases):
    replays = [r for r in replays if r is not None]
    er = enrich_replay_data(replays,aliases)
    stats = compute_stats(er)
    stats_post_processing(stats)
    return stats

def load_replay(contents, filename, date):
    f = io.BytesIO(base64.b64decode(re.sub("data:;base64", '', contents)))
    return load_single_replay(f, filename, date)
