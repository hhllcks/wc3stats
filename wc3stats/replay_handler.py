import replay_helper
import base64
import io
import re

def get_statistics(replays, aliases):
    replays = [r for r in replays if r is not None]
    er = replay_helper.enrich_replay_data(replays,aliases)
    stats = replay_helper.compute_stats(er)
    replay_helper.stats_post_processing(stats)
    return stats

def load_replay(contents, filename, date):
    f = io.BytesIO(base64.b64decode(re.sub("data:;base64", '', contents)))
    return replay_helper.load_single_replay(f, filename, date)
