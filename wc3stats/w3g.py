"""Implements the basic w3g file class. Based on information available at 

* http://w3g.deepnode.de/files/w3g_format.txt

:author: scopz <scopatz@gmail.com>
"""
from __future__ import unicode_literals, print_function
import io
import sys
import base64
import zlib
import struct
from collections import namedtuple
from w3g_rs import RACES, SPEEDS, OBSERVER, FIXED_TEAMS, GAME_TYPES, STATUS, COLORS, AI_STRENGTH, SELECT_MODES, CHAT_MODES, NUMERIC_ITEM, ITEMS, ABILITY_FLAGS, ITEMS_TO_RACE

WORD = 2   # bytes
DWORD = 4  # bytes, double word
NULLSTR = b'\0'
MAXPOS = 16384.0  # maps may range from -MAXPOS to MAXPOS with (0, 0) at the center

# build number associated with v1.07 of the game
BUILD_1_06 = 4656

# build number associated with v1.07 of the game
BUILD_1_07 = 6031

# build number associated with v1.13 of the game
BUILD_1_13 = 6037

# build number associated with v1.14b of the game
BUILD_1_14B = 6040

if sys.version_info[0] < 3:
    BLENFLAG = {1: 'B', WORD: 'H', DWORD: 'L', 8: 'Q'}
    b2i = lambda b: struct.unpack('<' + BLENFLAG[len(b)], b)[0]

    # to print unicode
    import codecs
    UTF8Writer = codecs.getwriter('utf8')
    utf8writer = UTF8Writer(sys.stdout)
    def umake(f):
        def uprint(*objects, **kw):
            uo = map(unicode, objects)
            if 'file' not in kw:
                kw['file'] = utf8writer
            f(*uo, **kw)
        return uprint
    print = umake(print)

    # fake lru_cache
    lru_cache = lambda maxsize=128, typed=False: lambda f: f
else:
    b2i = lambda b: b if isinstance(b, int) else int.from_bytes(b, 'little')
    from functools import lru_cache

def nulltermstr(b):
    """Returns the next null terminated string from bytes and its length."""
    i = b.find(NULLSTR)
    s = b[:i].decode('utf-8')
    return s, i

def blizdecomp(b):
    """Performs wacky blizard 'decompression' and returns bytes and len in 
    original string.
    """
    if isinstance(b, str):
        b = list(map(b2i, b))
    d = []
    pos = 0
    mask = None
    while b[pos] != 0:
        if pos%8 == 0:
            mask = b[pos]
        elif ((mask & (0x1 << (pos%8))) == 0):
            d.append(b[pos] - 1)
        else:
            d.append(b[pos])
        pos += 1
    if bytes == str:
        d = b''.join(map(chr, d))
    else:
        d = bytes(d)
    return d, pos

def blizdecode(b):
    d, l = blizdecomp(b)
    return d.decode(), l

def bits(b):
    """Returns the bits in a byte"""
    if isinstance(b, str):
        b = ord(b)
    return tuple([(b >> i) & 1 for i in range(8)])

def bitfield(b, idx):
    """Returns an integer representing the bit field. idx may be a slice."""
    f = bits(b)[idx]
    if f != 0 and f != 1:
        val = 0
        for i, x in enumerate(f):
            val += x * 2**i
        f = val
    return f

def b2f(b):
    return struct.unpack('<f', b)[0]

class Player(namedtuple('Player', ['id', 'name', 'race', 'ishost', 
                                   'runtime', 'raw', 'size'])):
    def __new__(cls, id=-1, name='', race='', ishost=False, runtime=-1, 
                 raw=b'', size=0):
        self = super(Player, cls).__new__(cls, id=id, name=name, race=race, 
                                          ishost=ishost, runtime=runtime, raw=raw, 
                                          size=size)
        return self

    @classmethod
    def from_raw(cls, data):
        kw = {'ishost': b2i(data[0]) == 0, 
              'id': b2i(data[1])}
        kw['name'], i = nulltermstr(data[2:])
        n = 2 + i + 1
        custom_or_ladder = b2i(data[n])
        n += 1
        if custom_or_ladder == 0x01:  # custom
            n += 1
            kw['runtime'] = 0
            kw['race'] = 'none'
        elif custom_or_ladder == 0x08:  # ladder
            kw['runtime'] = b2i(data[n:n+4])
            n += 4
            race_flag = b2i(data[n:n+4])
            n += 4
            kw['race'] = RACES[race_flag]
        else:
            raise ValueError("Player not recognized custom or ladder.")
        kw['size'] = n
        kw['raw'] = data[:n]
        return cls(**kw)

class SlotRecord(namedtuple('Player', ['player_id', 'status', 'ishuman', 'team', 
                                       'color', 'race', 'ai', 'handicap','raw', 
                                       'size'])):
    def __new__(cls, player_id=-1, status='empty', ishuman=False, team=-1, color='red', 
                race='none', ai='normal', handicap=100, raw=b'', size=0):
        self = super(SlotRecord, cls).__new__(cls, player_id=player_id, status=status, 
                                              ishuman=ishuman, team=team, color=color,
                                              race=race, ai=ai, handicap=handicap,  
                                              raw=raw, size=size)
        return self

    @classmethod
    def from_raw(cls, data):
        kw = {'player_id': b2i(data[0]), 
              'status': STATUS[b2i(data[2])],
              'ishuman': (b2i(data[3]) == 0x00),
              'team': b2i(data[4]),
              'color': COLORS[b2i(data[5])],
              'race': RACES.get(b2i(data[6]), 'none'),
              }
        kw['size'] = size = len(data)
        kw['raw'] = data
        if 8 <= size:
            kw['ai'] = AI_STRENGTH[b2i(data[7])]
        if 9 <= size:
            kw['handicap'] = b2i(data[8])
        return cls(**kw)

class Event(object):
    """An event base class."""

    apm = False

    def __init__(self, f):
        self.f = f
        self.time = f.clock

    def strtime(self):
        secs = self.time / 1000.0
        s = secs % 60
        m = int(secs / 60) % 60
        h = int(secs / 3600)
        rtn = []
        if h > 0: 
            rtn.append("{0:02}".format(h))
        if m > 0: 
            rtn.append("{0:02}".format(m))
        rtn.append("{0:06.3f}".format(s))
        return ":".join(rtn)

class Chat(Event):

    apm = False

    def __init__(self, f, player_id, mode, msg):
        super(Chat, self).__init__(f)
        self.player_id = player_id
        self.mode = mode
        self.msg = msg

    def __str__(self):
        t = self.strtime()
        p = self.f.player_name(self.player_id)
        m = self.strmode()
        return "[{t}] <{m}> {p}: {msg}".format(t=t, p=p, m=m, msg=self.msg)

    def strmode(self):
        mode = self.mode
        if not mode.startswith('player'):
            return mode
        pid = int(mode[6:])
        return self.f.player_name(pid)

class LeftGame(Event):

    apm = False

    remote_results = {
        0x01: 'left',
        0x07: 'left',
        0x08: 'lost',
        0x09: 'won',
        0x0A: 'draw',
        0x0B: 'left',
        }

    local_not_last_results = {
        0x01: 'disconnected',
        0x07: 'lost',
        0x08: 'lost',
        0x09: 'won',
        0x0A: 'draw',
        0x0B: 'lost',
        }

    local_last_results = {
        0x01: 'disconnected',
        0x08: 'lost',
        0x09: 'won',
        }

    def __init__(self, f, player_id, closedby, resultflag, inc, unknownflag):
        super(LeftGame, self).__init__(f)
        self.player_id = player_id
        self.closedby = closedby
        self.resultflag = resultflag
        self.inc = inc
        self.unknownflag = unknownflag
        self.next = None

    def __str__(self):
        t = self.strtime()
        p = self.f.player_name(self.player_id)
        r = self.result()
        rtn = "[{t}] <{cb}> {p} left game, {r}"
        return rtn.format(t=t, p=p, cb=self.closedby, r=r)

    def result(self):
        cb = self.closedby
        res = self.resultflag
        if cb == 'remote':
            r = self.remote_results[res]
        elif cb == 'local':
            if self.next is None:
                if res == 0x07 or res == 0x0B:
                    r = 'won' if self.inc else 'lost'
                else:
                    r = self.local_last_results[res]
            else:
                r = self.local_not_last_results[res]
        else:
            r = 'left'
        return r

class Countdown(Event):

    apm = False

    def __init__(self, f, mode, secs):
        super(Countdown, self).__init__(f)
        self.mode = mode
        self.secs = secs

    def __str__(self):
        t = self.strtime()
        rtn = "[{t}] Game countdown {mode}, {m:02}:{s:02} left"
        return rtn.format(t=t, mode=self.mode, m=int(self.secs/60), s=self.secs%60)

class Action(Event):

    le = -1
    id = -1
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(Action, self).__init__(f)
        self.player_id = player_id

    def __str__(self):
        t = self.strtime()
        p = self.f.player_name(self.player_id)
        rtn = "[{t}] <{c}> {p}"
        return rtn.format(t=t, c=self.__class__.__name__, p=p)

    def obj(self, o):
        if o == b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF': 
            return 'Ground'
        return 'Object#{0}'.format(b2i(o))

class Pause(Action):

    id = 0x01
    apm = False

    def __init__(self, f, player_id, action_block):
        super(Pause, self).__init__(f, player_id, action_block)

class Resume(Action):

    id = 0x02
    apm = False

    def __init__(self, f, player_id, action_block):
        super(Resume, self).__init__(f, player_id, action_block)

class SetGameSpeed(Action):

    id = 0x03
    size = 2
    apm = False

    def __init__(self, f, player_id, action_block):
        super(SetGameSpeed, self).__init__(f, player_id, action_block)
        self.speed = b2i(action_block[1])

    def __str__(self):
        s = super(SetGameSpeed, self).__str__()
        return '{0} - {1}'.format(s, SPEEDS[self.speed])

class IncreaseGameSpeed(Action):

    id = 0x04
    apm = False

    def __init__(self, f, player_id, action_block):
        super(IncreaseGameSpeed, self).__init__(f, player_id, action_block)

class DecreaseGameSpeed(Action):

    id = 0x05
    apm = False

    def __init__(self, f, player_id, action_block):
        super(DecreaseGameSpeed, self).__init__(f, player_id, action_block)

class SaveGame(Action):

    id = 0x06
    size = None
    apm = False

    def __init__(self, f, player_id, action_block):
        super(SaveGame, self).__init__(f, player_id, action_block)
        self.name, n = nulltermstr(action_block[1:])
        self.size = 1 + n + 1

    def __str__(self):
        s = super(SaveGame, self).__str__()
        return '{0} - {1}'.format(s, self.name)

class SaveGameFinished(Action):

    id = 0x07
    size = 5
    apm = False

    def __init__(self, f, player_id, action_block):
        super(SaveGameFinished, self).__init__(f, player_id, action_block)

class Ability(Action):

    id = 0x10
    apm = True

    def __init__(self, f, player_id, action_block):
        super(Ability, self).__init__(f, player_id, action_block)
        offset = 1
        o = 1 if f.build_num < BUILD_1_13 else WORD
        self.flags = b2i(action_block[offset:offset+o])
        offset += o
        self.ability = ability = action_block[offset:offset+DWORD]
        if ability[-2:] != NUMERIC_ITEM:
            self.ability = ability[::-1]
        offset += DWORD
        offset += 2 * DWORD if f.build_num >= BUILD_1_07 else 0
        self.size = offset

    def __str__(self):
        s = super(Ability, self).__str__()
        aflgs = ABILITY_FLAGS.get(self.flags, None)
        astr = '' if aflgs is None else ' [{0}]'.format(aflgs)
        return '{0} - {1}{2}'.format(s, ITEMS.get(self.ability, self.ability), astr) 

class AbilityPosition(Ability):

    id = 0x11
    apm = True

    def __init__(self, f, player_id, action_block):
        super(AbilityPosition, self).__init__(f, player_id, action_block)
        offset = self.size
        x = b2f(action_block[offset:offset+DWORD])
        offset += DWORD
        y = b2f(action_block[offset:offset+DWORD])
        offset += DWORD
        self.loc = (x, y)
        self.size = offset

    def __str__(self):
        s = super(AbilityPosition, self).__str__()
        return '{0} at ({1:.3%}, {2:.3%})'.format(s, self.loc[0]/MAXPOS, 
                                                     self.loc[1]/MAXPOS) 

class AbilityPositionObject(AbilityPosition):

    id = 0x12
    apm = True

    def __init__(self, f, player_id, action_block):
        super(AbilityPositionObject, self).__init__(f, player_id, action_block)
        offset = self.size
        self.object = action_block[offset:offset+2*DWORD]
        offset += 2*DWORD
        self.size = offset

    def _super_str(self):
        return super(AbilityPositionObject, self).__str__()

    def __str__(self):
        s = super(AbilityPositionObject, self).__str__()
        return '{0} {1}'.format(s, self.obj(self.object))

class GiveItem(AbilityPositionObject):

    id = 0x13
    apm = True

    def __init__(self, f, player_id, action_block):
        super(GiveItem, self).__init__(f, player_id, action_block)
        offset = self.size
        self.item = action_block[offset:offset+2*DWORD]
        offset += 2*DWORD
        self.size = offset

    def __str__(self):
        s = super(GiveItem, self)._super_str()
        return '{0} {1} -> {2}'.format(s, self.obj(self.item), 
                                          self.obj(self.object))

class DoubleAbility(AbilityPosition):

    id = 0x14
    apm = True

    def __init__(self, f, player_id, action_block):
        super(DoubleAbility, self).__init__(f, player_id, action_block)
        self.ability1 = self.ability
        self.loc1 = self.loc
        offset = self.size
        self.ability2 = ability2 = action_block[offset:offset+DWORD]
        offset += DWORD
        if ability2[-2:] != NUMERIC_ITEM:
            self.ability2 = ability2[::-1]
        offset += 9
        x2 = b2f(action_block[offset:offset+DWORD])
        offset += DWORD
        y2 = b2f(action_block[offset:offset+DWORD])
        offset += DWORD
        self.loc2 = (x2, y2)
        self.size = offset

    def __str__(self):
        s = super(DoubleAbility, self).__str__()
        loc2str = ''
        if self.loc1 != self.loc2:
            loc2str = ' at ({0:.3%}, {1:.3%})'.format(self.loc2[0]/MAXPOS, 
                                                      self.loc2[1]/MAXPOS) 
        return '{0} -> {1}{2}'.format(s, ITEMS.get(self.ability2, self.ability2), 
                                      loc2str)

class ChangeSelection(Action):

    id = 0x16
    apm = True

    modes = {0x01: 'Select', 0x02: 'Deselect'}

    def __init__(self, f, player_id, action_block):
        super(ChangeSelection, self).__init__(f, player_id, action_block)
        self.mode = b2i(action_block[1])
        n = b2i(action_block[2:2+WORD])
        self.size = 4 + 8*n
        objs = action_block[4:]
        self.objects = [objs[i:i+8] for i in range(n)]
        self.calc_apm()

    def calc_apm(self):
        if self.mode == 0x02:
            return
        if len(self.f.events) == 0:
            return
        last = self.f.events[-1]
        if last.player_id != self.player_id:
            return
        if not isinstance(last, ChangeSelection):
            return
        if last.mode != 0x02:
            return 
        self.apm = False

    def __str__(self):
        s = super(ChangeSelection, self).__str__()
        return '{0} {1} [{2}]'.format(s, self.modes[self.mode], 
                                      ', '.join(map(self.obj, self.objects)))

class AssignGroupHotkey(Action):

    id = 0x17
    apm = True

    def __init__(self, f, player_id, action_block):
        super(AssignGroupHotkey, self).__init__(f, player_id, action_block)
        self.hotkey = (b2i(action_block[1]) + 1) % 10
        n = b2i(action_block[2:2+WORD])
        self.size = 4 + 8*n
        objs = action_block[4:]
        self.objects = [objs[i:i+8] for i in range(n)]

    def __str__(self):
        s = super(AssignGroupHotkey, self).__str__()
        return '{0} Assign Hotkey #{1} [{2}]'.format(s, self.hotkey, 
            ', '.join(map(self.obj, self.objects)))

class SelectGroupHotkey(Action):

    id = 0x18
    size = 3
    apm = True

    def __init__(self, f, player_id, action_block):
        super(SelectGroupHotkey, self).__init__(f, player_id, action_block)
        self.hotkey = (b2i(action_block[1]) + 1) % 10

    def __str__(self):
        s = super(SelectGroupHotkey, self).__str__()
        return '{0} Select Hotkey #{1}'.format(s, self.hotkey)

class SelectSubgroup(Action):

    id = 0x19
    apm = False

    def __init__(self, f, player_id, action_block):
        super(SelectSubgroup, self).__init__(f, player_id, action_block)
        if f.build_num < BUILD_1_14B:
            self.size = 2 
            self.subgroup = b2i(action_block[1])
            if self.subgroup != 0x00 and self.subgroup != 0xFF:
                self.apm = True
        else:
            self.size = 13
            offset = 1
            self.ability = ability = action_block[offset:offset+DWORD]
            offset += DWORD
            if ability[-2:] != NUMERIC_ITEM:
                self.ability = ability[::-1]
            self.object = action_block[offset:offset+2*DWORD]
            offset += 2*DWORD

    def __str__(self):
        s = super(SelectSubgroup, self).__str__()
        if self.f.build_num < BUILD_1_14B:
            return '{0} - #{1}'.format(s, self.subgroup)
        else:
            return '{0} - {1} {2}'.format(s, 
                ITEMS.get(self.ability, self.ability), self.obj(self.object))

class PreSubselect(Action):

    id = 0x1A
    apm = False

    def __init__(self, f, player_id, action_block):
        super(PreSubselect, self).__init__(f, player_id, action_block)

class UnknownAction(Action):

    #  <=1.14b, >1.14b
    le = BUILD_1_14B
    id = (0x1A, 0x1B)
    size = 10
    apm = False

    def __init__(self, f, player_id, action_block):
        super(UnknownAction, self).__init__(f, player_id, action_block)

class SelectGroundItem(Action):

    #  <=1.14b, >1.14b
    le = BUILD_1_14B
    id = (0x1B, 0x1C)
    size = 10
    apm = True

    def __init__(self, f, player_id, action_block):
        super(SelectGroundItem, self).__init__(f, player_id, action_block)
        self.item = action_block[2:10]

    def __str__(self):
        s = super(SelectGroundItem, self).__str__()
        return '{0} - {1} '.format(s, self.obj(self.item))

class CancelHeroRevival(Action):

    #  <=1.14b, >1.14b
    le = BUILD_1_14B
    id = (0x1C, 0x1D)
    size = 9
    apm = True

    def __init__(self, f, player_id, action_block):
        super(CancelHeroRevival, self).__init__(f, player_id, action_block)
        self.hero = action_block[1:9]

    def __str__(self):
        s = super(CancelHeroRevival, self).__str__()
        return '{0} - {1} '.format(s, self.obj(self.hero))

class RemoveUnitFromBuildingQueue(Action):

    #  <=1.14b, >1.14b
    le = BUILD_1_14B
    id = (0x1D, 0x1E)
    size = 6
    apm = True

    def __init__(self, f, player_id, action_block):
        super(RemoveUnitFromBuildingQueue, self).__init__(f, player_id, action_block)
        self.pos = b2i(action_block[1])
        self.unit = unit = action_block[2:2+DWORD]
        if unit[-2:] != NUMERIC_ITEM:
            self.unit = unit[::-1]

    def __str__(self):
        s = super(RemoveUnitFromBuildingQueue, self).__str__()
        return '{0} - {1} at position #{2}'.format(s, ITEMS.get(self.unit, self.unit),
                                                   self.pos)

class RareUnknownAction(Action):

    id = 0x21
    size = 9
    apm = False

    def __init__(self, f, player_id, action_block):
        super(RareUnknownAction, self).__init__(f, player_id, action_block)

class TheDudeAbides(Action):

    id = 0x20
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(TheDudeAbides, self).__init__(f, player_id, action_block)

class SomebodySetUpUsTheBomb(Action):

    id = 0x22
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(SomebodySetUpUsTheBomb, self).__init__(f, player_id, action_block)

class WarpTen(Action):

    id = 0x23
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(WarpTen, self).__init__(f, player_id, action_block)

class IocainePowder(Action):

    id = 0x24
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(IocainePowder, self).__init__(f, player_id, action_block)

class PointBreak(Action):

    id = 0x25
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(PointBreak, self).__init__(f, player_id, action_block)

class WhosYourDaddy(Action):

    id = 0x26
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(WhosYourDaddy, self).__init__(f, player_id, action_block)

class KeyserSoze(Action):

    id = 0x27
    size = 6
    apm = False

    def __init__(self, f, player_id, action_block):
        super(KeyserSoze, self).__init__(f, player_id, action_block)
        self.gold = b2i(action_block[2:2+DWORD]) - 2**31

    def __str__(self):
        s = super(KeyserSoze, self).__str__()
        return '{0} - {1} gold'.format(s, self.gold)

class LeafitToMe(Action):

    id = 0x28
    size = 6
    apm = False

    def __init__(self, f, player_id, action_block):
        super(LeafitToMe, self).__init__(f, player_id, action_block)
        self.lumber = b2i(action_block[2:2+DWORD]) - 2**31

    def __str__(self):
        s = super(LeafitToMe, self).__str__()
        return '{0} - {1} lumber'.format(s, self.lumber)

class ThereIsNoSpoon(Action):

    id = 0x2
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(ThereIsNoSpoon, self).__init__(f, player_id, action_block)

class StrengthAndHonor(Action):

    id = 0x2A
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(StrengthAndHonor, self).__init__(f, player_id, action_block)

class ItVexesMe(Action):

    id = 0x2B
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(ItVexesMe, self).__init__(f, player_id, action_block)

class WhoIsJohnGalt(Action):

    id = 0x2C
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(WhoIsJohnGalt, self).__init__(f, player_id, action_block)

class GreedIsGood(Action):

    id = 0x2D
    size = 6
    apm = False

    def __init__(self, f, player_id, action_block):
        super(GreedIsGood, self).__init__(f, player_id, action_block)
        self.gold = self.lumber = b2i(action_block[2:2+DWORD]) - 2**31

    def __str__(self):
        s = super(GreedIsGood, self).__str__()
        return '{0} - {1} gold and {2} lumber'.format(s, self.gold, self.lumber)

class DayLightSavings(Action):

    id = 0x2E
    size = 5
    apm = False

    def __init__(self, f, player_id, action_block):
        super(DayLightSavings, self).__init__(f, player_id, action_block)
        self.time = struct.unpack('f', action_block[1:5])

class ISeeDeadPeople(Action):

    id = 0x2F
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(ISeeDeadPeople, self).__init__(f, player_id, action_block)

class Synergy(Action):

    id = 0x30
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(Synergy, self).__init__(f, player_id, action_block)

class SharpAndShiny(Action):

    id = 0x31
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(SharpAndShiny, self).__init__(f, player_id, action_block)

class AllYourBaseAreBelongToUs(Action):

    id = 0x32
    size = 1
    apm = False

    def __init__(self, f, player_id, action_block):
        super(AllYourBaseAreBelongToUs, self).__init__(f, player_id, action_block)

class ChangeAllyOptions(Action):

    id = 0x50
    size = 6
    apm = False

    def __init__(self, f, player_id, action_block):
        super(ChangeAllyOptions, self).__init__(f, player_id, action_block)
        self.ally_id = b2i(action_block[1])
        self.flags_bits = bits(b2i(action_block[2:4])) + bits(b2i(action_block[5:9]))

    def flagstr(self):
        fs = []
        b = self.flags_bits
        if all(b[:5]):
            fs.append('is allied')
        if b[5]:
            fs.append('shares vision')
        if b[6]:
            fs.append('shares unit control')
        svi = 10 if self.f.build_num >= BUILD_1_07 else 9

        if b[svi]:
            fs.append('shares victory')
        if len(fs) > 1:
            fs[-1] = 'and ' + fs[-1]
        return ', {0}'.format(fs)

    def __str__(self):
        s = super(ChangeAllyOptions, self).__str__()
        a = self.f.player_name(self.ally_id)
        return '{0} {1} with {2}'.format(s, self.flagstr(), a)

class TransferResources(Action):

    id = 0x51
    size = 10
    apm = False

    def __init__(self, f, player_id, action_block):
        super(TransferResources, self).__init__(f, player_id, action_block)
        self.ally_id = b2i(action_block[1])
        offset = 2
        self.gold = b2i(action_block[offset:offset+DWORD])
        offset += DWORD
        self.lumber = b2i(action_block[offset:offset+DWORD])

    def __str__(self):
        s = super(TransferResources, self).__str__()
        a = self.f.player_name(self.ally_id)
        return '{0} transfered {1} gold and {2} lumber to {3}'.format(s, self.gold, 
                                                                      self.lumber, a)

class MapTriggerChatCommand(Action):

    id = 0x60
    apm = False

    def __init__(self, f, player_id, action_block):
        super(MapTriggerChatCommand, self).__init__(f, player_id, action_block)
        offset = 1 + 2*DWORD
        s, i = nulltermstr(action_block[offset:])
        self.size = offset + i + 1

class EscapePressed(Action):

    id = 0x61
    size = 1
    apm = True

    def __init__(self, f, player_id, action_block):
        super(EscapePressed, self).__init__(f, player_id, action_block)

class ScenarioTrigger(Action):

    id = 0x62
    apm = False

    def __init__(self, f, player_id, action_block):
        super(ScenarioTrigger, self).__init__(f, player_id, action_block)
        self.size = 13 if self.f.build_num >= BUILD_1_07 else 9

class HeroSkillSubmenu(Action):

    le = BUILD_1_06
    id = (0x65, 0x66)
    size = 1
    apm = True

    def __init__(self, f, player_id, action_block):
        super(HeroSkillSubmenu, self).__init__(f, player_id, action_block)

class BuildingSubmenu(Action):

    le = BUILD_1_06
    id = (0x66, 0x67)
    size = 1
    apm = True

    def __init__(self, f, player_id, action_block):
        super(BuildingSubmenu, self).__init__(f, player_id, action_block)

class MinimapSignal(Action):

    le = BUILD_1_06
    id = (0x67, 0x68)
    size = 13
    apm = False

    def __init__(self, f, player_id, action_block):
        super(MinimapSignal, self).__init__(f, player_id, action_block)
        offset = 1
        x = b2f(action_block[offset:offset+DWORD])
        offset += DWORD
        y = b2f(action_block[offset:offset+DWORD])
        offset += DWORD
        self.loc = (x, y)

    def __str__(self):
        s = super(MinimapSignal, self).__str__()
        return '{0} at ({1:.3%}, {2:.3%})'.format(s, self.loc[0]/MAXPOS, 
                                                     self.loc[1]/MAXPOS) 

class ContinueGameB(Action):

    le = BUILD_1_06
    id = (0x68, 0x69)
    size = 17
    apm = False

    def __init__(self, f, player_id, action_block):
        super(ContinueGameB, self).__init__(f, player_id, action_block)

class ContinueGameA(Action):

    le = BUILD_1_06
    id = (0x69, 0x6A)
    size = 17
    apm = False

    def __init__(self, f, player_id, action_block):
        super(ContinueGameA, self).__init__(f, player_id, action_block)

class UnknownScenario(Action):

    id = 0x75
    size = 2
    apm = False

    def __init__(self, f, player_id, action_block):
        super(UnknownScenario, self).__init__(f, player_id, action_block)

# has to come after the action classes 
_locs = locals()
ACTIONS = {a.id: a for a in _locs.values() if hasattr(a, 'id') and \
                                    isinstance(a.id, int) and a.id > 0}
ACTIONS_LE_1_06 = {a.id[0]: a for a in _locs.values() if hasattr(a, 'id') and \
                                    isinstance(a.id, tuple) and a.le == BUILD_1_06}
ACTIONS_GT_1_06 = {a.id[1]: a for a in _locs.values() if hasattr(a, 'id') and \
                                    isinstance(a.id, tuple) and a.le == BUILD_1_06}
ACTIONS_LE_1_14B = {a.id[0]: a for a in _locs.values() if hasattr(a, 'id') and \
                                    isinstance(a.id, tuple) and a.le == BUILD_1_14B}
ACTIONS_GT_1_14B = {a.id[1]: a for a in _locs.values() if hasattr(a, 'id') and \
                                    isinstance(a.id, tuple) and a.le == BUILD_1_14B}
del _locs

class File(object):
    """A class that represents w3g files.

    Attributes
    ----------
    replay_length : game play time in ms
    """

    def __init__(self, f):
        """Parameters
        ----------
        f : file handle or str of path name
        """
        # init
        opened_here = False
        if isinstance(f, str):
            opened_here = True
            f = io.open(f, 'rb')
        self.f = f
        self.loc = 0

        # read in
        self._read_header()
        self._read_blocks()

        # clean up 
        if opened_here:
            f.close()

    def __del__(self):
        if not self.closed:
            self.f.close()

    def __enter__(self):
        return self

    def __exit__(self ,type, value, traceback):
        if not self.closed:
            self.f.close()

    @property
    def loc(self):
        return self.f.tell()

    @loc.setter
    def loc(self, value):
        self.f.seek(value)

    @property
    def closed(self):
        return self.f.closed

    def _read_header(self):
        f = self.f
        self.loc = 28
        self.header_size = b2i(f.read(DWORD))
        self.file_size_compressed = b2i(f.read(DWORD))
        self.header_version = hv = b2i(f.read(DWORD))
        self.file_size_decompressed = b2i(f.read(DWORD))
        self.nblocks = b2i(f.read(DWORD))
        self.loc = 0x30
        if hv == 0:
            self.loc += WORD
            self.version_num = b2i(f.read(WORD))
        elif hv == 1:
            self.version_id_str = f.read(DWORD)[::-1].decode()
            self.version_num = b2i(f.read(DWORD))
        else:
            raise ValueError("Header must be either v0 or v1, got v{0}".format(hv))
        self.build_num = b2i(f.read(WORD))
        self.flags = f.read(WORD)
        iflags = b2i(self.flags)
        self.singleplayer = (iflags == 0)
        self.multiplayer = (iflags == 0x8000)
        self.replay_length = b2i(f.read(DWORD))
        self.header_checksum = b2i(f.read(DWORD))

    def _read_blocks(self):
        f = self.f
        self.loc = self.header_size
        data = b''
        for n in range(self.nblocks):
            block_size = b2i(f.read(WORD))
            block_size_decomp = b2i(f.read(WORD))
            self.loc += DWORD
            raw = f.read(block_size)
            # Have to use Decompression obj rather than the decompress() func.
            # This avoids 'incomplete or truncated stream' errors
            #   dat = zlib.decompress(raw, 15, block_size_decomp)
            d = zlib.decompressobj()
            dat = d.decompress(raw, block_size_decomp)
            if len(dat) != block_size_decomp:
                raise zlib.error("Decompressed data size does not match expected size.")
            data += dat
        self._parse_blocks(data)

    def _parse_blocks(self, data):
        self.events = []
        self.clock = 0
        self._lastleft = None
        _parsers = {
            0x17: self._parse_leave_game,
            0x1A: lambda data: 5,
            0x1B: lambda data: 5,
            0x1C: lambda data: 5,
            0x1E: self._parse_time_slot,  # old blockid
            0x1F: self._parse_time_slot,  # new blockid
            0x20: self._parse_chat,
            0x22: lambda data: 6,
            0x23: lambda data: 11,
            0x2F: self._parse_countdown,
            }
        offset = self._parse_startup(data)
        data = data[offset:]
        blockid = b2i(data[0])
        while blockid != 0:
            offset = _parsers[blockid](data)
            data = data[offset:]
            blockid = b2i(data[0])

    def _parse_startup(self, data):
        offset = 4  # first four bytes have unknown meaning
        self.players = [Player.from_raw(data[offset:])]
        offset += self.players[0].size
        self.game_name, i = nulltermstr(data[offset:])
        offset += i + 1
        offset += 1  # extra null byte after game name
        # perform wacky decompression
        decomp, i = blizdecomp(data[offset:])
        offset += i + 1
        # get game settings
        settings = decomp[:13]
        self.game_speed = SPEEDS[bitfield(settings[0], slice(2))]
        vis = bits(settings[1])
        self.visibility_hide_terrain = bool(vis[0])
        self.visibility_map_explored = bool(vis[1])
        self.visibility_always_visible = bool(vis[2])
        self.visibility_default = bool(vis[3])
        self.observer = OBSERVER[vis[4] + 2 * vis[5]]
        self.teams_together = bool(vis[6])
        self.fixed_teams = FIXED_TEAMS[bitfield(settings[2], slice(1, 3))]
        ctl = bits(settings[3])
        self.full_shared_unit_control = bool(ctl[0])
        self.random_hero = bool(ctl[1])
        self.random_races = bool(ctl[2])
        self.observer_referees = bool(ctl[6])
        self.map_name, i = nulltermstr(decomp[13:])
        self.creator_name, _ = nulltermstr(decomp[13+i+1:])
        # back to less dense data
        self.player_count = b2i(data[offset:offset+4])
        offset += 4
        self.game_type = GAME_TYPES.get(b2i(data[offset]), 'unknown')
        offset += 1
        priv = b2i(data[offset])
        offset += 1
        self.ispublic = (priv == 0x00)
        self.isprivate = (priv == 0x08)
        offset += WORD  # more buffer space
        self.language_id = data[offset:offset+4]
        offset += 4
        while b2i(data[offset]) == 0x16:
            self.players.append(Player.from_raw(data[offset:]))
            offset += self.players[-1].size
            offset += 4  # 4 unknown padding bytes after each player record
        assert b2i(data[offset]) == 0x19
        offset += 1  # skip RecordID
        nstartbytes = b2i(data[offset:offset+WORD])
        offset += WORD
        nrecs = b2i(data[offset])
        offset += 1
        recsize = int((nstartbytes - DWORD - 3) / nrecs)
        assert 7 <= recsize <= 9
        rawrecs = data[offset:offset+(recsize*nrecs)]
        offset += recsize*nrecs
        self.slot_records = [SlotRecord.from_raw(rawrecs[n*recsize:(n+1)*recsize]) \
                             for n in range(nrecs)]
        self.random_seed = data[offset:offset+DWORD]
        offset += DWORD
        #self.select_mode = SELECT_MODES[b2i(data[offset])]
        offset += 1
        self.num_start_positions = b2i(data[offset])
        offset += 1
        return offset

    def _parse_leave_game(self, data):
        offset = 1
        reason = b2i(data[offset:offset+DWORD])
        offset += DWORD
        player_id = b2i(data[offset])
        offset += 1
        res = b2i(data[offset:offset+DWORD])
        offset += DWORD
        unknownflag = b2i(data[offset:offset+DWORD])
        offset += DWORD
        # compute inc
        if self._lastleft is None:
            inc = False
        else:
            inc = (unknownflag == (self._lastleft.unknownflag + 1))
        # compute closedby and reult
        if reason == 0x01:
            closedby = 'remote'
        elif reason == 0x0C:
            closedby = 'local'
        else: 
            closedby = 'unknown'
        e = LeftGame(self, player_id, closedby, res, inc, unknownflag)
        self.events.append(e)
        if self._lastleft is not None:
            self._lastleft.next = e
        self._lastleft = e
        return 14

    def _parse_time_slot(self, data):
        n = b2i(data[1:1+WORD])
        offset = 1 + WORD
        dt = b2i(data[offset:offset+WORD])
        offset += WORD
        cmddata = data[offset:n+3]
        while len(cmddata) > 0:
            player_id = b2i(cmddata[0])
            i = b2i(cmddata[1:1+WORD])
            action_block = cmddata[1+WORD:i+1+WORD]
            self._parse_actions(player_id, action_block)
            cmddata = cmddata[i+1+WORD:]
        self.clock += dt
        return n + 3

    def _parse_chat(self, data):
        player_id = b2i(data[1])
        n = b2i(data[2:2+WORD])
        offset = 2 + WORD
        flags = b2i(data[offset])
        offset += 1
        if flags == 0x10:
            mode = 'startup'
        else:
            m = b2i(data[offset:offset+DWORD])
            offset += DWORD
            mode = CHAT_MODES.get(m, None)
            if mode is None:
                mode = 'player{0}'.format(m - 0x3)
        msg, _ = nulltermstr(data[offset:])
        self.events.append(Chat(self, player_id, mode, msg))
        return n + 4

    def _parse_countdown(self, data):
        offset = 1
        m = b2i(data[offset:offset+DWORD])
        offset += DWORD
        mode = 'running' if m == 0x00 else 'over'
        secs = b2i(data[offset:offset+DWORD])
        offset += DWORD
        e = Countdown(self, mode, secs)
        self.events.append(e)
        return 9

    def _parse_actions(self, player_id, action_block):
        actions = dict(ACTIONS)
        actions.update(ACTIONS_LE_1_06 if self.build_num <= BUILD_1_06 \
                       else ACTIONS_GT_1_06)
        actions.update(ACTIONS_LE_1_14B if self.build_num <= BUILD_1_14B \
                       else ACTIONS_GT_1_14B)
        while len(action_block) > 0:
            aid = b2i(action_block[0])
            action = actions.get(aid, None)
            if action is None:
                return 
            e = action(self, player_id, action_block)
            self.events.append(e)
            action_block = action_block[e.size:]

    @lru_cache(13)
    def slot_record(self, pid):
        records = self.slot_records
        for sr in records:
            if sr.player_id == pid:
                break
        else:
            raise ValueError("could not find slot record for player ID {0}".format(pid))
        return sr

    @lru_cache(13)
    def player(self, pid):
        players = self.players
        if pid < len(players):
            p = players[pid]
            if p.id == pid:
                return p
        for p in players:
            if p.id == pid:
                break
        else:
            p = self.slot_record(pid)
        return p

    @lru_cache(13)
    def player_name(self, pid):
        try:
            p = self.player(pid)
        except ValueError:
            return "unknown"
        if isinstance(p, SlotRecord):
            return 'observer'
        return p.name

    @lru_cache(13)
    def player_race(self, pid):
        p = self.player(pid)
        if p.race == 'none' and isinstance(p, Player):
            p = self.slot_record(pid)
        if p.race == 'none':
            # guess race from the units used durring the first few seconds
            for e in self.events[:50]:
                if e.player_id != pid:
                    continue
                if hasattr(e, 'ability') and e.ability in ITEMS_TO_RACE:
                    return ITEMS_TO_RACE[e.ability]
        return p.race

    def print_apm(self):
        acts = {p.id: 0 for p in self.players}
        for e in self.events:
            if e.apm:
                acts[e.player_id] += 1
        mins = self.clock / (60 * 1000.0)
        m = "Actions per minute over {0:.3} min".format(mins)
        print('-' * len(m))
        print(m)
        for pid, act in sorted(acts.items()):
            if act == 0:
                continue
            print("  {0}: {1:.5}".format(self.player_name(pid), act/mins))

    def player_apm(self):
        player_apm = {}
        acts = {p.id: 0 for p in self.players}
        for e in self.events:
            if e.apm:
                acts[e.player_id] += 1
        mins = self.clock / (60 * 1000.0)
        for pid, act in sorted(acts.items()):
            if act == 0:
                continue
            player_apm[pid] = act/mins
        return player_apm

    def timeseries_actions(self):
        """Returns timeseries of cummulative number of actions, as measured
        by actions per minute. 
        """
        acts = {p.id: ([0], [0]) for p in self.players}
        for e in self.events:
            if not e.apm:
                continue
            t, a = acts[e.player_id]
            if e.time == t[-1]:
                a[-1] += 1
            else:
                t.append(e.time)
                a.append(a[-1] + 1)
        acts = {pid: (t, a) for pid, (t, a) in acts.items() if len(t) > 1}
        return acts

    def timegrid_actions(self, dt=1000, dur=120*60*1000):
        """Returns timeseries of cummulative number of actions, as measured
        by actions per minute, but on an evenly spaced grid of dt miliseconds
        of duration dur [miliseconds]. Defaults to 1 second time steps over 2 hrs.
        """
        nsteps = (dur//dt) + 1
        acts = {p.id: [0, 0] for p in self.players}
        for e in self.events:
            if not e.apm:
                continue
            a = acts[e.player_id]
            if e.time//dt == len(a) - 2:
                a[-1] += 1
            else:
                a.append(a[-1] + 1)
        acts = {pid: a + a[-1:]*(nsteps - len(a)) for pid, a in acts.items() 
                                                  if len(a) > 2}
        return acts

    def winner(self):
        for e in self.events[-1:-300:-1]:
            if not isinstance(e, LeftGame):
                continue
            result = e.result()
            if result == 'won':
                return e.player_id
            elif result == 'lost':
                players = [sr.player_id for sr in self.slot_records \
                           if sr.team < 12 and sr.player_id > 0]
                winner = [pid for pid in players if pid != e.player_id][0]
                return winner
        # if no one won or lost, find out who said gg and left
        players = {sr.player_id for sr in self.slot_records \
                   if sr.team < 12 and sr.player_id > 0}
        for e in self.events[-1:-300:-1]:
            if not isinstance(e, LeftGame):
                continue
            if e.player_id not in players:
                continue
            if e.result() != 'left':
                continue
            chats = {c.msg.lower() for c in self.events[-300:] \
                        if isinstance(c, Chat) and c.player_id == e.player_id}
            if 'g' in chats or 'gg' in chats:
                # is loser
                winner = [pid for pid in players if pid != e.player_id][0]
                return winner
        raise RuntimeError("Winner could not be found")

def main():
    f = File(sys.argv[1])
    for event in f.events:
        print(event)
    f.print_apm()
    print('-' * 10)
    print('The winner is {0}'.format(f.player_name(f.winner())))
    #print(f.version_num)
    #print(f.build_num)

if __name__ == '__main__':
    main()
