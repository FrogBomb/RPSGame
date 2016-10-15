# -*- coding: utf-8 -*-
"""
Created on Sun Oct  9 15:25:46 2016

@author: Tom Blanchet

Example code for integrating a neural network
into an ai for the rps game.
"""

from rpsGame import RPSPlayer, RPSCustomVsGame
import numpy as np
from neuralNetwork import NeuronLayer as NL, sigmoid
import random


#I left this class mostly empty since I don't know what kind of network
#you want to try to build. I put in a bunch of comments to try to help.
class RPSNeuronLayer(NL):
    #I'll use this list parameter to help translate
    #into "neuron language" in the _translateThrow method
    _symbols = ['r', 'p', 's']

    def __init__(self, bufferSize=7):
        
        #Build the neuron layer. The output will
        #attempt to predict the player's move, and the
        #AI's choice (accessed via predict) will be randomly decided based on
        #the network response.
        super().__init__(bufferSize*4, len(self._symbols), activationFunc=sigmoid)
        #Buffer :: [[win, r, p, s]], size = bufferSize
        #The tail element of the buffer is the most recent.
        self._buffer = [[0.1]+[0.1]*len(self._symbols)]*bufferSize
        return
        
    def feed(self, lastOpThrow, didWin):
        #Basically, if either of
        #the inputs are none, do nothing.
        #This is just to keep going
        #in case something breaks for some reason.
        if(lastOpThrow == None):
            return
        if(didWin == None):
            return
        
        #Train based on the results.
        target = self._translateThrow(lastOpThrow)
        self.train(np.array(self._buffer).flatten(), target, 0.03)
        
        #Push the new outcome to the end of the buffer.
        self._appendBuffer(lastOpThrow, didWin)
        
        
    def predict(self):

        #we get a random number in [0, sum(raw_nl_out)), and subtract from that number
        #with the outputs until it is less than or equal to 0, and we
        #take that symbol as the prediction for the opponent's play.
        raw_nl_out = self(np.array(self._buffer).flatten())
#        print(raw_nl_out, self._symbols)
        roll = random.random()*sum(raw_nl_out)
        
        #break the loop when roll is non-positive. "i" will
        #then be the symbol index of the prediction for the opponents play.
        for i in range(len(raw_nl_out)):
            roll -= raw_nl_out[i]
            if roll <= 0:
                break
        op_play_guess = i
        
        return self._symbols[(op_play_guess + 1)%len(self._symbols)]
    
    def _translateThrow(self, throw):
        #  throw -> array
        #  'r' -> [.99, .01, .01]
        #  'p' -> [.01, .99, .01]
        #  's' -> [.01, .01, .99]
        return [.9 if _s == throw else 0.1 for _s in self._symbols]

    def _appendBuffer(self, throw, didWin):
        self._buffer.append([.9 if didWin else .1] +\
                            self._translateThrow(throw))
        del self._buffer[0]
          
        
        
class RPSPlayer_2PAiWithNN(RPSPlayer):
    """AI designed for a two player game
    
    The neural network nn will take in new data
    through the nn.feed(lastOpThrow, didWin) method,
    and will predict the best throw through 
    the nn.predict() method.
    
    (nn.feed should be able to take None(s) by default.)
    """
    def __init__(self, engine, neuralNetwork):
        
        ##This line makes it so that
        ##everything happens that happens when
        ##a new RPSPlayer is instanciated
        super().__init__(engine)
        
        #Stuff here is to keep the nn stuff
        #here, and to 
        self._nn = neuralNetwork()
        self._lastOpThrow = None
        self._didWinLast = None
        
    def giveThrows(self, throwList):
        
        #This line is good practice in case of
        #multiple inheritance. Just runs the
        #method of the superclass (in this case, RPSPlayer).
        super().giveThrows(throwList)
        
        #This will save the throw of the opponent.
        self._lastOpThrow = throwList[1-self.id]
    
    def giveWins(self, winNumber):
        #This line runs the giveWins method of the superclass
        #so that we don't have to rewrite however the game
        #internally keeps wins.
        super().giveWins(winNumber)
        
        #To track if we won the last game
        #if winNumber is 0, not winNumber is True,
        #so not not winNumber is False. Otherwise,
        #not winNumber is False, so not not winNumber
        #is True.
        self._didWinLast = not not winNumber
    
    def getThrow(self):
        self._nn.feed(self._lastOpThrow, self._didWinLast)
        return self._nn.predict()
        
def main():
    g = RPSCustomVsGame(RPSPlayer_2PAiWithNN, RPSNeuronLayer)
    g.loop()
    print("player score:", g.players[0].wins)
    print("AI score:", g.players[1].wins)
    return g

if __name__ == "__main__":
    lastGame = main()