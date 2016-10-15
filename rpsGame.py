# -*- coding: utf-8 -*-
"""
RPS Game
10/8/2016

Tom Blanchet
"""
import random

THROW_OPTIONS = ['r', 'p', 's']
THROW_NAME_REF = {'r': "Rock", 'p': "Paper", 's':"Scissors"}

class RPSThrowError(BaseException):
    """Error when an incorrect throw is input"""
    pass

class ExitGame(BaseException):
    """Error signal to exit game"""
    pass

def assertIsThrow(throw):
    """Assert that throw is a valid RPS throw"""
    global THROW_OPTIONS
    if(throw not in THROW_OPTIONS):
        raise RPSThrowError
    return

class PlayerRegError(BaseException):
    """Error when there are aleady too many players in the game."""
    pass

class PlayError(BaseException):
    """Error when a player already made a play before the round is over."""
    def getThrow(self):
        try:
            return self.args[0]
        except IndexError:
            return None

class RPSEngine:
    ##This is an engine reference for what input beats what.
    winMap = {'r':'s', 's':'p', 'p':'r'}
    def __init__(self, numPlayers):
        """
        Make a new engine to play rock paper scissors.
        """
        self._throws = [None]*numPlayers
        self._players = [None]*numPlayers
        self.numPlayers = numPlayers
    
    def play(self, player, throw):
        """
        Tell the game that the player threw the throw
        """
        assertIsThrow(throw)
        if self._throws[player.id] == None:
            self._throws[player.id] = throw
        else:
            raise PlayError(throw)
        if(all([t!=None for t in self._throws])):
            for p in self._players:
                p.giveThrows(self._throws)
                p.giveWins(sum([self.winMap[self._throws[p.id]] == t\
                            for t in self._throws]))
            self._throws = [None]*self.numPlayers
        
    
    def register(self, player):
        """
        Register a new player for the game. Returns the player ID.
        If the game is full, raises a PlayerRegError.
        """
        try:
            ret = self._players.index(None)
            self._players[ret] = player
        except ValueError:
            raise PlayerRegError
        return ret
        
    def clearThrow(self, player):
        """
        Used to clear a throw of a player this round.
        """
        self._throws[player.id] = None
        
class RPSPlayer:
    """
    Class to play RPS with the engine.
    """
    def __init__(self, engine):
        self.wins = 0;
        self.id = engine.register(self)
        self.engine = engine
        
    def giveThrows(self, throwList):
        """
        Method used by the game engine to give the player the throws
        of the round when the round completes.
        """
        return
    def giveWins(self, winNumber):
        """
        Method used for a player to count their score in the game.
        Win number will be the number of other players in the game
        that this player beat. 
        """
        self.wins += winNumber
    def triggerPlay(self):
        """
        Sends a message to the player that it is ok
        for them to play the next round.
        """
        self.engine.play(self, self.getThrow())
    def getThrow(self):
        """
        Method used as a part of triggerPlay to determine the next throw.
        """
        global THROW_OPTIONS
        return THROW_OPTIONS[random.randint(0, len(THROW_OPTIONS)-1)]


    
class RPSInterface(RPSPlayer):
    """User interface to play RPS"""
    def giveThrows(self, throwList):
        global THROW_NAME_REF
        print("For Player " + str(self.id+1) + ", opponent(s) threw: ")
        print(*[THROW_NAME_REF[throwList[i]] for i in range(len(throwList)) if i!=self.id], sep=', ')
    def getThrow(self):
        print("You can stop the game by typing (E)xit", end="")
        throw = ""
        global THROW_OPTIONS
        while(throw not in THROW_OPTIONS):
            tmp = input("(R)ock, (P)aper, or (S)cissors?: ")
            try:
                throw = tmp[0].lower()
            except IndexError:
                pass
            if throw == "e":
                raise ExitGame
        return throw
            
#class RPSRememberer(RPSPlayer):
#    def giveThrows(self, throwList):
#        global THROW_OPTIONS
#        try:
#            self.previousRounds
#        except AttributeError:
#            self.previousRounds = []
#        self.previousRounds.append(throwList)

class RPSGameError(BaseException):
    """Error for when an RPSGame is not properly invoked."""
    pass

class RPSGame:
    """
    Base (factory) class for making an RPSGame.
    
    engineClass must be inherited from RPSEngine.
    playerClasses must be a list of classes inherited from RPSPlayer.
    engineArgs, if not None, is the list of arguements for the engine 
        invocation
    playerArgs is a list of lists of arguements for the players.
        (e.g., playerArgs[0][4] will be the fifth arguement for
        the first class in playerClass)
    """
    def __init__(self, engineClass, playerClasses, engineArgs = None,\
                 playerArgs = None):
        
        #Set default behavior
        if(engineArgs == None):
            engineArgs = []
        if(playerArgs == None):
            playerArgs = [[]]*len(playerClasses)
        
        #Validate
        if(not issubclass(engineClass, RPSEngine)):
            raise RPSGameError(engineClass, RPSEngine)
        
        for pC in playerClasses:
            if(not issubclass(pC, RPSPlayer)):
                raise RPSGameError(pC, RPSPlayer)
                
        if(len(playerClasses) != len(playerArgs)):
            raise RPSGameError("Mismatch length in playerClasses and playerArgs.")
            
        self.engine = engineClass(*engineArgs)
        self.players = [pC(self.engine, *pArgs) for pC, pArgs in\
                        zip(playerClasses, playerArgs)]
    def loop(self):
        """Main game loop."""
        while(True):
            for p in self.players:
                self.loopPrompt(p)
                try:
                    p.triggerPlay()
                except ExitGame as e:
                    return e
                except PlayError as pE:
                    self.handlePlayError(p, pE.getThrow())
                    
    def loopPrompt(self, player):
        """Prompt to print for each player during the loop."""
        print("Current player: " + str(player.id + 1))
        print("Current score : " + str(player.wins))
        
    def handlePlayError(self, player, newThrow):
        """If a player has already registered a throw this round and attempts 
        to change it, this method is called with the player and the newThrow."""
        self.engine.clearThrow(player)
        self.engine.play(player, newThrow)
    

class RPSCustomVsGame(RPSGame):
    """
    Make a basic game of RPS against a custom player
    
    customPlayerClass must inherit from RPSPlayer
    """
    def __init__(self, customPlayerClass, *args):
        playerClasses = [RPSInterface, customPlayerClass]
        engineArgs = [2]
        super().__init__(RPSEngine,\
                        playerClasses,\
                        engineArgs = engineArgs,
                        playerArgs = [[], args]
                        )
        
class RPSBasicGame(RPSCustomVsGame):
    """
    Makes a basic game of RPS against a random computer.
    """
    def __init__(self):
        super().__init__(RPSPlayer)
        
        ##Same as below:
#        self.engine = RPSEngine(2)
#        self.players = [RPSInterface(self.engine),\
#                        RPSPlayer(self.engine)]
        
                    
class RPSTwoHumanGame(RPSCustomVsGame):
    """
    Makes a two person game of RPS.
    """
    def __init__(self):
        super().__init__(RPSInterface)
        ##Same as below:
#        self.engine = RPSEngine(2)
#        self.players = [RPSInterface(self.engine), RPSInterface(self.engine)]
    def loopPrompt(self, player):
        RPSBasicGame.loopPrompt(self, player)
        print("Player " + str(player.id + 1) + " go!")
    
                    
def start(gameClass = RPSBasicGame, *args):
    g = gameClass(*args)
    g.loop()
    return g