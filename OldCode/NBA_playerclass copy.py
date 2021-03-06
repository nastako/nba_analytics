import sys, os

reqargs = ['pts', 'fg', '3pt', 'ft', 'rb']
stats   = {'mins':0.0, 'fg':0, 'fga':0, '3pt':0, '3pta':0, 'ft':0,
         'fta':0, 'pts':0, 'stl':0, 'ast':0, 'to':0, 'blk':0,
         'rbo':0, 'rbd':0, 'rb':0, 'pf':0}
sks     = ('mins', 'fg', 'fga', '3pt', '3pta', 'ft', 'fta', 'pts',
            'stl', 'ast', 'to', 'blk', 'rbo', 'rbd', 'rb', 'pf')

class player():
    def __init__(self, name, team, ID):
        self._name          = name      # ESPN name; may need to be "names"
        self._team          = team      # ESPN team; likely needs to be "teams"
        self._ID            = ID        # Gloabl ID assigned by yours truely
        self.curgame        = None      # keeps track of the current game   
        self._gamestats     = dict()    # dict of dict, keys are gameIDs, values are stats for that game
        self._games         = set()     # set of game IDs the player has played in
        self.actionfeed     = dict()    # dict of key->game, value->actions a player has performed
        self.seasonIDs      = list()    # list of ESPN season IDs
        self.playergameIDs  = list()    # list of single-game player IDs
        #for stat in statslist:

    def _newgame(self, game, playergameID):
        '''
        Sets the gameID as the current game, and sets the
        current stats equal to 0's; also, automatically flushes old stats
        if they have not been flushed; initialize new game stats with
        the dictionary "stats" to allow for easy referencing when
        updating;
        '''
        if self.curgame not in self._games and self.curgame:
            self._flushgame()
        self.curgame        = game          # current game ID (ESPN)
        self.stats          = stats.copy()  # set current stats to NULL stats dict
        self.curactfeed     = list()        # list of (gameID, [actions]) for cur game
        self.playergameIDs.append(playergameID)
        
    def _flushgame(self):
        '''
        Adds the new game ID to the set of games played in, and
        moves the current game data to a stats dictionary with
        keys as game ids, and entries are dictionaries with stat
        handles as keys; resets current game values;
        '''
        self._games.add(self.curgame)
        self._gamestats[self.curgame] = self.stats.copy()
        self.actionfeed[self.curgame] = self.curactfeed.copy()
        self.curgame = None
        self.stats = None
        self.curactfeed = list()
        
    def getcur(self, game):
        '''
        NEED TO UPDATE SINCE "CURRENT" HAS CHANGED
        Returns dictionary of current stats, as well as name, id, and
        team;
        '''
        if game == self.curgame:
            s = self.stats.copy()
            s['Name']   = self._name
            s['ID']     = self._ID
            s['Team']   = self._team
            return s
        else:
            raise ValueError("no stats for %s for %s" % (self._name, game))

    def getgame(self, game, args=None):
        '''
        Returns dictionary of game stats, as well as name, id, and
        team;
        '''
        if game in self._games:
            s = self._gamestats[game].copy()
            if not args:
                s['Name']   = self._name
                s['ID']     = self._ID
                s['Team']   = self._team
            return s
        else:
            raise ValueError("no stats for %s for %s" % (self._name, game))

    def getgames(self):
        '''
        Returns dictionary dictionaries of game stats {game:stats},
        as well as name, id, and team (once);
        '''
        s           = dict()
        g           = list()
        s['Name']   = self._name
        s['ID']     = self._ID
        s['Team']   = self._team
        for game in self._games:
            s[game] = self.getgame(game, args=1)
            g.append(game)
        s['games']      = g
        s['statlist']   = sks
        return s
    
    def update(self, name, stat, increment):
        '''
        Checks to make sure "name" in a valid player and "stat"
        is a valid stat; if so, calls updatestat module to increment
        "stat" by "increment"; if not, returns a ValueError
        '''
        if name in playerlist:
            if stat in statlist:
                playerstats = PlayerStats[name]
                playerstats = updatestat(playerstat, stat, increment)
                PlayerStats[name] = playerstats
            else:
                raise ValueError('stat "%s" not a player stat' % stat)
        else:
            raise ValueError('player "%s" not a player' % name)

    def updatestat(self, time, stat, args):
        '''
        Updates stat "stat" in "playerstats" by "increment; I think
        there is a way to handle these together instead of writing out
        separate updates for each one...idk
        '''
        if stat.lower() in stats.keys():
            if stat.lower() in reqargs and args==None:
                return -1
            else:
                new_action = None
                if stat=='PTS':
                    self.stats['pts'] += args
                elif stat=='FG':
                    self.stats['fga'] += 1
                    if args=='Made':
                        self.stats['fg'] += 1
                    new_action = ' '.join([args, 'FG'])
                elif stat=='3PT':
                    self.stats['3pta'] += 1
                    if args=='Made':
                        self.stats['3pt'] += 1
                    new_action = ' '.join([args, '3PT'])
                elif stat=='FT':
                    self.stats['fta'] += 1
                    if args=='Made':
                        self.stats['ft'] += 1
                    new_action = ' '.join([args, 'FT'])
                elif stat in ['STL','AST','BLK','TO','PF']:
                    self.stats[stat.lower()] += 1
                    new_action = stat
                elif stat=='RB':
                    args = args.split()
                    args = [arg.split(":") for arg in args]
                    if args[2][0] > self.stats['rbo']:
                        new_action = 'RBO'
                    elif args[5][0] > self.stats['rbd']:
                        new_action = 'RBD'
                    self.stats['rbo']  = int(args[2][0])
                    self.stats['rbd']  = int(args[5][0])
                    self.stats['rb']   = int(args[2][0]) + int(args[5][0])
                elif stat=='MINS':
                    self.stats['mins'] += args
                # append line to action feed
                if new_action:
                    self.actionfeed.append([self.curgame, time, new_action])
                                        
                return 1
        else:
            return -2

    def name(self):
        return self._name

    def team(self, Year=None):
        return self._team

    def ID(self):
        return self._ID

    def games(self):
        return self._games

'''
Need to re-write this so that each instance of "game" class corresponds
to a single game, not a group of games; 
'''
class game():
    def __init__(self, fhandlepbp, fhandlenam):
        self._pbpfile = os.path.splitext(os.path.basename(fhandlepbp))[0]
        self._plafile = os.path.splitext(os.path.basename(fhandlenam))[0]
        self._home  = dict()
        self._away  = dict()
        self._teams = dict()
        self._score = dict()
        self._stats = dict()
        self.games  = []

    def _addgame(self, game, score):
        '''
        Updates home, away, teams, score for new game "game" with score
        "score";
        '''
        self.games.append(game)
        home, away = game[-3:], game[-6:-3]
        self._home[game]    = home
        self._away[game]    = away
        self._teams[game]   = (home, away)
        self._score[game]   = {home:score[home], away:score[away]}

    def _addstats(self, game, pstats, active):
        '''
        Updates the player stats for game "game"; just creates a list
        of dictionaries output from the player class for the current
        game; note that the player class returns a ValueError if a
        player name referenced in "active" dose not have their current
        game set as "game";
        ''' 
        self._stats[game] = [pstats[p].getcur(game) for p in active]
            
    def update(self, game, pstats, active, score):
        '''
        Adds the current game stats to self under heading of "game"
        '''
        self._addgame(game, score)
        self._addstats(game, pstats, active)

    def showgame(self, game):
        '''
        pprint display the stats from game "game"
        '''
        temp = getgame(self, game)
        
    def getscore(self, game):
        return self._score[game]
    
    def getteams(self, game):
        return self._teams[game]

    def getgame(self, game):
        '''
        Return a usable format of the stats from game; specifically, return
        a dictionary with player names as keys and stats as dicts, key
        "teams" with teams as values, keys with each 3-letter team abv. with
        scores as values, and keys str(3-letter team abv. + Team) with
        the list of players on that team as values;
        '''
        out     = self.getscore(game)
        home, away = self.getteams(game)
        hplay, aplay = [], []
        for p in self._stats[game]:
            if p['Team']==home:
                hplay.append(p['Name'])
            elif p['Team']==away:
                aplay.append(p['Name'])
            temp = {}
            for stat in stats:
                temp[stat] = p[stat]
            for stat in ['Name', 'ID', 'Team']:
                temp[stat] = p[stat]
            out[p['Name']] = temp
        out['home'], out['away'] = home, away
        out[home+'Team'] = hplay
        out[away+'Team'] = aplay
        return out

    def getgames(self):
        '''
        Returns the stats from all games contained in self as a dictionary
        with keys as game ids and values as returns from 'getgame(game id)";
        '''
        out = dict()
        for game in self.games:
            out[game] = self.getgame(game)
        out['statlist'] = sks
        return out

    def starters(self):
        '''
        Returns the list of starts for the game, self; used primarely in
        setting up player game IDs;
        '''

        return

    def players(self):
        '''
        Returns the list of all players (via ID?) that played in game 'self'
        '''

        return
