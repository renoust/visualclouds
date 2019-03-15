import sys
import os
import csv
import json

import sys
reload(sys) 
sys.setdefaultencoding('utf-8')

MAX_SEARCH_PERSON = 8
MAX_SEARCH_RESULT = 400


class myTopicServer():
  def __init__(self):
    print 'start loading the data ...'
    self.imdbDataLoad()

  def getFaceList(self):
    # castDict = self.getCast()
    return self.castDict

    faceList = os.listdir('server/data/sface')
    res = {}
    for oneFace in faceList:
      fl  = oneFace.split('.')
      if fl[1] == 'jpg':
        oneCast = fl[0]
        if oneCast not in res:
          res[oneCast] = 1
        else:
          res[oneCast] += 1
    return res

  def getCast(self):
    castDict = {}
    castFileList = os.listdir('server/data/cast')
    for oneFile in castFileList:
      if oneFile != '.DS_Store':
        fileIndex = int(oneFile.split('.')[0])
        with open('server/data/cast/'+oneFile, 'r') as csvfile:
          spamreader = csv.reader(csvfile, delimiter='|', quotechar='"')
          for oneCastLine in spamreader:
            oneCastList = oneCastLine[0].split(' | ')
            if oneCastList[-1] == '':
              oneCastList = oneCastList[:-1]
            castDict[fileIndex] = oneCastList
    return castDict

  def getKeywords(self):
    keywordsDict = {}
    keywordsFileList = os.listdir('server/data/keywords')
    for oneFile in keywordsFileList:
      if oneFile != '.DS_Store':
        fileIndex = int(oneFile.split('.')[0])
        with open('server/data/keywords/'+oneFile, 'r') as csvfile:
          spamreader = csv.reader(csvfile, delimiter='|', quotechar='"')
          for onekeywordsLine in spamreader:
            onekeywordsList = onekeywordsLine[0].split('|')
            if onekeywordsList[-1] ==  '':
              onekeywordsList = onekeywordsList[:-1]
            keywordsDict[fileIndex] = onekeywordsList
    return keywordsDict

  def getStoryLine(self):
    storyLineDict = {}
    storyLineFileList = os.listdir('server/data/storyline')
    for oneFile in storyLineFileList:
      if oneFile != '.DS_Store':
        fileIndex = int(oneFile.split('.')[0])
        with open('server/data/storyLine/'+oneFile, 'r') as csvfile:
          spamreader = csv.reader(csvfile, delimiter='|', quotechar='"')
          for onestoryLineLine in spamreader:
            storyLineDict[fileIndex] = onestoryLineLine[0]
    return storyLineDict

  def getPremierDict(self, dict, topVal):
    res = {}
    stdict = sorted(dict.items(), key=lambda d: d[1], reverse=True)
    i = 0
    for key, val in stdict:
      res[key] = val
      i += 1
      if i >= topVal:
        break
    return res

  def checkCondition(self, oneData, cnd):
    isOk = True
    isFirst = True

    for oneCnd in cnd:
      isOneOk = True
      if 'faceName' in oneCnd:
        if oneCnd['faceName'] not in oneData['person']:
          isOneOk = False
      if 'startDate' in oneCnd:
        if oneCnd['startDate'] > oneData['date']:
          isOneOk = False
      if 'endDate' in oneCnd:
        if oneCnd['endDate'] < oneData['date']:
          isOneOk = False
      if 'keyword' in oneCnd:
        if oneCnd['keyword'] not in oneData['text']:
          isOneOk = False
      
      if oneCnd['condition'] == 'and':
        if isOk and isOneOk:
          isOk = True
        else:
          isOk = False
      elif oneCnd['condition'] == 'or':
        if isOk or isOneOk:
          isOk = True
        else:
          isOk = False
      elif oneCnd['condition'] == 'not':
        if not isOneOk and isOk:
          isOk = True
        else:
          isOk = False

    return isOk


  def analyseRequest(self, para):
    numberChecker = 0
    res = []
    print para
    topCastNum = int(para['maxCastNum'])
    topKwdNum = int(para['maxKeywordNum'])

    for oneIndex in self.allData:
      if numberChecker >= para['maxSnpNum']:
        break
      if self.checkCondition(self.allData[oneIndex], para['data']):
        temp = {}
        for oneProp in self.allData[oneIndex]:
          temp[oneProp] = self.allData[oneIndex][oneProp]

        temp['keywords'] = ';'.join(temp['keywords'][0:topKwdNum])
        temp['cast'] = ';'.join(temp['cast'][0:topCastNum])
        res.append(temp)
        numberChecker += 1

    return res

  def addPerson(self, personName, fileIndex):
    if len(personName) > 0:
      # if personName in self.castDict:
        # self.personToTopic[personName][fileIndex] = True
      self.castDict[personName] = 0
      # else:
      #   self.personToTopic[personName] = {}
      #   self.personToTopic[personName][fileIndex] = True

  def imdbDataLoad(self):
    color = 0
    director_name = 1
    num_critic_for_reviews = 2
    duration = 3
    director_facebook_likes = 4
    actor_3_facebook_likes = 5
    actor_2_name = 6
    actor_1_facebook_likes = 7
    gross = 8
    genres = 9
    actor_1_name = 10
    movie_title = 11
    num_voted_users = 12
    cast_total_facebook_likes = 13
    actor_3_name = 14
    facenumber_in_poster = 15
    plot_keywords = 16
    movie_imdb_link = 17
    num_user_for_reviews = 18
    language = 19
    country = 20
    content_rating = 21
    budget = 22
    title_year = 23
    actor_2_facebook_likes = 24
    imdb_score = 25
    aspect_ratio = 26
    movie_facebook_likes = 27

    self.allData = {}
    # self.personToTopic = {}
    self.castDict = {}

    isTitle = True
    titleList = []
    rowSize = 0

    fileNameIndex = 1
    castDict = self.getCast()
    keywordsDict = self.getKeywords()
    storyLineDict = self.getStoryLine()

    with open('server/data/movie_metadata.csv', 'r') as csvfile:
      spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
      for row in spamreader:

        if isTitle:
          isTitle = False
          titleList = row
          rowSize = len(row)
          continue
      
        director = row[director_name]
        actor1 = row[actor_1_name]
        actor2 = row[actor_2_name]
        actor3 = row[actor_3_name]

        self.addPerson(director, fileNameIndex)
        self.addPerson(actor1, fileNameIndex)
        self.addPerson(actor2, fileNameIndex)
        self.addPerson(actor3, fileNameIndex)

        infoText = ''
        prop = {}
        for oneIndex in range(0, rowSize):
          prop[titleList[oneIndex]] = row[oneIndex]
          if len(row[oneIndex]) != 0:
            infoText += ' ' + row[oneIndex].lower()

        # tempCast = row[actor_1_name] + ';' + row[actor_2_name] + ';' + row[actor_3_name]


        infoText += storyLineDict[fileNameIndex]

        castText = ';'.join(castDict[fileNameIndex])
        infoText += ';'.join(keywordsDict[fileNameIndex])
        infoText += castText.lower()

        self.allData[fileNameIndex] = {
          'title': row[movie_title],
          'text': infoText,
          'date': row[title_year],
          'prop': prop,
          'cast': castDict[fileNameIndex],
          'director': director,
          'person': castText + ';' + director,
          'storyLine': storyLineDict[fileNameIndex],
          'genres': row[genres].replace('|', ';'),
          'keywords': keywordsDict[fileNameIndex],
          'index': fileNameIndex
          # 'keywords': (row[plot_keywords]).replace('|', ';')
        }
        fileNameIndex += 1

  def getTopicFromFaces(self, faceStr):
    facesArr = faceStr.split(',')
    topics = []
    faceCounter = 0
    for oneFace in facesArr:
      faceCounter += 1
      if faceCounter >= MAX_SEARCH_PERSON:
        break
      if oneFace in self.personToTopic:
        topics += self.personToTopic[oneFace]
    return topics

  def getRightConj(self, rightExpression):
    lg = len(rightExpression)
    conj = 'AND'
    rightExp = ''
    for i in range(lg-1):
      if rightExpression[i].get('conj') != None:
        conj = rightExpression[i]['conj']
        rightExp = rightExpression[i+1:]
        break
    return {
      'rightExpression': rightExp,
      'conj': conj
    }

  def combineLeftRightResults(self, leftRes, rightRes):
    res = []
    for i in leftRes:
      res.append(i)
    for oneRes in rightRes:
      if oneRes not in leftRes:
        leftRes.append(oneRes)
    return leftRes

  def conjLeftRightResults(self, leftRes, rightRes):
    res = []
    for i in leftRes:
      if i in rightRes:
        res.append(i)
    return res

  def matchFaceToTopics(self, faceName, topicTarget):
    res = []
    if faceName in self.personToTopic:
      tempRes = self.personToTopic[faceName]
      for oneTopic in tempRes:
        if oneTopic in topicTarget:
          res.append(oneTopic)
    return res
  
  def matchKeywordToTopics(self, keyword, topicTarget):
    res = []
    if keyword == '':
      return res
    for oneTopic in topicTarget:
        contentText = self.allData[oneTopic]['text']
        if keyword in contentText.lower():
          res.append(oneTopic)
    return res

  def logicalParser(self, topicTarget, expression):
    expSize = len(expression)
    if expSize == 0:
      return []
    elif expSize == 1:
      if expression[0].get('text') != None:
        return self.filterMethod(expression[0]['text'], topicTarget)
      else:
        return []
    else:
      if expression[0].get('text') != None:
        leftExpression = [expression[0]]
        rightInfo = self.getRightConj(expression[1:])
        rightExpression = rightInfo['rightExpression']
        conjExpression = rightInfo['conj']
        
      elif expression[0].get('bracket') != None:
        conjExpression = 'AND'
        if expression[0]['bracket'] == '(':
          count = 1
          startIndex = 1
          endIndex = 0
          for i in range(1, expSize):
            if expression[i].get('bracket') != None:
              if expression[i]['bracket'] == '(':
                count += 1
              elif expression[i]['bracket'] == ')':
                count -= 1
                if count == 0:
                  endIndex = i
                  break
          leftExpression = expression[startIndex : endIndex]
          rightInfo = self.getRightConj(expression[endIndex+1 :])
          rightExpression = rightInfo['rightExpression']
          conjExpression = rightInfo['conj']
        else:
          leftExpression = expression[1:]
          rightExpression = ''
      elif expression[0].get('conj') != None:
        leftExpression = expression[1:]
        rightExpression = ''
      
    leftResults = self.logicalParser(topicTarget, leftExpression)
    if conjExpression == 'AND':
      return self.logicalParser(leftResults, rightExpression)
    else:
      rightResults = self.logicalParser(topicTarget, rightExpression)
    return self.combineLeftRightResults(leftResults, rightResults)


