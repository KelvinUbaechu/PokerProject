from enum import Enum
import cardUtils, ranks
import cards as cds
from typing import Iterable, Sequence, Tuple, List, Any

class Comparison(Enum):
	GREATER = 1
	EQUAL = 0
	LESSER = -1

#Categories for each rank
FACE_FREQUENCY_RANKS = (ranks.HIGH, ranks.PAIR, ranks.TWO_PAIR, ranks.THREE_OF_A_KIND, ranks.FULL_HOUSE, ranks.FOUR_OF_A_KIND)
SEQUENTIAL_RANKS = (ranks.STRAIGHT, ranks.STRAIGHT_FLUSH, ranks.ROYAL_FLUSH)
SUIT_FREQUENCY_RANKS = (ranks.FLUSH,)

def compare_group_items(group_item1: Tuple[cds.Face, List[cds.Card]], group_item2: Tuple[cds.Face, List[cds.Card]]) -> Comparison:
	'''Compares the two different items of a face group dictionary
	
Returns Comparison.GREATER if the first group item is greater than the second item
Returns Comparison.LESSER if the first group item is lesser than the second item
Returns Comparison.EQUAL if the first group item is equal to the second item

Group items are compared primarily by the length of their card group (the value of the key, value pair)
Their compared secondarily by the value of the face (the key of the key, value pair)'''
	face1, group1 = group_item1
	face2, group2 = group_item2

	if len(group1) > len(group2) or \
		(len(group1) == len(group2) and face1.value > face2.value):
		return Comparison.GREATER
	elif len(group1) < len(group2) or \
		(len(group1) == len(group2) and face1.value < face2.value):
		return Comparison.LESSER

	return Comparison.EQUAL

def compare_length(iterable1: Iterable[Any], iterable2: Iterable[Any]) -> Comparison:
	'''Compares iterables by their length
	
Returns Comparison.GREATER if the length of the first iterable is greater than the length of the second
Returns Comparison.LESSER if the length of the first iterable is lesser than the length of the second
Returns Comparison.EQUAL if the length of the first iterable is equal to the length of the second'''
	if len(iterable1) > len(iterable2):
		return Comparison.GREATER
	elif len(iterable1) < len(iterable2):
		return Comparison.LESSER
	else:
		return Comparison.EQUAL

def compare_hands(incumbent_hand: Sequence[cds.Card], challenger_hand: Sequence[cds.Card]) -> Comparison:
	'''Compares hands by the value of their rank
	
If ranks of both hands are the same, then the contents of their hands are compared depending on the category of their ranks'''
	incumbent_rank, challenger_rank = ranks.get_rank(incumbent_hand), ranks.get_rank(challenger_hand)

	if incumbent_rank > challenger_rank:
		return Comparison.GREATER
	elif incumbent_rank < challenger_rank:
		return Comparison.LESSER

	if incumbent_rank in FACE_FREQUENCY_RANKS:
		return compare_by_face_frequency(incumbent_hand, challenger_hand)
	elif incumbent_rank in SEQUENTIAL_RANKS:
		return compare_by_straight_starter(incumbent_hand, challenger_hand)
	else:
		return compare_by_value(incumbent_hand, challenger_hand)

def compare_by_face_frequency(incumbent_hand: Sequence[cds.Card], challenger_hand: Sequence[cds.Card]) -> Comparison:
	'''Compares both hands by face frequency
	
If one hand has more cards with the same face than the other hand, then that hand is considered to be greater
If both hand have cards whose faces appear at the same frequency, then the hand whose cards have greater value is considered greater'''
	incumbent_groups = cardUtils.Hand(incumbent_hand).get_groups_by_face()
	challenger_groups = cardUtils.Hand(challenger_hand).get_groups_by_face()

	group_match_up_generator = zip(
									cardUtils.get_group_items_by_size_and_value(incumbent_groups, reverse=True),
									cardUtils.get_group_items_by_size_and_value(challenger_groups, reverse=True)
								)

	for inc_group_item, cha_group_item in group_match_up_generator:
		result = compare_group_items(inc_group_item, cha_group_item)

		if result != Comparison.EQUAL:
			return result

	return compare_length(incumbent_groups, challenger_groups)

def compare_by_straight_starter(incumbent_hand: Sequence[cds.Card], challenger_hand: Sequence[cds.Card]) -> Comparison:
	'''Compares the values of each card of both hands sorted from the most precedent straight starter to least precedent'''
	
	inc_starter = cardUtils.get_most_frequent_starter_of_sequences_including_faces(
		faces=cardUtils.Hand(incumbent_hand).get_faces(),
		sequence_length=ranks.REQUIRED_LENGTH,
		invalid=ranks.INVALID_STRAIGHT_STARTERS
	)
	cha_starter = cardUtils.get_most_frequent_starter_of_sequences_including_faces(
		faces=cardUtils.Hand(challenger_hand).get_faces(),
		sequence_length=ranks.REQUIRED_LENGTH,
		invalid=ranks.INVALID_STRAIGHT_STARTERS
	)

	if inc_starter == cha_starter:
		return Comparison.EQUAL
	elif cardUtils.is_straight_starter_greater(inc_starter, cha_starter):
		return Comparison.GREATER
	else:
		return Comparison.LESSER

def compare_by_value(incumbent_hand: Sequence[cds.Card], challenger_hand: Sequence[cds.Card]) -> Comparison:
	'''Compares the values of each card of both hands sorted from greatest to least'''
	sorted_incumbent = sorted(incumbent_hand, reverse=True)
	sorted_challenger = sorted(challenger_hand, reverse=True)

	for inc_item, cha_item in zip(sorted_incumbent, sorted_challenger):
		if inc_item.value > cha_item.value:
			return Comparison.GREATER
		elif inc_item.value < cha_item.value:
			return Comparison.LESSER

	return compare_length(incumbent_hand, challenger_hand)