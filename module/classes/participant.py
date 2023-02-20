# Importing necessary Packages
import pandas as pd
import numpy as np
import os
from module.settings import settings

class participant():
    '''
    A class to represent a participant in a game of blackjack.
    
    Attributes
    ----------
    soft_strategy: pd.DataFrame
        The strategy the participant used for soft totals.
        
    hard_strategy: pd.DataFrame
        The strategy the participant used for hard totals.
        
    cards: list
        A list that represents cards drawn by the participants.
        
    possible: list
        A list that represents the possible value of the given cards. Starts
        with a list with length of 1 and value of 0.
        
    value: int
        The card value that represents the total value of the card. If the
        participant has more than 1 possible value of cards due to Ace, this
        value will take the maximum value.
        
    ptype: str
        The type of participant in the game, it can be a dealer ('d'), or 
        player ('p').
        
    bet: int
        The bet that the participant has put in. It is defaulted to be 0, that
        is when the participant is a dealer.
        
    active: bool
        A boolean to represent whether the current participant is still able
        to hit more or not (used when the participant is doubling).
        
    bust: bool
        A boolean to represent whether the current participant is bust or not.
        
    runV: list
        A list that represent all of the card value the participant has.
        
    runW: list
        A list that represent all of the winnings the participant has.
    
    Methods
    -------
    set_strategy(strategy = 'strategy_dealer', count = None):
        Set the strategy of the participant.
    
    set_bet(bet = 0)
        Set the bet of the participant.
    
    set_bet_counting(count)
        Set the bet of the player based on counting methods.
        
    check_bust(val1, val2)
        Check whether the palyer is bust or not based on two value added.
        
    hit(num_cards, count, double = False)
        Simulate hit a card in a blackjack game.
        
    play_strategy(dealer)
        Play a strategy based on the strategy target.
    
    result(dealer)
        Get the result between the player and the dealer, that is see whether the
        player won or loses and record the result to runV and runW.
        
    reset(running = False)
        Reset the participant status and condition for the new game, that is resetting 'cards',
        'value', 'active' and 'bust'. Can also be used to reset the player's running 
        winnings and card values.
    '''

    def __init__(self, ptype = 'p'):
        self.ptype = ptype
        self.reset(True)
    
    def set_strategy(self, strategy = 'strategy_dealer', count = None, num_cards = None):
        '''
        Set the strategy of the participant.
        
        Parameters
        ----------
        strategy: str
            A string that indicates the folder name of the strategy. The folder
            should include two csv files 'hard_totals.csv' and 'soft_totals.csv'
            that indicates what to do for each situation.
        '''
        main_path   = os.path.join('strategy', strategy)
        self.soft_strategy = pd.read_csv(os.path.join(main_path, 'soft_totals.csv'), index_col = 0)
        self.hard_strategy = pd.read_csv(os.path.join(main_path, 'hard_totals.csv'), index_col = 0)
        
        f = open(os.path.join(main_path, 'strategy.txt'))
        if 'True' in list(f.readlines())[-1]: self.set_bet_counting(count, num_cards)
        
    def set_bet(self, bet = None):
        '''
        Set the bet of the player.
        
        Parameters
        ----------
        bet: int
            The bet value.
        '''
        if bet == None: self.bet = settings.MIN_BET
        else: self.bet = bet
    
    def set_bet_counting(self, count, num_cards):
        '''
        Set the bet of the player based on counting methods.
        
        Parameters
        ----------
        count: int
            An integer that represent the current running count, for counting
            method.
        num_cards: list
            A list that represents the count of each individual card in the
            deck.
        '''
        true_count = count / sum(num_cards) * settings.N_CARD_EACH_DECK * len(settings.CARDS)
        bet_value  = max((true_count - 1) * settings.MIN_BET, 0)
        if bet_value < settings.MIN_BET: self.set_bet(0)
        else: self.set_bet(bet_value)
    
    def check_bust(self, val1, val2):
        '''
        Check whether the palyer is bust or not based on two value added.
        
        Parameters
        ----------
        val1: int
            Represent the value of the first card.
        val2: int
            Represent the value of the second card.
            
        Return
        ------
        A boolean to represent whether the participant has bust or not.
        '''
        # If the participant type is dealer, 22 is still considered not bust, but standoff.
        dealer_stdoff = 1 if self.ptype == 'd' else 0
        if val1 + val2 <= 21 + dealer_stdoff: return True
        else: return False
    
    def hit(self, num_cards, count, double = False):
        '''
        Simulate hit a card in a blackjack game.
        
        Parameters
        ----------
        num_cards: list
            A list that represents the count of each individual card in the
            deck.
        count: int
            An integer that represent the current running count, for counting
            method.
        double: bool
            A boolean that indicates whether the player wants to double the bet
            as well or not. If the player doubles, it changes the active status
            to False.
        
        Return
        ------
        updated_num_cards, updated_count
        '''
        # Calculate probability based on number of card in the deck
        prob  = [num_card/sum(num_cards) for num_card in num_cards]
        index = np.random.choice(len(settings.CARDS), replace = True, p = prob)
        
        # Simulate the card and value that has been pulled
        card  = settings.CARDS[index]
        value = settings.VALUE[index]
               
        # Update num_cards and count
        updated_num_cards = num_cards.copy()
        updated_num_cards[index] = updated_num_cards[index] - 1
        updated_count = count + settings.CARDS_COUNT[index]
        
        # Calculate the possible values based on cards drawn
        if type(value) == list: self.possible = [val1 + val2 for val1 in self.possible for val2 in value if self.check_bust(val1, val2)]
        else: self.possible = [val1 + value for val1 in self.possible if self.check_bust(val1, value)]
        if len(self.possible) == 0: self.bust = True
        
        # Update the attributes of the participant
        self.possible = list(set(self.possible))
        self.cards.append(card)
        self.value = 0 if self.bust else np.max(self.possible)
        if double:
            self.bet = self.bet * 2
            self.active = False
        
        return updated_num_cards, updated_count
    
    def play_strategy(self, num_cards, count, dealer = None):
        '''
        Play a strategy based on the strategy target.
        
        Parameters
        ----------
        num_cards: list
            A list that represents the count of each individual card in the
            deck.
        count: int
            An integer that represent the current running count, for counting
            method.
        dealer: participant
            The object that represents a dealer, that is a participant with ptpye 'd'.
        
        Return
        ------
        updated_num_cards, updated_count
        '''
        
        action = ''
        updated_num_cards, updated_count = num_cards.copy(), count

        while action != 'S' and not self.bust and self.active:
            if len(self.possible) > 1: 
                if dealer == None: action = self.soft_strategy['Value'][self.value]
                else: action = self.soft_strategy[str(dealer.value)][self.value]
            else: 
                if dealer == None: action = self.hard_strategy['Value'][self.value]
                else: action = self.hard_strategy[str(dealer.value)][self.value]

            if action == 'H': updated_num_cards, updated_count = self.hit(updated_num_cards, updated_count)
            elif action == 'D': updated_num_cards, updated_count = self.hit(updated_num_cards, updated_count, True)

        return updated_num_cards, updated_count
        
    def result(self, dealer):
        '''
        Get the result between the participant and the dealer, that is see whether the
        participant won or loses and record the result to runV and runW. Note that
        blackjack returns 3:2.
        
        Parameters
        ----------
        dealer: participant
            The object that represents a dealer, that is a participant with ptpye 'd'.
        '''
        # Initiate a variable to represent whether the player wins, loses or standoff
        # -1 indicates losing, 0 indicates standoff and 1 indicates winning
        # 2 indicates the player gets blackjack on the 2nd card
        final_result = 0
        
        # Check the player bust type then dealer bust type
        if self.bust: final_result = -1
        elif dealer.bust: final_result = 1
        
        # Check whether the player gets blackjack
        if len(self.cards) == 2 and self.value == 21: final_result = 2
        elif self.value == 21 or len(self.cards) >= 5: final_result = 1
        
        # Check whether dealer card is 22 (standoff)
        if dealer.value == 22: final_result = 0
        
        # Check whether the dealer cards are lower than or higher than player
        if dealer.value > self.value: final_result = -1
        elif dealer.value < self.value: final_result = 1
        
        self.runV.append(self.value)
        if final_result == 0: self.runW.append(0)
        elif final_result == -1: self.runW.append(-self.bet)
        elif final_result == 1: self.runW.append(self.bet)
        elif final_result == 2: self.runW.append(self.bet * 1.5)
        
        self.reset()
        
    def reset(self, running = False):
        '''
        Reset the participant status and condition for the new game, that is resetting 'cards',
        'possible', 'value', 'bet', 'active' and 'bust'. Can also be used to reset the 
        participant's running winnings and card values.
        
        Parameters
        ----------
        running: bool
            If this is True then it also resets 'runV' and 'runW' to empty list.
        '''
        # Reset standard attributes
        self.cards, self.possible = [], [0]
        self.value, self.bet      = 0, 0
        self.active, self.bust    = True, False
        if running: self.runV, self.runW = [], []