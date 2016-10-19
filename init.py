from rpsGameAi import *
def main():
    g = RPSCustomVsGame(RPSPlayer_2PAiWithNN, RPSNeuronLayer)
    g.loop()
    print("player score:", g.players[0].wins)
    print("AI score:", g.players[1].wins)
    return g

if __name__ == "__main__":
    lastGame = main()
