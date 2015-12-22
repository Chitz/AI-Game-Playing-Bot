__author__ = 'ctewani'
# Automatic Yahtzee game player
# B551 Fall 2015
# PUT YOUR NAME AND USER ID HERE!
# Name => Chitesh Tewani User ID => ctewani
# Based on skeleton code by D. Crandall
''''
Analysis of Program:
Best score so far: 208
Typical average score: 195 to 205
Time taken: ~ 1 min or less.

Algorithm -

For this problem, I have used expectimax and several rule-like condition to maximize the output.

Expecti-max
1. Implemented using a Priority Queue, where-in the nodes are the indices used to find the best re-roll for the next move
2. Based on the combinations [without symmetrical], I find the probabilistic average for each node and the node with the
best average is selected and given for re-rolls.
3. The average or sum for the combination score is using the current available score card, i.e. those categories which are
are already picked would not be included in the computing the average
4. The indices selected for expecti-max is selected by checking the available categories and finding indices from the given dice formations
which best suites the category or re-roll will achieve that category.

General rules and decisions implemented
1. Mixed categories - If the dice formation is very likely to fall in one of the two categories an intersection of their indices is taken
for re-roll
E.g. Suppose the formation is [1,2,1,4,4]. A reroll on the dice will very likely fetch Unos or Cuatro. Hence that's a mix category..
I pick the index 1, as re-rolling only one index has a higher probability of the falling in Unos or Cuatro, instead of picking three
indices for both the category and lesser probability of falling into any of them

2. To assign Bonus for Unos to Seiess. I have implemented a trick, where in only best possible numbers would fit in the category for Unos to S
Seiss for the bonus.

With the bestest score of the indices in first six categories, we can reach a count of 120. We calculate the individual effort put by each 1st six category

Unos - 6 (6/120) .. effort put by Unos. Multiplying by 63 as the total, we will get a value whcih we would need to make to the sum of 63.

So it is [3,6,9...] so on..

If one of the 1st six category has better result at some point, we understand teh effort taken by rest of the numbers would be lesser to make it to the bonus.

3. I pick the numbers repeated twice or more in the dice formattion and try to fill in the singles, so to get closer to the bonus.

4. Tamal is not assigned unless really really needed. We settle with a small value for singles category. 1 for Unos is better than 5 from Cucions.. As getting a mutiple
5 will boost the score, but lower numbers won't boost as much

5. The special categories are given preference, based the availability of the singles empty category, as if not many available we'll like
to fill singles category better for the bonus.

6. Each indices picked for teh individually optimized to give the best indices..

7. The threashold for singles category help to get the bonus on the score baord, as only right fitting values are put. This rule is
sometimes relaxed to fit in special categories for more point.

8. The category picked for first roll is carry forward for the next roll to get better results. They are mixed with other categories sometis
to get a randomized optimized results.


'''

from YahtzeeState import Dice
from YahtzeeState import Scorecard
import random
from collections import defaultdict
from itertools import combinations_with_replacement
from copy import deepcopy as copy
import Queue

diceSampleSpace = defaultdict(list)

class evaluate:
      def __init__(self, dice, scorecard):
            self.score = 0
            self.scorecard = scorecard
            self.dice = dice
            self.expectedSingleValue = self.getExpectedSinglesValueArray()

      def evaluateScore(self, dice, category):
            counts = [dice.dice.count(i) for i in range(1,7)]
            if category in Scorecard.Numbers:
                  self.score = counts[Scorecard.Numbers[category]-1] * Scorecard.Numbers[category]
            elif category == "pupusa de queso":
                  self.score = 40 if sorted(dice.dice) == [1,2,3,4,5] or sorted(dice.dice) == [2,3,4,5,6] else 0
            elif category == "pupusa de frijol":
                  self.score = 30 if (len(set([1,2,3,4]) - set(dice.dice)) == 0 or len(set([2,3,4,5]) - set(dice.dice)) == 0 or len(set([3,4,5,6]) - set(dice.dice)) == 0) else 0
            elif category == "elote":
                  self.score = 25 if (2 in counts) and (3 in counts) else 0
            elif category == "triple":
                  self.score = sum(dice.dice) if max(counts) >= 3 else 0
            elif category == "cuadruple":
                  self.score = sum(dice.dice) if max(counts) >= 4 else 0
            elif category == "quintupulo":
                  self.score = 50 if max(counts) == 5 else 0
            elif category == "tamal":
                  self.score = sum(dice.dice)

      def maxBet(self, count):
            return count * 5

      # make expected value array for 1 to 6, to compare
      def getExpectedSinglesValueArray(self):
            expectedSingleValue = copy(Scorecard.Numbers)
            missingSingle = []
            singleSum = 0
            emptySingleSum = 0
            for i in Scorecard.Numbers:
                  if i in self.scorecard.scorecard:
                        singleSum += self.scorecard.scorecard[i]
                  else:
                        maxBet = self.maxBet(self.scorecard.Numbers[i])
                        expectedSingleValue[i] = maxBet
                        missingSingle.append(i)
                        emptySingleSum += maxBet
            # Rule 1: Check the count for 1-6 category, if sum of scores is 63.
            if singleSum < 63:
                  singleSum = 63 - singleSum
                  for i in missingSingle:
                        expectedSingleValue[i] = expectedSingleValue[i]*singleSum*1.0/emptySingleSum
            return expectedSingleValue

      # evaluate the dice formation, HOW?
      def evaluate(self):
            categoryScore = []
            maxSinglesScore = 0
            emptyCategories = list(set(Scorecard.Categories) - set(self.scorecard.scorecard.keys()))
            for category in emptyCategories:
                  self.evaluateScore(self.dice, category)
                  categoryScore.append(self.score)
            sortedCategoryScoreList = sorted(range(len(categoryScore)), key=lambda k: categoryScore[k],reverse=True)
            sortedCategoryList = [emptyCategories[i] for i in sortedCategoryScoreList]
            for singlesCategory in [singleCategory for singleCategory in self.expectedSingleValue if singleCategory in emptyCategories]:
                  singlesCategoryScore = categoryScore[emptyCategories.index(singlesCategory)]
                  if self.expectedSingleValue[singlesCategory] <= singlesCategoryScore and \
                                  maxSinglesScore < singlesCategoryScore:
                        maxSinglesScore = singlesCategoryScore
                        category = singlesCategory
            if maxSinglesScore != 0:
                  maxCategoryScore = maxSinglesScore
                  # if many remaining tries left; say # of tries >= (# of 1st 6 blocks yet to fill) + 2; give other higher values a try
                  if len(emptyCategories) > len([singleCategory for singleCategory in self.expectedSingleValue if singleCategory in emptyCategories]):
                        for index in range(len(sortedCategoryScoreList)):
                              if sortedCategoryList[index] not in Scorecard.Numbers.keys() + ['tamal'] and categoryScore[sortedCategoryScoreList[index]] > maxSinglesScore:
                                    maxCategoryScore = categoryScore[sortedCategoryScoreList[index]]
                                    category = sortedCategoryList[index]
                                    break
            else:
                  maxCategoryScoreOG = maxCategoryScore = categoryScore[sortedCategoryScoreList[0]]
                  categoryOG = category = sortedCategoryList[0]

                  for index in range(len(sortedCategoryScoreList)):
                        maxCategoryScore = categoryScore[sortedCategoryScoreList[index]]
                        category = sortedCategoryList[index]
                        if category not in Scorecard.Numbers.keys() + ['tamal']:
                              break

                  if len(sortedCategoryList) > 1 and categoryScore[sortedCategoryScoreList[1]] == categoryScore[sortedCategoryScoreList[0]]:
                        if category != 'talam':
                              maxCategoryScore = categoryScore[sortedCategoryScoreList[1]]
                              category = sortedCategoryList[1]
                  elif maxCategoryScore == 0 and len(sortedCategoryList) > 1 and \
                              maxCategoryScore < 25:
                        #try next best and not tamal
                        if maxCategoryScore == 0:
                              #nothing works. so use tamal
                              if categoryOG in Scorecard.Numbers:
                                    # if picking 1 to 6 slots, pick the lowest value..
                                    for index in range(len(sortedCategoryList)-1,-1,-1):
                                          if sortedCategoryList[index] in Scorecard.Numbers and categoryScore[sortedCategoryScoreList[index]]/Scorecard.Numbers[sortedCategoryList[index]] > 1:
                                                category = sortedCategoryList[index]
                                                maxCategoryScore = categoryScore[sortedCategoryScoreList[index]]
                                                break
                              else:
                                    category = categoryOG
                                    maxCategoryScore = maxCategoryScoreOG

                  elif maxCategoryScoreOG >= 25:
                        category = categoryOG
                        maxCategoryScore = maxCategoryScoreOG
            if maxCategoryScore == 0:
                  max = 0
                  for index in sortedCategoryScoreList:
                        if categoryScore[sortedCategoryScoreList[index]] > max:
                              maxCategoryScore = categoryScore[sortedCategoryScoreList[index]]
                              category = sortedCategoryList[index]
            return category, maxCategoryScore

# put chanceNode in priority Queue and get best
class chanceNode:
      def __init__(self, indices, category, dice):
            self.indices = indices
            self.averageScore = 0
            self.score = []
            self.dice = dice
            self.category = category
            self.diceSampleSpace = self.getDiceSampleSpace(len(self.indices))

      def getDiceSampleSpace(self, diceCount):
            if not diceSampleSpace[diceCount]:
                  diceSampleSpace[diceCount] = list(combinations_with_replacement(range(1,7),r=diceCount))
            return diceSampleSpace[diceCount]

      def __lt__(self, other):
        return self.averageScore > other.averageScore

      def addChildren(self, scorecard):
            chanceDice  = copy(self.dice)
            self.dice = chanceDice
            ev = evaluate(self.dice, scorecard)
            for combination in self.diceSampleSpace:
                  ev.dice = copy(self.dice)
                  for index in range(0,len(self.indices)-1):
                        ev.dice.dice[self.indices[index]] = combination[index]
                  category, score = ev.evaluate()
                  self.score.append(score)

            self.averageScore = sum(self.score)*1.0/len(self.diceSampleSpace)
            #print "average",self.averageScore,"sum",sum(self.score),"indices",self.indices

class YahtzeeAutoPlayer:

      def __init__(self):
            self.pickedCategory = []
            pass

      def mixed(self, category):
            #print category,
            category = category.split('-')
            leftCategory = self.pickCategory(category[0])
            rightCategory = self.pickCategory(category[1])
            indices = list(set(leftCategory).intersection(rightCategory))
            #print "mixed", indices
            return indices

      def pickCategory(self, category):
            if '-' in category:
                  return self.mixed(category)
            switch = {
                  "unos": self.evaluateUnos,
                  "doses": self.evaluateDoses,
                  "treses": self.evalateTreses,
                  "cuatros": self.evaluateCuatros,
                  "cincos": self.evaluateCincos,
                  "seises": self.evaluateSeises,
                  "pupusa de queso": self.evaluatePupusaDeQueso,
                  "pupusa de frijol": self.evaluatePupusaDeFrijol,
                  "elote": self.evaluateElote,
                  "triple": self.evaluateTriple,
                  "cuadruple": self.evaluateCuadruple,
                  "quintupulo": self.evaluateQuintupulo,
                  "tamal": self.evaluateTamal,
            }
            return switch[category]()

      def evaluatePupusaDeQueso(self):
            # Pupusa de Queso [1,2,3,4,5] and [2,3,4,5,6]
            #print "evaluatePupusaDeQueso", self.dice,
            missingIndices = []
            numList = range(1,7)
            startIndex = 0
            endIndex = 5
            excludeIndex = -1
            runCount = 0
            emptyList = []
            while runCount < 2:
                  runCountIndices = copy(emptyList)
                  for number in numList[startIndex:endIndex]:
                        runCountIndices.extend(self.diceIndicesDict[number][1:])
                  if self.diceIndicesDict[numList[excludeIndex]]:
                        runCountIndices.extend(self.diceIndicesDict[numList[excludeIndex]][:])
                  missingIndices.append(runCountIndices)
                  startIndex += 1
                  endIndex += 1
                  excludeIndex += 1
                  runCount += 1
            xIndices = missingIndices[0] if len(missingIndices[0]) <= len(missingIndices[1]) else missingIndices[1]
            #print "rerollIndices", xIndices
            return xIndices

      def evaluatePupusaDeFrijol(self):
            #print "evaluatePupusaDeFrijol", self.dice,
            # Pupusa De Frijol [1,2,3,4] or [2,3,4,5] or [3,4,5,6]
            missingIndices = []
            numList = range(1, 7)
            startIndex = 0
            endIndex = 4
            excludeIndex = [-1, -2]
            runCount = 0
            emptyList = []
            while runCount < 3:
                  runCountIndices = copy(emptyList)
                  uniqueCount = 0
                  for number in numList[startIndex:endIndex]:
                        if self.diceIndicesDict[number]:
                              uniqueCount += 1
                              runCountIndices.extend(self.diceIndicesDict[number][1:])
                  for xIndex in excludeIndex:
                        if self.diceIndicesDict[numList[xIndex]]:
                              uniqueCount += 1
                              runCountIndices.extend(self.diceIndicesDict[xIndex][:])
                              if uniqueCount > 4:
                                    break
                  missingIndices.append(runCountIndices)
                  startIndex += 1
                  endIndex += 1
                  excludeIndex = [excludeIndex + 1 for excludeIndex in excludeIndex]
                  runCount += 1
            # implement in a new function!
            for missingSet in missingIndices:
                  if len(numList) > len(missingSet):
                        numList = missingSet
            #print "rerollIndices",numList
            return numList

      def evaluateElote(self):
            #print "evaluateElote", self.dice,
            rerollIndices = []
            rerollCount = 3
            diceFreqDictCopy = copy(self.diceFreqDict)
            #just check for diceFreq = 1
            diceFreq = 1
            diceFreqDictCopy[diceFreq].sort()
            for diceNum in diceFreqDictCopy[diceFreq]:
                  if rerollCount == 0:
                        break
                  rerollCount -= 1
                  rerollIndices.extend(self.diceIndicesDict[diceNum])
            #print "rerollIndices", rerollIndices
            return rerollIndices

      def evaluateTriple(self):
            #print "evaluateTriple", self.dice,
            rerollIndices = []
            excludeIndices = []
            diceFreqDictCopy = copy(self.diceFreqDict)
            if len(self.diceFreqDict[2]) == 1:
                  excludeIndices = self.diceIndicesDict[self.diceFreqDict[2][0]]
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            elif len(self.diceFreqDict[2]) > 1:
                  for x in self.diceFreqDict[2]:
                        excludeIndices.extend(self.diceIndicesDict[x])
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            else:
                  diceFreqDictCopy[1].sort()
                  for diceNum in diceFreqDictCopy[1][:3]:
                        rerollIndices.extend(self.diceIndicesDict[diceNum])
            #print "rerollIndices",rerollIndices
            return rerollIndices

      def evaluateCuadruple(self):
            #print "evaluateCuadruple", self.dice,
            diceFreqDictCopy = copy(self.diceFreqDict)
            rerollIndices = []
            if len(self.diceFreqDict[3]) == 1:
                  excludeIndices = self.diceIndicesDict[self.diceFreqDict[3][0]]
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            elif len(self.diceFreqDict[2]) > 1:
                  self.diceFreqDict[2].sort()
                  excludeIndices = self.diceIndicesDict[diceFreqDictCopy[2][-1]]
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            elif len(self.diceFreqDict[2]) == 1:
                  excludeIndices = self.diceIndicesDict[self.diceFreqDict[2][0]]
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            else:
                  diceFreqDictCopy[1].sort()
                  for diceNum in diceFreqDictCopy[1][:4]:
                        rerollIndices.extend(self.diceIndicesDict[diceNum])
            #print "rerollIndices", rerollIndices
            return rerollIndices

      def evaluateQuintupulo(self):
            #print "evaluateQuintupulo", self.dice,
            rerollIndices = []
            diceFreqDictCopy = copy(self.diceFreqDict)
            if len(self.diceFreqDict[4]) == 1:
                  excludeIndices = self.diceIndicesDict[self.diceFreqDict[4][0]]
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            elif len(self.diceFreqDict[3]) == 1:
                  excludeIndices = self.diceIndicesDict[self.diceFreqDict[3][0]]
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            elif len(self.diceFreqDict[2]) > 1:
                  diceFreqDictCopy[2].sort()
                  excludeIndices = self.diceIndicesDict[diceFreqDictCopy[2][-1]]
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            elif len(self.diceFreqDict[2]) == 1:
                  excludeIndices = self.diceIndicesDict[self.diceFreqDict[2][0]]
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            else:
                  diceFreqDictCopy[1].sort()
                  for diceNum in diceFreqDictCopy[1][:4]:
                        rerollIndices.extend(self.diceIndicesDict[diceNum])
            #print "rerollIndices", rerollIndices
            return rerollIndices

      def evaluateSeises(self):
            #print "evaluateSeises",self.dice
            if self.diceIndicesDict[6]:
                  excludeIndices = self.diceIndicesDict[6]
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            else:
                  rerollIndices = range(0,5)
            #print "rerollIndices", rerollIndices
            return rerollIndices

      def evaluateCincos(self):
            #print "evaluateCincos", self.dice,
            if self.diceIndicesDict[5]:
                  excludeIndices = self.diceIndicesDict[5]
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            else:
                  rerollIndices = range(0,5)
            #print "rerollIndices", rerollIndices
            return rerollIndices

      def evaluateUnos(self):
            #print "evaluateUnos", self.dice,
            if self.diceIndicesDict[1]:
                  excludeIndices = self.diceIndicesDict[1]
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            else:
                  rerollIndices = range(0,5)
            #print "rerollIndices", rerollIndices
            return rerollIndices

      def evaluateDoses(self):
            #print "evaluateDoses", self.dice,
            if self.diceIndicesDict[2]:
                  excludeIndices = self.diceIndicesDict[2]
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            else:
                  rerollIndices = range(0,5)
            #print "rerollIndices", rerollIndices
            return rerollIndices

      def evalateTreses(self):
            #print "evaluateTreses", self.dice,
            if self.diceIndicesDict[3]:
                  excludeIndices = self.diceIndicesDict[3]
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            else:
                  rerollIndices = range(0,5)
            #print "rerollIndices", rerollIndices
            return rerollIndices

      def evaluateCuatros(self):
            #print "evaluateCuatros", self.dice,
            if self.diceIndicesDict[4]:
                  excludeIndices = self.diceIndicesDict[4]
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            else:
                  rerollIndices = range(0,5)
            #print "rerollIndices", rerollIndices
            return rerollIndices

      def evaluateTamal(self):
            #print "evaluateTamal", self.dice
            excludeIndices = []
            if(sum(self.dice.dice)>20):
                  rerollIndices = self.dice.dice.index(max(self.dice.dice))
            else:
                  for i in range(6,-1,-1):
                        excludeIndices.extend(self.diceIndicesDict[i][:])
                        if len(excludeIndices)>2:
                              break
                  rerollIndices = [i for i in range(0,5) if i not in excludeIndices]
            #print "rerollIndices", rerollIndices
            return rerollIndices

      def updateDict(self):
            self.diceIndicesDict = defaultdict(list)
            self.diceFreqDict = defaultdict(list)
            for index in range(0,5):
                  self.diceIndicesDict[self.dice.dice[index]].append(index)
                  diceFreq = len(self.diceIndicesDict[self.dice.dice[index]])
                  if diceFreq > 1:
                        self.diceFreqDict[diceFreq - 1].remove(self.dice.dice[index])
                  self.diceFreqDict[diceFreq].append(self.dice.dice[index])

      # decide the indices to re-roll again
      def decideIndices(self, dice, scorecard, currCategory):
            emptyCategories = []
            chancePQ = Queue.PriorityQueue()
            emptyCategoriesOG = list(set(Scorecard.Categories) - set(scorecard.scorecard.keys()))
            emptyCategoriesInt = list(set(emptyCategoriesOG).intersection(scorecard.Numbers.keys()))
            if self.pickedCategory:
                  emptyCategories = self.pickedCategory
            if emptyCategoriesInt:
                  specialCategories = []
                  emptyCategories = []
                  diceIndicesDict = defaultdict(list)
                  diceFreqDict = defaultdict(list)
                  for index in range(0,5):
                        diceIndicesDict[dice.dice[index]].append(index)
                        diceFreq = len(diceIndicesDict[dice.dice[index]])
                        if diceFreq > 1:
                              diceFreqDict[diceFreq - 1].remove(dice.dice[index])
                        diceFreqDict[diceFreq].append(dice.dice[index])
                  # check for elote, triple and cuadraple
                  if len(diceFreqDict[3]) == 1 and 'triple' in emptyCategoriesOG:
                        specialCategories.append('triple')
                  elif len(diceFreqDict[3]) == 1 and diceFreqDict[2] == 1 and 'elote' in emptyCategoriesOG:
                        specialCategories.append('elote')
                  elif len(diceFreqDict[4]) == 1 and 'cuadruple' in emptyCategoriesOG:
                        specialCategories.append('cuadruple')
                  for cat in emptyCategoriesInt:
                        if len(diceIndicesDict[scorecard.Numbers[cat]]) >= 2:
                              emptyCategories.append(cat)

                  if not emptyCategories:
                        emptyCategories = emptyCategoriesOG
                  else:
                        emptyCategories = ['-'.join(list(set(emptyCategories)))]
                  if specialCategories:
                        emptyCategories.extend(specialCategories)
            count = 0
            if currCategory not in emptyCategories and currCategory != 'tamal':
                  emptyCategories.append(currCategory)
            self.pickedCategory = emptyCategories
            for category in emptyCategories:
                  indices = self.pickCategory(category)
                  if type(indices) is not list:
                        indices = [indices]
                  if len(indices) == 0:
                        continue
                  dice = copy(self.dice)
                  cNode = chanceNode(indices, category, dice)
                  cNode.addChildren(scorecard)
                  chancePQ.put(cNode)
                  count += 1
            if count != 0:
                  bestChanceNode = chancePQ.get()
                  #print "Category picked", bestChanceNode.category, "Average score", bestChanceNode.averageScore, "Indices", bestChanceNode.indices
                  return bestChanceNode.category, bestChanceNode.averageScore, bestChanceNode.indices
            else:
                  return "No category",999999,[]

      def first_roll(self, dice, scorecard):
            self.dice = dice
            self.updateDict()
            self.pickedCategory = []
            ev = evaluate(dice,scorecard)
            currentCategory, currentScore = ev.evaluate()
            dCategory, averageScore, indices = self.decideIndices(dice,scorecard, currentCategory)
            if currentCategory in self.pickedCategory:
                  indices = self.pickCategory(currentCategory)
                  if type(indices) is not list:
                        indices = [indices]
            elif (currentScore >= averageScore and dCategory not in self.pickedCategory) \
                    or currentCategory not in scorecard.Numbers.keys() + ['tamal']:
                  indices = []
            return indices

      def second_roll(self, dice, scorecard):
            self.dice = dice
            self.updateDict()
            ev = evaluate(dice,scorecard)
            currentCategory, currentScore = ev.evaluate()
            dCategory, averageScore, indices = self.decideIndices(dice,scorecard,currentCategory)

            if currentCategory in self.pickedCategory:
                  indices = self.pickCategory(currentCategory)
                  if type(indices) is not list:
                        indices = [indices]
            elif currentScore > averageScore and dCategory not in self.pickedCategory \
                     or currentCategory not in scorecard.Numbers.keys() + ['tamal']:
                  indices = []
            return indices
            #return [1, 2] # always re-roll second and third dice (blindly)

      def third_roll(self, dice, scorecard):
            self.dice = dice
            self.updateDict()
            ev = evaluate(dice, scorecard)
            category, score = ev.evaluate()
            print "################################"
            print "Final score", score, "Category", category
            print "################################"
            #return list(set(Scorecard.Categories)).index(category)
            return category
            #return random.choice( list(set(Scorecard.Categories) - set(scorecard.scorecard.keys())) )

