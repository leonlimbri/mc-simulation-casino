from . import participant

class blackjack():
    '''
    A class to simulate a game of blackjack.
    
    Attributes
    ----------
    players: list
        The list of players.
        
    dealer: player
        The dealer.
    
    num_cards: list
        A list that represents the count of each individual card in the
        deck.
        
    count: int
        An integer that represent the current running count, for counting
        method.
        
    Methods
    -------
    add_player(player)
        Add a player to the game.
    
    play()
        Start the game by dealing two cards to player and 1 card for the dealer,
        then let each players run their strategy and let dealer play their strategy.
    
    '''
    
    def __init__(self, num_cards, count):
        self.players = []
        self.dealer  = participant.participant('d')
        self.dealer.set_strategy()
        self.num_cards = num_cards
        self.count = count
        
    def add_player(self, *player):
        '''
        Add a player to the game.
        
        Parameters
        ----------
        player: player
            A player to be added.
        '''
        for p in player:
            self.players.append(p)
    
    def play(self):
        '''
        Start the game by dealing two cards to player and 1 card for the dealer,
        then let each players run their strategy and let dealer play their strategy.
        
        Return
        ------
        updated_num_cards, updated_count
        '''
        # Deal initial cards
        for player in self.players: self.num_cards, self.count = player.hit(self.num_cards, self.count)
        self.num_cards, self.count = self.dealer.hit(self.num_cards, self.count)
        for player in self.players: self.num_cards, self.count = player.hit(self.num_cards, self.count)
        
        for player in self.players: self.num_cards, self.count = player.play_strategy(self.num_cards, self.count, dealer)
        self.num_cards, self.count = self.dealer.play_strategy(self.num_cards, self.count)
        for player in self.players: player.result(self.dealer)
        
        return self.num_cards, self.count