from enum import Enum
from collections import Counter
from typing import Iterable, Sequence, List, Dict, Optional, Callable, Any
import cards as cds
import cardUtils

RankValidator = Callable[[cds.Card], bool]

class Rank:

	def __init__(self, name: str, value: int, *, validators: Optional[Iterable[RankValidator]]=None):
		self.name = name
		self.value = value

		self.validators = validators or []

	def __eq__(self, other: 'Rank') -> bool:
		return isinstance(other, Rank) and self.value == other.value

	def __ne__(self, other: 'Rank') -> bool:
		return not isinstance(other, Rank) or self.value != other.value

	def __gt__(self, other: 'Rank') -> bool:
		if isinstance(other, Rank):
			return self.value > other.value

		return NotImplemented

	def __ge__(self, other: 'Rank') -> bool:
		if isinstance(other, Rank):
			return self.value >= other.value

		return NotImplemented

	def __lt__(self, other: 'Rank') -> bool:
		if isinstance(other, Rank):
			return self.value < other.value

		return NotImplemented

	def __le__(self, other: 'Rank') -> bool:
		if isinstance(other, Rank):
			return self.value <= other.value

		return NotImplemented

	def __repr__(self) -> str:
		return f'Rank({self.name}, {self.value})'

	def is_rank(self, cards: Iterable[cds.Card]) -> bool:
		'''Returns True if the cards meet the criteria of the validators for the rank
	Returns False if otherwise'''
		for validator in self.validators:
			if not validator(cards):
				return False

		return True

	@classmethod
	def none(cls) -> 'Rank':
		'''Returns a null rank'''
		return cls(name='None', value=0)

def has_required_group(attributes: Sequence[Any], group_size: int, num_of_groups: int) -> bool:
	'''Returns True if their are enough items (num_of_groups) who appear at the given frequency (group size) in the sequence
Returns False if otherwise'''
	attribute_frequencies = Counter(attributes)
	num_of_valid_groups = 0

	for frequency in attribute_frequencies.values():
		if frequency == group_size:
			num_of_valid_groups += 1

	return num_of_valid_groups == num_of_groups

#Factory functions to create a validators for the default ranks
def create_length_validator(required_length: int) -> RankValidator:
	
	def validate_length(cards):
		return len(cards) == required_length

	return validate_length

def create_sequence_validator(invalid_starters: Optional[Iterable[cds.Face]]=None) -> RankValidator:

	invalid_starters = invalid_starters or set()

	def validate_sequence(cards):

		card_group = cardUtils.Hand(cards)
		sequence_length = len(card_group)
		faces = card_group.get_faces()

		starter = cardUtils.get_most_frequent_starter_of_sequences_including_faces(
			faces=faces,
			sequence_length=sequence_length,
			invalid=invalid_starters
		)

		for _ in range(sequence_length):
			if starter not in faces:
				return False

			starter = cds.get_next_face(starter)

		return True

	return validate_sequence

def create_face_validator(required_faces: Iterable[cds.Face]) -> RankValidator:

	def validate_faces(cards):
		card_group = cardUtils.Hand(cards)
		faces = card_group.get_faces()

		for face in required_faces:
			if face not in faces:
				return False
			
		return True

	return validate_faces

def create_suit_validator(required_suits: Iterable[cds.Suit]) -> RankValidator:

	def validate_suits(cards):
		card_group = cardUtils.Hand(cards)
		suits = card_group.get_suits()

		for suit in required_suits:
			if suit not in suits:
				return False
			
		return True

	return validate_suits

def create_face_frequency_validator(required_frequencies: Dict[int, int]) -> RankValidator:

	def validate_face_frequencies(cards):
		card_group = cardUtils.Hand(cards)

		for group_size, required_num_of_group in required_frequencies.items():
			if not has_required_group(card_group.get_faces(), group_size, required_num_of_group):
				return False

		return True

	return validate_face_frequencies

def create_suit_frequency_validator(required_frequencies: Dict[int, int]) -> RankValidator:

	def validate_suit_frequencies(cards):
		card_group = cardUtils.Hand(cards)

		for group_size, required_num_of_group in required_frequencies.items():
			if not has_required_group(card_group.get_suits(), group_size, required_num_of_group):
				return False

		return True

	return validate_suit_frequencies

REQUIRED_LENGTH = 5 #Required length of sequence of cards to be in ordered to be considered
INVALID_STRAIGHT_STARTERS = {cds.Face.JACK, cds.Face.QUEEN, cds.Face.KING}
ROYAL_FACES = {cds.Face.TEN, cds.Face.JACK, cds.Face.QUEEN, cds.Face.KING, cds.Face.ACE}

NULL_RANK = Rank(
	name='None',
	value=0,
)

#All ranks for poker
HIGH = Rank(
	name='High Card',
	value=1,
	validators=[
		create_length_validator(REQUIRED_LENGTH)
	]
)

PAIR = Rank(
	name='Pair',
	value=2,
	validators=[
		create_length_validator(REQUIRED_LENGTH),
		create_face_frequency_validator({2:1})
	]
)

TWO_PAIR = Rank(
	name='Two Pair',
	value=3,
	validators=[
		create_length_validator(REQUIRED_LENGTH),
		create_face_frequency_validator({2:2})
	]
)

THREE_OF_A_KIND = Rank(
	name='Three of a Kind',
	value=4,
	validators=[
		create_length_validator(REQUIRED_LENGTH),
		create_face_frequency_validator({3:1})
	]
)

STRAIGHT = Rank(
	name='Straight',
	value=5,
	validators=[
		create_length_validator(REQUIRED_LENGTH),
		create_sequence_validator(INVALID_STRAIGHT_STARTERS)
	]
)

FLUSH = Rank(
	name='Flush',
	value=6,
	validators=[
		create_length_validator(REQUIRED_LENGTH),
		create_suit_frequency_validator({REQUIRED_LENGTH:1})
	]
)

FULL_HOUSE = Rank(
	name='Full House',
	value=7,
	validators=[
		create_length_validator(REQUIRED_LENGTH),
		create_face_frequency_validator({3:1, 2:1})
	]
)

FOUR_OF_A_KIND = Rank(
	name='Four of a Kind',
	value=8,
	validators=[
		create_length_validator(REQUIRED_LENGTH),
		create_face_frequency_validator({4:1})
	]
)

STRAIGHT_FLUSH = Rank(
	name='Straight Flush',
	value=9,
	validators=[
		create_length_validator(REQUIRED_LENGTH),
		create_sequence_validator(INVALID_STRAIGHT_STARTERS),
		create_suit_frequency_validator({REQUIRED_LENGTH:1})
	]
)

ROYAL_FLUSH = Rank(
	name='Royal Flush',
	value=10,
	validators=[
		create_length_validator(REQUIRED_LENGTH),
		create_sequence_validator(INVALID_STRAIGHT_STARTERS),
		create_suit_frequency_validator({REQUIRED_LENGTH:1}),
		create_face_validator(ROYAL_FACES)
	]
)

DEFAULT_RANKS = (
	ROYAL_FLUSH,
	STRAIGHT_FLUSH,
	FOUR_OF_A_KIND,
	FULL_HOUSE,
	FLUSH,
	STRAIGHT,
	THREE_OF_A_KIND,
	TWO_PAIR,
	PAIR,
	HIGH
)

def get_rank(cards: Sequence[cds.Card], *, ranks: Optional[Sequence[Rank]]=None) -> Rank:
	'''Returns the highest rank of the given ranks that the hand fulfills
	
If no ranks are given, then default ranks are used instead
Returns a null rank if the cards do not fulfill any of the ranks'''
	ranks = ranks or DEFAULT_RANKS

	for rank in ranks:
		if rank.is_rank(cards):
			return rank

	return NULL_RANK