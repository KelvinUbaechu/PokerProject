from enum import Enum

class Face(Enum):
	TWO = 2
	THREE = 3
	FOUR = 4
	FIVE = 5
	SIX = 6
	SEVEN = 7
	EIGHT = 8
	NINE = 9
	TEN = 10
	JACK = 11
	QUEEN = 12
	KING = 13
	ACE = 14

class Suit(Enum):
	SPADES = 0
	HEARTS = 1
	CLOVERS = 2
	DIAMONDS = 3

MIN_VALUE = min(face.value for face in Face)
MAX_VALUE = max(face.value for face in Face)

class Card:
	def __init__(self, face: Face, suit: Suit):
		self.face = face
		self.suit = suit

	@property
	def value(self) -> int:
		return self.face.value

	def __eq__(self, other: 'Card') -> bool:
		return isinstance(other, Card) and \
			self.face == other.face and \
			self.suit == other.suit

	def __ne__(self, other: 'Card') -> bool:
		return not isinstance(other, Card) or \
			self.face != other.face or \
			self.suit != other.suit

	def __hash__(self) -> int:
		return hash((self.face, self.suit))

	def __gt__(self, other: 'Card') -> bool:
		if isinstance(other, Card):
			return self.value > other.value
		
		return NotImplemented

	def __ge__(self, other: 'Card') -> bool:
		if isinstance(other, Card):
			return self.value >= other.value
		
		return NotImplemented

	def __lt__(self, other: 'Card') -> bool:
		if isinstance(other, Card):
			return self.value < other.value
		
		return NotImplemented

	def __le__(self, other: 'Card') -> bool:
		if isinstance(other, Card):
			return self.value <= other.value
		
		return NotImplemented

	def __repr__(self) -> str:
		return f'Card{self.face, self.suit, self.value}'

	def __str__(self) -> str:
		return f'{self.face.name.title()} of {self.suit.name.title()}'

def get_next_face(face: Face) -> Face:
	try:
		return Face(face.value + 1)
	except ValueError:
		return Face(MIN_VALUE)

def get_previous_face(face: Face) -> Face:
	try:
		return Face(face.value - 1)
	except ValueError:
		return Face(MAX_VALUE)

def get_face_from_value(value: int) -> Face:
	'''Returns the Face enum with the same value as the integer provided'''
	try:
		return Face(value)
	except ValueError:
		return None