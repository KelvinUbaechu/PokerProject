import cards as cds
from collections import Counter, UserList
from typing import List, Sequence, Iterable, Dict, Set, Tuple, Optional, Any

class Hand(UserList):
	def __init__(self, cards: Optional[Iterable[cds.Card]] = None):
		super().__init__(cards)

	def update(cards: Iterable[cds.Card]):
		self.clear()
		self.extend(cards)

	def get_faces(self) -> List[cds.Face]:
		'''Returns the faces of the cards in a list'''
		return [card.face for card in self]

	def get_suits(self) -> List[cds.Suit]:
		'''Returns the suits of the cards in a list'''
		return [card.suit for card in self]

	def get_cards_with_face(self, face: cds.Face) -> List[cds.Card]:
		'''Returns a list of cards that have same face as the face provided'''
		return [card for card in self if card.face == face]

	def get_cards_with_suit(self, suit: cds.Suit) -> List[cds.Card]:
		'''Returns a list of cards that have same suit as the face provided'''
		return [card for card in self if card.suit == suit]

	def get_groups_by_face(self) -> Dict[cds.Face, List[cds.Card]]:
		'''Returns a dictionary where the keys are faces and their values are a list of cards that contain the corresponding face'''
		groups = {face: [] for face in self.get_faces()}

		for card in self:
			groups[card.face].append(card)

		return groups

	def get_groups_by_suit(self) -> Dict[cds.Suit, List[cds.Card]]:
		'''Returns a dictionary where the keys are suits and their values are a list of cards that contain the corresponding suit'''
		groups = {suit: [] for suit in self.get_suits()}

		for card in self:
			groups[card.suit].append(card)

		return groups

	def get_faces_with_frequency(self, frequency: int) -> List[cds.Face]:
		'''Returns a list of faces which appear in the same frequency within the cards as the frequency provided'''
		faces = []

		for face, group in self.get_groups_by_face().items():
			if len(group) == frequency:
				faces.append(face)
				
		return faces

	def get_suits_with_frequency(self, frequency: int) -> List[cds.Suit]:
		'''Returns a list of suits which appear in the same frequency within the cards as the frequency provided'''
		suits = []

		for suit, group in self.get_groups_by_suit().items():
			if len(group) == frequency:
				suits.append(suit)

		return suits

def sorted_faces(faces: Iterable[cds.Face], *, reverse: bool = False) -> List[cds.Face]:
	'''Returns a list of faces sorted by value'''
	key = lambda face: face.value
	return sorted(faces, key=key, reverse=reverse)

def get_max_face(faces: Iterable[cds.Face]) -> cds.Face:
	'''Returns the face with the greatest value within the provided list of faces'''
	return sorted_faces(faces)[-1]

def get_min_face(faces: Iterable[cds.Face]) -> cds.Face:
	'''Returns the face with the smallest value within the provided list of faces'''
	return sorted_faces(faces)[0]

def sorted_starters(starters: Iterable[cds.Face], *, reverse: bool = False) -> List[cds.Face]:
	'''Returns a list of sequence starters sorted by precedence

Precedence from least-to-greatest A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K'''

	key = lambda starter: starter.value if starter != cds.Face.ACE else cds.MIN_VALUE - 1
	return sorted(starters, key=key, reverse=reverse)

def get_max_straight_starter(starters: Iterable[cds.Face]) -> cds.Face:
	'''Returns the straight starter with greatest precedence

Precedence from least-to-greatest A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K'''

	return sorted_starters(starters)[-1]

def get_min_straight_starter(starters: Iterable[cds.Face]) -> cds.Face:
	'''Returns the straight starter with least precedence

Precedence from least-to-greatest A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K'''

	return sorted_starters(starters)[0]

def is_straight_starter_greater(starter1: cds.Face, starter2: cds.Face) -> bool:
	'''Returns True if the first straight starter has greater precedence than the second straight starter

Precedence from least-to-greatest A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K'''
	if starter1 == starter2:
		return False

	if starter1 != cds.Face.ACE and starter2 != cds.Face.ACE:
		return starter1.value > starter2.value

	return starter1 != cds.Face.ACE

def is_straight_starter_lesser(starter1: cds.Face, starter2: cds.Face) -> bool:
	'''Returns True if the first straight starter has lesser precedence than the second straight starter

Precedence from least-to-greatest A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K'''
	if starter1 == starter2:
		return False

	if starter1 != cds.Face.ACE and starter2 != cds.Face.ACE:
		return starter1.value < starter2.value

	return starter1 == cds.Face.ACE

def get_sequence_of_starter(starter: cds.Face, *, sequence_length: int) -> List[cds.Face]:
	'''Returns the sequence of the provided length that the provided face starts'''
	sequence = []
	cur_face = starter

	for _ in range(sequence_length):
		sequence.append(cur_face)
		cur_face = cds.get_next_face(cur_face)

	return sequence

def get_starters_of_sequences_including_face(face: cds.Face, *, sequence_length: int, invalid: Optional[Iterable[cds.Face]]=None) -> Set[cds.Face]:
	'''Returns a set of sequence starters whose sequences of the given length contains the provided face
	
Can also provide an iterable of faces that are to be excluded from the returned set'''
	starters = set()
	starter = face
	invalid = invalid or set()

	for _ in range(sequence_length):

		if starter in starters:
			break
		elif starter not in invalid:
			starters.add(starter)

		starter = cds.get_previous_face(starter)

	return starters

def get_starters_of_sequences_including_faces(faces: Iterable[cds.Face], *, sequence_length: int, invalid: Optional[Iterable[cds.Face]]=None) -> Counter:
	'''Returns a Counter of sequence starters whose sequences of the given length contains the provided face
	
The value of the Counter represents the number of faces within the provided iterable of faces that are contained with the sequence of the key starter
Can also provide an iterable of faces that are to be excluded from the returned Counter'''
	starters = Counter()

	for face in set(faces):
		starters.update(get_starters_of_sequences_including_face(face, sequence_length=sequence_length, invalid=invalid))

	return starters

def get_most_frequent_starter_of_sequences_including_faces(faces: Iterable[cds.Face], *, sequence_length: int, invalid: Optional[Iterable[cds.Face]]=None) -> cds.Face:
	'''Returns the sequence starter whose sequence of the provided length contains the greatest number of the provided faces
	
If there are two or more sequence starters that contain the same number of faces, then the one with the greatest precedence is returned'''
	starters = get_starters_of_sequences_including_faces(faces, sequence_length=sequence_length, invalid=invalid)
	max_frequency = max(starters.values())

	return get_max_straight_starter([face for face in starters if starters[face] == max_frequency])

def get_sequence_including_most_faces(faces: Iterable[cds.Face], *, sequence_length: int, invalid: Optional[Iterable[cds.Face]]=None) -> List[cds.Face]:
	'''Returns the sequence of the provided length of the starter that contains the most of the provided faces'''
	starter = get_most_frequent_starter_of_sequences_including_faces(
		faces=faces,
		sequence_length=sequence_length,
		invalid=invalid
	)
	return get_sequence_of_starter(starter, sequence_length=sequence_length)

def sorted_by_frequency(iterable: Iterable[Any], *, reverse: bool = False) -> List[Any]:
	'''Returns a list sorted by the frequency of the items provided'''
	key = lambda item: iterable.count(item)
	return sorted(iterable, key=key, reverse=reverse)

def get_first_cards_with_faces(cards: Iterable[cds.Card], *, faces: Iterable[cds.Card]) -> List[cds.Card]:
	'''Returns a list of the first cards that contain the face in the provided iterable of faces'''
	first_cards_with_faces = []
	used_faces = set()

	for card in cards:
		if card.face in faces and card.face not in used_faces:
			first_cards_with_faces.append(card)
			used_faces.add(card.face)

	return first_cards_with_faces

def get_first_cards_with_suits(cards: Iterable[cds.Card], *, suits: Iterable[cds.Suit]) -> List[cds.Card]:
	'''Returns a list of the first cards that contain the suits in the provided iterable of suits'''
	first_cards_with_suits = []
	used_suits = set()

	for card in cards:
		if card.suit in suits and card.suit not in used_suits:
			first_cards_with_suits.append(card)
			used_suits.add(card.suit)

	return first_cards_with_suits

def get_group_items_by_size_and_value(face_group: Dict[cds.Face, List[cds.Card]], *, reverse: bool = False) -> List[Tuple[cds.Face, List[cds.Card]]]:
	'''Returns a list of key, value tuples of face group dict
	
Sorts the pair primarily by the length of the value list
Sorts the pair secondarily by the value of the key
	- This is done by getting the value of the first card in the value list, then getting its value'''

	groups = []
	key = lambda tup: (len(tup[1]), sorted(tup[1], reverse=True)[0].value)

	for face, group in sorted(face_group.items(), key=key, reverse=reverse):
		groups.append((face, group))

	return groups

def get_max_face_frequency(cards: Iterable[cds.Card]) -> int:
	'''Returns the highest frequency of any face in the provided iterable of cards'''
	hand = Hand(cards)
	return max(len(group) for group in hand.get_groups_by_face().values())

def get_min_face_frequency(cards: Iterable[cds.Card]) -> int:
	'''Returns the lowest frequency of any face in the provided iterable of cards'''
	hand = Hand(cards)
	return min(len(group) for group in hand.get_groups_by_face().values())

def get_max_suit_frequency(cards: Iterable[cds.Card]) -> int:
	'''Returns the highest frequency of any suit in the provided iterable of cards'''
	hand = Hand(cards)
	return max(len(group) for group in hand.get_groups_by_suit().values())

def get_min_suit_frequency(cards: Iterable[cds.Card]) -> int:
	'''Returns the lowest frequency of any suit in the provided iterable of cards'''
	hand = Hand(cards)
	return min(len(group) for group in hand.get_groups_by_suit().values())