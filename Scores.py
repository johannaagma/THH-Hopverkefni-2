import os, time
bonusTime = ''
	
#ekki ok
def getScore(time, deckLength, pyramidLength, height, sortsOn, win):
	timePoints = getTimePoints(time)
	deckPoints = getDeckPoints(deckLength)
	pyramidPoints = getPyrPoints(pyramidLength, height, sortsOn)
	sortsOnMuliply = 2
	winPoints = 1000
	if(sortsOn):
		if(win):
			return int(sortsOnMuliply*(pyramidPoints + winPoints) + deckPoints + timePoints)
		else:
			return int(sortsOnMuliply*pyramidPoints + deckPoints + timePoints)
	else:
		if(win):
			return int(pyramidPoints + winPoints + deckPoints + timePoints)
		else:
			return int(pyramidPoints + deckPoints + timePoints)

def getCurrentPoints(aGame):
	pyramidLength = len(aGame.pyramid)
	height = aGame.height
	sortsOn = aGame.sortsOn
	return getPyrPoints(pyramidLength, height, sortsOn)
	
def startBonusTime():
	global bonusTime
	s=0
	m=3
	while m>=0:
		os.system('cls')
		if(s < 10):
			bonusTime =  'Timebonus: ' + '0' + str(m) + ':0' + str(s)
		else:
			bonusTime = 'Timebonus: ' + '0' + str(m) + ':' + str(s)
		time.sleep(1)
		if s==0:
			m-=1
			s=60
		s-=1

def getBonusTime():
	global bonusTime
	return bonusTime
	
#ok	
def getTimePoints(time):
	timeBonus = 180  #3 minutes
	if(time > timeBonus):
		return 0
	return (timeBonus-time)*10

#ok	
def getDeckPoints(deckLength):
	return deckLength*100

#ok
def getPyrPoints(pyramidLength, height, sortsOn):
	origPyrLength = getOrigPyramidLength(height)
	if(sortsOn):
		return (origPyrLength - pyramidLength)*1000*2
	return (origPyrLength - pyramidLength)*1000

#ok	
def getOrigPyramidLength(height, count=0):
	if(height == 0):
		return count
	return getOrigPyramidLength(height-1, count+height)

#ok	
def getHighScores():
	scores = getScores()
	highScores = []
	if(len(scores) < 5):
		length = len(scores)
	else:
		length = 5
	top = 0
	for i in range(0,length):
		top = max(scores)
		highScores.append(top)
		scores.remove(top)
	return highScores

#ok
def add(score):
	scores = open('allScores.txt', 'a')
	scores.write(score)	
	scores.close()

#ok	
def getScores():
	temp = open('allScores.txt', 'r+')
	str = temp.read()
	temp.close()
	
	listOfScores = str.splitlines()
	scores = []
	for i in range(0, len(listOfScores)):
		scores.append(int(listOfScores[i]))
	return scores

def getHelp():
	temp = open('help.txt', 'r')
	string = temp.read()
	temp.close()

	return string
	
def getHighScoreString():
	listT = getHighScores()
	one =  '            1. ' + str(listT[0]) + '\n'
	two =  '            2. ' + str(listT[1]) + '\n'
	three = '            3. ' + str(listT[2]) + '\n'
	four =  '            4. ' + str(listT[3]) + '\n'
	five =  '            5. ' + str(listT[4]) + '\n'
	return one + two + three + four + five
	

	
	