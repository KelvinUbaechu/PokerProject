import cardUtils, ranks, pokerLogic
import cards as cds
import random
from typing import Iterable, List, Sequence, Dict, Callable, TypeVar, Optional

CardKeeper = Callable[[Sequence[cds.Card]], List[cds.Card]]
Frequency = TypeVar('Frequency', int, Callable[[Sequence[cds.Card]], Sequence[cds.Card]])

def create_sequence_target_finder(*, sequence_length: int, invalid_starters: Optional[Iterable[cds.Card]]=None) -> CardKeeper:
	'''Factory function that returns a function that returns a list of the best cards to create a sequence according to the specifications provided'''
	def get_best_sequence_targets(cards: Sequence[cds.Card]) -> List[cds.Card]:
		'''Returns a list of the best cards to create a sequence'''
		hand = cardUtils.Hand(cards)
		faces = hand.get_faces()

		target_faces = cardUtils.get_sequence_including_most_faces(
			faces=faces,
			sequence_length=sequence_length,
			invalid=invalid_starters or []
		)

		return cardUtils.get_first_cards_with_faces(cards, faces=target_faces)

	return get_best_sequence_targets

def create_face_frequency_target_finder(get_min_frequency: Frequency) -> CardKeeper:
	'''Factory function that returns a function that returns a list of the best cards to form face-frequency-based rank according to the specifications provided'''
	if not hasattr(get_min_frequency, '__call__'):
		get_min_frequency_func = lambda cards: get_min_frequency
	else:
		get_min_frequency_func = get_min_frequency

	def get_face_frequency_targets(cards: Sequence[cds.Card]) -> List[cds.Card]:
		'''Returns a list of the best cards to form face-frequency-based rank'''
		cards_to_keep = []
		hand = cardUtils.Hand(cards)

		for _, group in cardUtils.get_group_items_by_size_and_value(hand.get_groups_by_face(), reverse=True):
			if len(group) >= get_min_frequency_func(cards):
				cards_to_keep.extend(group)
			else:
				break

		return cards_to_keep

	return get_face_frequency_targets

def create_suit_frequency_target_finder(get_min_frequency: Frequency) -> CardKeeper:
	'''Factory function that returns a function that returns a list of the best cards to form suit-frequency-based rank according to the specifications provided'''
	if not hasattr(get_min_frequency, '__call__'):
		get_min_frequency_func = lambda cards: get_min_frequency
	else:
		get_min_frequency_func = get_min_frequency

	def get_suit_frequency_targets(cards: Sequence[cds.Card]) -> List[cds.Card]:
		'''Returns a list of the best cards to form suit-frequency-based rank'''
		cards_to_keep = []
		hand = cardUtils.Hand(cards)

		for _, group in cardUtils.get_group_items_by_size_and_value(hand.get_groups_by_suit(), reverse=True):
			if len(group) >= get_min_frequency_func(cards):
				cards_to_keep.extend(group)
			else:
				break

		return cards_to_keep

	return get_suit_frequency_targets

def get_targets_from_user(cards: Sequence[cds.Card], *, max_discards: int = float('inf')) -> List[cds.Card]:
	'''Allows the user to choose cards to keep and returns those cards in a list'''
	prompt = 'Press ENTER to stop selecting cards; press a key then ENTER to continue selecting: '
	chosen = {card: False for card in cards}

	get_num_chosen = lambda: sum(chosen.values())
	display_cards(cards)

	while True:
		print('Chosen cards: ', end='')
		print(*(card for card in chosen if chosen[card]), sep=', ', end='\n\n')

		card = select_card(cards)

		if card:
			chosen[card] = not chosen[card] and get_num_chosen() < max_discards
			
		elif confirm_selection(prompt):
			break

	return [card for card in chosen if not chosen[card]]

def select_card(cards: Sequence[cds.Card]) -> cds.Card:
	'''Allows user to select a card from a list of cards'''
	try:
		index = int(input('Select a card by index: '))

		if index < 1 or index > len(cards):
			return None

	except ValueError:
		return None

	return cards[index - 1]

def get_most_frequent_face_targets(cards: Sequence[cds.Card]) -> List[cds.Card]:
	'''Returns the list of cards with the most frequent face'''
	hand = cardUtils.Hand(cards)
	sorted_group_items = cardUtils.get_group_items_by_size_and_value(hand.get_groups_by_face(), reverse=True)
	cards_to_keep = sorted_group_items[0][1] #Gets the cards that are part of the greatest face group item

	return cards_to_keep

def get_most_frequent_suit_targets(cards: Sequence[cds.Card]) -> List[cds.Card]:
	'''Returns the list of cards with the most frequent suit'''
	hand = cardUtils.Hand(cards)
	sorted_group_items = cardUtils.get_group_items_by_size_and_value(hand.get_groups_by_suit(), reverse=True)

	cards_to_keep = sorted_group_items[0][1] #Gets the cards that are part of the greatest suit group item

	return cards_to_keep

def confirm_selection(prompt: Optional[str]=None) -> bool:
	'''Returns True if user confirms their selection
Returns False if otherwise'''
	if prompt is None:
		prompt = 'Press ENTER to confirm; A key then ENTER to decline: '

	selection = not bool(input(prompt))
	print()

	return selection

def enter_name() -> str:
	'''Allows user to enter their name'''
	while True:
		name = input('Enter your name: ')
		if confirm_selection():
			return name

def display_cards(cards: Sequence[cds.Card]) -> None:
	'''Displays a formatted list of cards indexed from top-to-bottom'''
	for idx, card in enumerate(cards, start=1):
		print(f'{idx}) {card}')
	print()


class Discarder:
	def __init__(self, *, max_discards: int, get_keeper_func: CardKeeper, sorter: Callable[[Sequence[cds.Card]], List[cds.Card]] = sorted):
		self.max_discards = max_discards
		self.get_keeper_func = get_keeper_func
		self.sorter = sorter

	def get_target_cards(self, cards: Sequence[cds.Card]) -> List[cds.Card]:
		'''Returns a list of target cards depending on keeper function'''
		sorted_cards = self.sorted_by_precedence(cards)
		return self.get_keeper_func(sorted_cards)

	def get_irrelevant_cards(self, cards: Sequence[cds.Card]) -> List[cds.Card]:
		'''Returns a list of cards that are not targets depending on keeper function'''
		keeper_cards = self.get_keeper_func(cards)
		return [card for card in cards if card not in keeper_cards]

	def sorted_by_precedence(self, cards: Sequence[cds.Card], *, reverse: bool = True) -> Sequence[cds.Card]:
		'''Sorts from greatest to least by default'''

		return self.sorter(cards, reverse=reverse)

	def get_discards(self, cards: Sequence[cds.Card]) -> List[cds.Card]:
		'''Returns a list of the best discards depending on the keeper function and max number of allowed discards'''
		irrelevant_cards = self.get_irrelevant_cards(cards)
		return irrelevant_cards[:self.max_discards]

MAX_NUM_OF_DISCARDS = 3
MIN_FREQUENCY_TO_KEEP = 2

FREQUENCY_DISCARDER = Discarder(
	max_discards=MAX_NUM_OF_DISCARDS,
	get_keeper_func=create_face_frequency_target_finder(MIN_FREQUENCY_TO_KEEP)
)

FLUSH_DISCARDER = Discarder(
	max_discards=MAX_NUM_OF_DISCARDS,
	get_keeper_func=get_most_frequent_suit_targets
)

STRAIGHT_DISCARDER = Discarder(
	max_discards=MAX_NUM_OF_DISCARDS,
	get_keeper_func=create_sequence_target_finder(
		sequence_length=ranks.REQUIRED_LENGTH,
		invalid_starters=ranks.INVALID_STRAIGHT_STARTERS
	)
)

user_keeper_func: CardKeeper = lambda cards: get_targets_from_user(cards, max_discards=MAX_NUM_OF_DISCARDS)

USER_DISCARDER = Discarder(
	max_discards=MAX_NUM_OF_DISCARDS,
	get_keeper_func=user_keeper_func
)

class Player:
	DEFAULT_NAME = 'Player'

	def __init__(self, name: str = DEFAULT_NAME, *, discarder: Discarder, cards: Sequence[cds.Card] = None):
		self.name = name
		self.discarder = discarder

		self.hand = cardUtils.Hand(cards)

	def add_card(self, card: cds.Card) -> None:
		self.hand.append(card)

	def add_cards(self, cards: Sequence[cds.Card]) -> None:
		self.hand.extend(cards)

	def remove_card(self, card: cds.Card):
		self.hand.remove(card)

	def discard(self) -> None:
		'''Removes the player's targetted discards depending on their discarder'''
		cards_to_be_discarded = self.discarder.get_discards(self.hand)

		for card in cards_to_be_discarded:
			self.remove_card(card)

	def display(self) -> None:
		'''Displays the player's name and cards'''
		print(self.name)
		display_cards(self.hand)

class Game:
	NUM_OF_PLAYERS = 4
	NUM_OF_ROUNDS = 2

	MAX_HAND_LENGTH = 5

	DISCARDERS = [FLUSH_DISCARDER, STRAIGHT_DISCARDER, FREQUENCY_DISCARDER]

	def __init__(self):
		self.initialize_players()
		self.initialize_deck()

		self.rounds = self.NUM_OF_ROUNDS

	def initialize_players(self) -> None:
		'''Initializers the computer players and the human player'''
		self.players = []

		#Initializes computer players
		for _ in range(self.NUM_OF_PLAYERS - 1):
			name = f'Player {len(self.players) + 1}'
			discarder = random.choice(self.DISCARDERS)

			player = Player(name=name, discarder=discarder)
			self.players.append(player)

		#Initializes the human player
		user = Player(name=enter_name(), discarder=USER_DISCARDER)
		self.players.append(user)

	def initialize_deck(self) -> None:
		'''Initializes and shuffles the deck'''
		self.deck = []

		for face in cds.Face:
			for suit in cds.Suit:
				card = cds.Card(face=face, suit=suit)
				self.deck.append(card)

		random.shuffle(self.deck)

	def clear_player_hand(self, player: Player) -> None:
		player.hand.clear()

	def clear_all_player_hands(self) -> None:
		for player in self.players:
			self.clear_player_hand(player)

	def fill_player_hand(self, player: Player) -> None:
		while len(player.hand) < self.MAX_HAND_LENGTH:
			card = self.deck.pop()
			player.hand.append(card)

	def fill_all_player_hands(self) -> None:
		for player in self.players:
			self.fill_player_hand(player)

	def execute_player_discard(self, player: Player) -> None:
		player.discard()

	def find_winners(self) -> List[Player]:
		key_incumbent = self.players[0]
		incumbents = [key_incumbent]

		for challenger in self.players[1:]:
			result = pokerLogic.compare_hands(key_incumbent.hand, challenger.hand)

			if result == pokerLogic.Comparison.EQUAL:
				incumbents.append(challenger)
			elif result == pokerLogic.Comparison.LESSER:
				key_incumbent = challenger
				incumbents = [key_incumbent]

		return incumbents

	def display_player(self, player: Player) -> None:
		rank = ranks.get_rank(player.hand).name.title()
		player.display()
		print(f'They have a {rank}', end='\n\n')

	def display_all_players(self) -> None:
		for player in self.players:
			self.display_player(player)

	def display_all_winners(self) -> None:
		winners = self.find_winners()
		winning_rank = ranks.get_rank(winners[0].hand).name.title()
		print(f'Here are the winner(s) with a {winning_rank}: ', end='\n\n')
		for player in winners:
			self.display_player(player)

	def execute_rounds(self) -> None:
		'''Executes all the rounds of poker
		
Each round consists of all the players discarding their cards then drawing new cards from the deck'''
		for _ in range(self.NUM_OF_ROUNDS):
			for player in self.players:
				self.execute_player_discard(player)
				self.fill_player_hand(player)

	def reset(self) -> None:
		self.clear_all_player_hands()
		self.initialize_deck()


	def main_loop(self) -> None:
		running = True

		while running:
			self.fill_all_player_hands()
			self.execute_rounds()
			self.display_all_players()
			self.display_all_winners()

			running = confirm_selection('Press ENTER to play again. Press a key then ENTER to quit: ')

			if running:
				self.reset()

		print('Thanks for playing!')

def main() -> None:
	game = Game()
	game.main_loop()

if __name__ == '__main__':
	main()