import random
import re
import csv
import PlayingCards
from datetime import datetime


class Game:

    def __init__(self, bet, user):
        self.bet = float(bet)
        self.user = user
        self.counter = -1
        self.__seed = self.calculateSeed()
        self.result = None


    def calculateSeed(self):
        return hash((str(datetime.utcnow()), str(self.user.id)))

    def play(self):
        print(f"{self.user.name} wagerd {self.bet} on a Game with seed {self.__seed}")


class Coinflip(Game):

    def __init__(self, bet, user):
        super().__init__(bet, user)
        
    
    def play(self, reaction):
        self._Game__seed = self.calculateSeed()
        random.seed(self._Game__seed)
        positions = ["heads", "tails"]
        if random.choice(positions) == reaction:
            #print(f"{self.user.name} won {Coinflip.__name__} \t Seed: {self._Game__seed}")
            return True
        else:
            #print(f"{self.user.name} lose {Coinflip.__name__} \t Seed: {self._Game__seed}")
            return False

    def simulate(self, simulations, NumberOfGames, reaction):
        for x in range(0,simulations):
            totalStake = 0
            totalWin = 0
            games = 0 
            for i in range(0,NumberOfGames):
                r = self.play(reaction)
                games+=1
                totalStake+=bet
                if r:
                    totalWin+=bet

            RTP = (totalWin/totalStake)*100 

            print(f"Bet:{bet} Games:{games} Total Stake:{totalStake} Total Win:{totalWin} RTP:{RTP:.2f}%")


    def __str__(self):
        return f"{Coinflip.__name__} {self.user.name} {self.bet} {self.reaction.emoji} {self._Game__seed}"
        
class Slot(Game):
    values = {
        ":lemon:" :0.25,
        ":tangerine:" :0.50,
        ":cherries:":1, 
        ":grapes:" :2, 
        ":eggplant:":5, 
        ":watermelon:":17, 
        ":bell:":40, 
        ":crown:":60, 
        ":seven:":80, 
        ":gem:":100
        }
    reel = [":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",":lemon:",
            ":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",":tangerine:",
            ":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",":cherries:",
            ":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",":grapes:",
            ":eggplant:",":eggplant:",":eggplant:",":eggplant:",":eggplant:",":eggplant:",
            ":watermelon:",":watermelon:",":watermelon:",":watermelon:",":watermelon:",":watermelon:",
            ":bell:",":bell:",":bell:",":bell:",":bell:",
            ":crown:",":crown:",":crown:",":crown:",
            ":seven:",":seven:",
            ":gem:"]
    def __init__(self, bet, user):
        super().__init__(bet, user)
        self.counter=0
        self.profit_loss=0
    
    def play(self):
        self._Game__seed = self.calculateSeed()
        random.seed(self._Game__seed)
        results = []
        self.counter+=1
        for i in range(0, 5):
            results.append(random.choice(Slot.reel))


        if results[0]==results[1] and results[1]==results[2] and results[2]==results[3] and results[3]==results[4]:
            multiplier = Slot.values[results[0]]*20
            self.profit_loss += self.bet*multiplier
            return (multiplier, results) 
        elif results[0]==results[1] and results[1]==results[2] and results[2]==results[3]:
            multiplier = Slot.values[results[0]]*8
            self.profit_loss += self.bet*multiplier
            return (multiplier, results)
        elif results[0]==results[1] and results[1]==results[2]:
            multiplier = Slot.values[results[0]]*4
            self.profit_loss += self.bet*multiplier
            return (multiplier, results)
        elif results[0]==results[1]:
            multiplier = Slot.values[results[0]]*2
            self.profit_loss += self.bet*multiplier
            return (multiplier, results)
        else:
            self.profit_loss = self.profit_loss - self.bet
            return (0, results)
        
    def simulate(self, simulations, NumberOfGames):
        for x in range(0,simulations):
            totalStake = 0
            totalWin = 0
            games = 0
            sims = []
            for i in range(0,NumberOfGames):
                r = self.play()
                row = [r[0], " ".join(map(str, r[1])), self._Game__seed]
                sims.append(row) 
                games+=1
                totalStake+=bet
                totalWin+=bet*r[0]
            
            with open('slot_simulations.csv', mode="w") as sims_file:
                sims_writer = csv.writer(sims_file, delimiter=',')
                sims_writer.writerows(sims)

            RTP = (totalWin/totalStake)*100 

            print(f"Bet:{bet} Games:{games} Total Stake:{totalStake} Total Win:{totalWin} RTP:{RTP:.2f}%")


    def __str__(self):
        return f"{Slot.__name__} {self.user.name} {self.bet} {self.reaction.emoji} {self._Game__seed}"


class FindTheKing(Game):
    def __init__(self, bet, user):
        super().__init__(bet, user)

    def play(self, reaction):
        self.reaction = reaction
        self._Game__seed = self.calculateSeed()
        random.seed(self._Game__seed)

        if reaction == "red":
            self.reaction = 0
        elif reaction == "green":
            self.reaction = 1
        elif reaction == "blue":
            self.reaction = 2
        else:
            self.reaction = None
            return None

        positions = ["<:cardSpadesK:853266560361824256>", "<:cardJoker:853266881603829791> ", "<:cardJoker:853266881603829791> "]
        random.shuffle(positions)
    
        if positions[self.reaction]=="<:cardSpadesK:853266560361824256>":
            return (True, positions)
        else:
            return (False, positions)
    
    def simulate(self, simulations, NumberOfGames, reaction):
        for x in range(0,simulations):
            totalStake = 0
            totalWin = 0
            games = 0
            sims = []
            for i in range(0,NumberOfGames):
                r = self.play(reaction)
                row = [reaction.emoji.name, r[0], " ".join(map(str, r[1])), self._Game__seed]
                sims.append(row) 
                games+=1
                totalStake+=bet
                totalWin+=bet*r[0]
            
            with open('ftk_simulations.csv', mode="w") as sims_file:
                sims_writer = csv.writer(sims_file, delimiter=',')
                sims_writer.writerows(sims)

            RTP = (totalWin/totalStake)*100 

            print(f"Bet:{bet} Games:{games} Total Stake:{totalStake} Total Win:{totalWin} RTP:{RTP:.2f}%")

    def __str__(self):
        return f"{FindTheKing.__name__} {self.user.name} {self.bet} {self.reaction.emoji} {self._Game__seed}"

class Dice(Game):
    def __init__(self, bet, user):
        super().__init__(bet, user)

    def play(self):
        self._Game__seed = self.calculateSeed()
        random.seed(self._Game__seed)

        dice1, dice2 = random.randrange(1,7), random.randrange(1,7) 
        dices = [dice1, dice2]
        s = dice1 + dice2

        if s < 7: 
            return (0, dices)
        elif s < 10:
            return (1, dices)
        elif s <12:
            return (2, dices)
        elif s<13:
            return (12, dices)
        else:
            return None
        
    def simulate(self, simulations, NumberOfGames):
        for x in range(0,simulations):
            totalStake = 0
            totalWin = 0
            games = 0
            sims = []
            for i in range(0,NumberOfGames):
                r = self.play()
                row = [r[0], " ".join(map(str, r[1])), self._Game__seed]
                sims.append(row) 
                games+=1
                totalStake+=bet
                totalWin+=bet*r[0]
            
            with open('dice_simulations.csv', mode="w") as sims_file:
                sims_writer = csv.writer(sims_file, delimiter=',')
                sims_writer.writerows(sims)

            RTP = (totalWin/totalStake)*100 

            print(f"Bet:{bet} Games:{games} Total Stake:{totalStake} Total Win:{totalWin} RTP:{RTP:.2f}%")


    def __str__(self):
        return f"{Dice.__name__} {self.user.name} {self.bet} {self._Game__seed}"


class BlackJack(Game):
    def __init__(self, bet, user):
        super().__init__(bet, user)
        self.deck = PlayingCards.Deck()
        self.deck.shuffle()
        self.player = []
        self.player_score = 0
        self.banker = []
        self.banker_score = 0

    def _check_if_exceeded(self, score):
        if score > 21:
            return True
        else: False

    def _calculate_value(self, card, score):
        if card.facedDown:
            return 0

        if card.value.isdigit(): 
            return int(card.value)
        elif card.value == 'A':
            if score<11:
                return 11
            else:     
                return 1
        else: 
            return 10 # αφορά τις τιμές T,J,Q,K

    def check_winner(self):
        ''' 
            0: player lost
            1: draw
            2: player won
        '''
        if self.player_score>self.banker_score:
            return 2
        elif self.player_score==self.banker_score:
            return 1
        else:
            return 0

    def play(self):

        for card in range(2):
            card = self.deck.draw()
            self.player.append(card)

            card = self.deck.draw()
            self.banker.append(card)          

        for card in self.player:
            card.facedDown=False
            self.player_score += self._calculate_value(card, self.player_score)
        
        self.banker[0].facedDown=False
        self.banker_score += self._calculate_value(self.banker[0], self.banker_score)

        if self.player_score==21:
            return 21
        
        return True

    def hit(self):
        ''' True: player can hit again
            0: player passed 21 (cant hit again)
            21: player hits 21
        '''
        card = self.deck.draw()
        card.facedDown=False
        self.player.append(card)
        self.player_score += self._calculate_value(card, self.player_score)
        
        if self._check_if_exceeded(self.player_score):
            return 0
        
        if self.player_score==21:
            return 21

        return True

    def stand(self):
        ''' 2 means player wins
            0 means banker wins
        '''

        self.banker[1].facedDown=False
        self.banker_score += self._calculate_value(self.banker[1], self.banker_score)

        while self.banker_score<17:
            card = self.deck.draw()
            card.facedDown=False
            self.banker.append(card)
            self.banker_score += self._calculate_value(card, self.banker_score)
        
            if self._check_if_exceeded(self.banker_score):
                return 2
        
            if self.banker_score==21:
                return 0

        return self.check_winner()

    def __str__(self):
        return f"{FindTheKing.__name__} {self.user.name} {self.bet} {self.reaction.emoji} {self._Game__seed}"


if __name__ == "__main__":

    class FakeUser:
        def __init__(self):
            self.name = 'Tasos'
            self.id = 420058166651256842

    class FakeEmoji:
        def __init__(self):
            self.name = 'cardBackGreen'
            self.id = 853266658201436190

        def __repr__(self):
            return f"<:{self.name}:{self.id}>"

    class FakeReaction:
        def __init__(self):
            self.emoji = FakeEmoji()
            self.id = 809385851334557706


    user = FakeUser()
    reaction = FakeReaction()
    bet = 1
    #c = Coinflip(bet, user)
    #c.simulate(1, 10)

    #s = Slot(bet, user)
    #s.simulate(1, 1000000)

    #f=FindTheKing(bet, user)
    #f.simulate(1, 1000000, reaction)

    d=Dice(bet, user)
    d.simulate(1, 1000000)


    