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

def zeros(**kwargs):
    return np.zeros(kwargs['size'])

#I left this class mostly empty since I don't know what kind of network
#you want to try to build. I put in a bunch of comments to try to help.
class RPSNeuronLayer(NL):
    #I'll use this list parameter to help translate
    #into "neuron language" in the _translateThrow method
    _symbols = ['r', 'p', 's']

    def __init__(self, bufferSize=5, learnRate = .03, stability = 1.2):

        #Build the neuron layer. The output will
        #attempt to predict the player's move, and the
        #AI's choice (accessed via predict) will be randomly decided based on
        #the network response.
        self._sep = 1.0
        self._learnRate = learnRate
        self._featureNum = len(self._symbols)**2
        self._edgeSpaceAprox = min(self._learnRate*self._featureNum*stability, .45)
        featureNum = self._featureNum
        super().__init__(bufferSize*featureNum + 1, len(self._symbols),
                          activationFunc=sigmoid, sampler = zeros)
        #Buffer :: [[[(r, r), (r, p), (r, s), (p, r), ... , (s, p), (s, s)]],
        #           size = bufferSize
        #The tail element of the buffer is the most recent.
        self._buffer = [[0.0]*featureNum]*bufferSize
        return

    def __call__(self):
        return super().__call__(self._NNIn())

    def train(self, *args, **kwargs):
        super().train(self._NNIn(), *args, **kwargs)



    def feed(self, lastAiThrow, lastOpThrow):
        #Basically, if either of
        #the inputs are none, do nothing.
        #This is just to keep going
        #in case something breaks for some reason.
        if(lastOpThrow == None):
            return
        if(lastAiThrow == None):
            return

        #Train based on the results.
        edgeSpaceAprox = self._edgeSpaceAprox
        target = [edgeSpaceAprox]*len(self._symbols)
        target[self._symbols.index(lastOpThrow)] = 1.0 - edgeSpaceAprox
        self.train(target, self._learnRate)

        #Push the new outcome to the end of the buffer.
        self._appendBuffer(lastAiThrow, lastOpThrow)


    def predict(self):

        #we get a random number in [0, sum(raw_nl_out)), and subtract from that number
        #with the outputs until it is less than or equal to 0, and we
        #take that symbol as the prediction for the opponent's play.
        raw_nl_out = self()
        raw_nl_out -= min(np.min(raw_nl_out), self._edgeSpaceAprox)
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

    def _NNIn(self):
        return np.append(1.0, np.array(self._buffer).flatten())

    @staticmethod
    def _throwsToIndex(lastAiThrow, lastOpThrow):
        return 3*RPSNeuronLayer._symbols.index(lastAiThrow)\
                 + RPSNeuronLayer._symbols.index(lastOpThrow)

    def _appendBuffer(self, lastAiThrow, lastOpThrow):
        del self._buffer[0]
        outcome = [-self._sep]*self._featureNum
        outcome[self._throwsToIndex(lastAiThrow, lastOpThrow)] = self._sep
        self._buffer.append(outcome);



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
        self._lastAiThrow = None

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
        self._nn.feed(self._lastAiThrow, self._lastOpThrow)
        self._lastAiThrow = self._nn.predict()
        return self._lastAiThrow
