import random
from discord import File
class Card:
    '''κλάση φύλλων τράπουλας'''
    gr_names = {'s': 'Σπαθί ♣', 'c': 'Μπαστουνι ♠️', 'h': 'Κούπα ♥', 'd': 'Καρό ♦',
                'A': 'Άσσος', '2': 'Δύο', '3':'Τρία', '4':'Τέσσερα', '5':'Πέντε', '6':'Έξι', '7':'Επτά', '8':'Οκτώ',
                '9': 'Εννιά', 'T': 'Δέκα', 'J': 'Βαλές', 'Q':'Ντάμα', 'K': 'Ρήγας'}
    eng_names = {'s': 'Spades ♣', 'c': 'Clubs ♠️', 'h': 'Hearts ♥', 'd': 'Diamonds ♦',
                'A': 'Ace', '2': 'Two', '3':'Three', '4':'Four', '5':'Five', '6':'Six', '7':'Seven', '8':'Eight',
                '9': 'Nine', 'T': 'Ten', 'J': 'Jack', 'Q':'Queen', 'K': 'King'}
    the_cards = []
    def __init__(self, value, symbol):
        self.value = value.upper().strip()
        self.symbol = symbol.lower().strip()
        self.img = f"crds/{self.symbol}{self.value}.png"
        Card.the_cards.append(self)

    def load_card_image(self):
        with open(self.img, "rb") as fh:
            f = File(fh, filename=self.img)
        return f

    def __str__(self):
        return self.value+self.symbol
    
    def detailed_info(self):
        if self.value in Card.gr_names and self.symbol in Card.gr_names:
            return Card.gr_names[self.value]+ ' ' + Card.gr_names[self.symbol]
        else: return ''

class Deck():
    '''κλάση που υλοποιεί τράπουλα για παιχνίδια με χαρτιά'''
    symbols = "shcd" #  οι κατηγορίες από φύλλα, spade,heart,club,diamonds
    values =  "A23456789TJQK" # οι αξίες που μπορεί να έχουν τα φύλλα
    def __init__(self):
        self.content = [] # χαρτιά που βρίσκονται στην τράπουλα
        self.pile = [] # χαρτιά που έχουν μοιραστεί
        for s in Deck.symbols:
            for v in Deck.values:
                self.content.append(Card(v,s))
    def shuffle(self):
        random.shuffle(self.content)
    def draw(self):
        if len(self.content)< 1 : return 'empty deck'
        drawn_card = self.content.pop(0)
        self.pile.append(drawn_card)
        return drawn_card
    def collect(self):
        self.content += self.pile
        self.pile = []
    def __str__(self):
        s = ''
        cnt = 0 # μετρητής φύλλων για εκτύπωση, τυπώνουμε φύλλα σε σειρές των 13
        for i in self.content:
            s=s+str(i)+' '
            cnt += 1
            if cnt%13 == 0: s=s+'\n'
        if s[-1] != '\n': s += '\n'
        return s
