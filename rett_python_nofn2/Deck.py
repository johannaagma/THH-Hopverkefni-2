#Hopverkefni 2
import random

class Deck:
	def __init__(self):
		self.deck = []

	def full_deck(self):
		suit = ["H", "S", "D", "C"]
		rank = range(1, 14)
		for i in range(0, len(suit)):
			for j in range(0, len(rank)):
				if(i == 0 or i == 2):
					card = Card(suit[i], rank[j], True)
					self.deck.append(card)
				else:
					card = Card(suit[i], rank[j], False)
					self.deck.append(card)					

	def shuffle(self):
		random.shuffle(self.deck)
	
	#Shows first card and then removes it from the deck	
	def draw(self):
		if(not self.is_empty()):
			return self.deck.pop(0)
		else:
			return

	#Shows first card in deck but does not remove it
	def show(self, key=0):
		if(not self.is_empty()):
			return self.deck[key]
		else:
			return

	def add_first(self,card):
		self.deck.insert(0,card)

	def add_last(self,card):
		self.deck.append(card)

	def empty_deck(self):
		self.deck = []

	def is_empty(self):
		return self.deck == []
	
	def show_all(self):
		for i in range(0, len(self.deck)):
			print self.deck[i],
	
	def get(self, number=0):
		return self.deck[number].get()

class Card(object):
	def __init__(self, Suit, Rank, Red):
		self.suit = Suit
		self.rank = Rank
		self.red = Red
		self.up = False
		self.left = None
		self.right = None
		self.rightParent = None
		self.leftParent = None
		#center of card
		self.x = 450
		self.y = 500

	#When str() is used on Card, [X Y] will be the output 
	#where X is the suit of the card and Y is the rank
	def __str__(self):
		return "["+self.suit+" "+str(self.rank)+"]"
		
	def insert_left(self, data, list):
		if self.left is None:
			self.left = data
			self.left.rightParent = self
			self.left.x = self.x-80
			self.left.y = self.y+100
			list.append(self.left)
		else:
			self.left.insert_left(data,list)
	
	def insert_right(self, data, list, special=False):
		#special is True if card has 2 parents, and those parents then need update
		if self.right is None:
			self.right = data
			self.right.leftParent = self
			self.right.x = self.x+80
			self.right.y = self.y+100
			list.append(self.right)
			if(special):
				parent = self #the data's left parent
				master = parent.rightParent #the right parent of parent
				magic = master.right #this card will be data's right parent
				magic.left = self.right #update the right parent of data
				self.right.rightParent = magic #now magic is the data's right parent
		else:
			if(special):
				self.right.insert_right(data,list,True)
			else:
				self.right.insert_right(data,list)
	
	def delete(self):
		if self.rightParent is not None:
			right_parent = self.rightParent
			right_parent.left = None
		if self.leftParent is not None:
			left_parent = self.leftParent
			left_parent.right = None
			
	def is_available(self):
		if(self.left is None and self.right is None):
			self.up = True
			return True
		else:
			return False
		
		
	#Shows the card (for example temp.show() shows what card temp is)
	def show(self):
		return self.data

