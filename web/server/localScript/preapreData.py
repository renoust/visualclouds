import sys
import json
import csv
from os import listdir, path
from urllib.parse import urlparse
import urllib.request

from bs4 import BeautifulSoup
import requests

def getJsonData(path):
  with open(path, 'rb') as loadFile:
    data = json.load(loadFile)
    return data

def saveJsonData(path, data):
  with open(path, 'w') as outFile:
    json.dump(data, outFile)

def savePersonList():
  res = {}
  personList = getJsonData('../data/topic_bcp.json')
  for oneTopic in personList:
    personNameArr = personList[oneTopic]
    for personName in personNameArr:
      if personName not in res:
        res[personName] = [oneTopic]
      else:
        res[personName].append(oneTopic)

  saveJsonData('../data/personToTopicListAll.json', res)

def findPersonFace():
  # personList = getJsonData('../data/haolinProcessed/personToTopicListAll.json')
  faceNameList = listdir('../../client/data/faces')
  nameDict = {}
  for oneFace in faceNameList:
    faceName = oneFace.replace('.jpg', '')
    if faceName not in nameDict:
      nameDict[faceName] = oneFace
  saveJsonData('../data/faceNameDict.json', nameDict)

def buildFakeEmiArr():
  res = []
  nameDict = getJsonData('../data/faceNameDict.json')
  personList = getJsonData('../data/topic_to_persons_kw-all.json')
  # count = 0

  def getDate(strDate):
    return strDate[0:4] + strDate[5:7] + strDate[8:10]

  for i in personList:
    mm = ''
    emiDate = getDate(i)
    
    for oneKey in personList[i]:
      tempArr = []   
      tempArr.append(i)
      tempArr.append(emiDate)
      tempArr.append(oneKey)
      tempArr.append(oneKey)
      tempArr.append('')
      tempArr.append('')
      tempArr.append('')
      tempArr.append('')
      tempArr.append(i)
      tempArr.append(oneKey)

      res.append(tempArr)
  return res
# savePersonList()

def loadCSV(fileName):
  res = []
  with open(fileName, 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in spamreader:
      res.append(row)
  return res

# findPersonFace()

def saveImage(imgPath, imgName):
  urllib.request.urlretrieve(imgPath, imgName)

def imdbDataLoader():
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

  d = loadCSV('movie_metadata.csv')

  fullData = []

  dataSize = len(d)

  fDict = {}
  sDict = {}

  fullDataTitle = []
  for oneCol in d[0]:
    fullDataTitle.append(oneCol)

  fullDataTitle.append('casts')
  fullDataTitle.append('full_plot_keywords')

  fullData.append(fullDataTitle)

  print('%d to proceed'%dataSize)
  resume = False
  last_index = 1
  if resume:
    last_index = max([int(x.replace('.json','')) for x in listdir('../data/keywords/')])
  print('restarting from %d/%d'%(last_index,dataSize))
  
  has_no_small_face = []
  if path.isfile('../has_no_small_face.json'):
    with open('../has_no_small_face.json') as f:
      has_no_small_face = json.load(f)

  has_no_big_face = []
  if path.isfile('../has_no_big_face.json'):
    with open('../has_no_big_face.json') as f:
      has_no_big_face = json.load(f)
    
  has_no_director_face = []
  if path.isfile('../has_no_director_face.json'):
    with open('../has_no_director_face.json') as f:
      has_no_director_face = json.load(f)

  has_no_keyword = []
  if path.isfile('../has_no_keyword.json'):
    with open('../has_no_keyword.json') as f:
      has_no_keyword = json.load(f)

  has_no_storyline = []
  if path.isfile('../has_no_storyline.json'):
    with open('../has_no_storyline.json') as f:
      has_no_storyline = json.load(f)

  for i in range(last_index, dataSize+1):

    with open('../has_no_small_face.json', 'w') as f:
      json.dump(has_no_small_face, f)
    with open('../has_no_big_face.json', 'w') as f:
      json.dump(has_no_big_face, f)
    with open('../has_no_director_face.json', 'w') as f:
      json.dump(has_no_director_face, f)
    with open('../has_no_keyword.json', 'w') as f:
      json.dump(has_no_keyword, f)
    with open('../has_no_storyline.json', 'w') as f:
      json.dump(has_no_storyline, f)

    if i==len(d):
      print ('stopping %d/%d'%(i,dataSize))
      break

    print ('processing %d/%d'%(i,dataSize))
    lk = d[i][movie_imdb_link]

    actor1 = d[i][actor_1_name]
    actor2 = d[i][actor_2_name]
    actor3 = d[i][actor_3_name]

    oneRow = []
    for oneCol in d[i]:
      oneRow.append(oneCol)

    req = None
    castsStr = ''

    target_json = '../data/cast/%d.json'%i
    if not path.isfile(target_json):

      req = requests.get(url=lk)

      html = req.text
      bf = BeautifulSoup(html, features="html.parser")
      casts = bf.find_all('td', {'class': 'primary_photo'})
      director = bf.find('div', {'class': 'credit_summary_item'})

      directorName = d[i][director_name]
      target_file = '../data/face/' + directorName + '.jpg'

      has_erred = False

      if not path.isfile(target_file) and directorName not in has_no_director_face:
        directorPage = "None"
        try:
          directorPage = 'https://www.imdb.com' + director.find('a')['href']
          directReq = requests.get(url=directorPage)
          directHTML = directReq.text
          directPageBf = BeautifulSoup(directHTML, features='html.parser')
          img_primary = directPageBf.find('td', {'id': 'img_primary'})
          if 'img' not in img_primary:
            has_no_director_face.append(directorName)
          else :
            img_primary_address = img_primary.find('img')['src']
            saveImage(img_primary_address, target_file)
        except Exception as e:
          has_erred = True
          print('Cannot load any director face: ' + directorName)
          print (img_primary)
          print(e)

      for oneCast in casts:
        oneInfo = oneCast.find('img')
        castName = oneInfo['title']
        castsStr += castName + '|'

        target_file = '../data/sface/' + castName + '.jpg'
  
        if castName not in sDict and not path.isfile(target_file) and castName not in has_no_small_face:
          if not 'loadlate' in oneInfo:
            has_no_small_face.append(castName)
            sDict[castName] = 0

          else:
            castSmallFaceAddress = "None"
            try:
              castSmallFaceAddress = oneInfo['loadlate']
              saveImage(castSmallFaceAddress, target_file)
              sDict[castName] = 0
            except Exception as e:
              has_erred = True
              print('Cannot load any small face: '+castName+' '+castSmallFaceAddress)
              print(oneInfo)
              print(e)
        else:
          sDict[castName] = 0


        target_file = '../data/face/' + castName + '.jpg'
        if castName not in fDict and not path.isfile(target_file) and castName not in has_no_big_face:
            castPage = "None"
            try:
              castPage = 'https://www.imdb.com' + oneCast.find('a')['href']
              castReq = requests.get(url=castPage)
              castHTML = castReq.text
              castPageBf = BeautifulSoup(castHTML, features='html.parser')
              img_primary = castPageBf.find('td', {'id': 'img_primary'})
              if 'img' not in img_primary:
                has_no_big_face.append(castName)
              else :
                img_primary_address = img_primary.find('img')['src']
                saveImage(img_primary_address, target_file)
              fDict[castName] = 0

            except Exception as e:
              has_erred = True
              print('Cannot load any big face: ' + castName + ' ' + castPage)
              print(img_primary_address)
              print(e)

      if has_erred == False:
        with open(target_json, 'w') as f:
          json.dump(castsStr, f)
    else:
      with open(target_json) as f:
        castsStr = json.load(f)



    oneRow.append(castsStr)

    full_plot_keywords = ''
    target_json = '../data/keywords/%d.json'%i
    if not path.isfile(target_json) and i not in has_no_keyword:

      #print ('grabbing keywords')
      if req == None:
        req = requests.get(url=lk)
        html = req.text
        bf = BeautifulSoup(html, features="html.parser")        

      try:
        keywordLink = bf.find_all('div', {'class': ['se-more', 'canwrap']})
        if len(keywordLink) == 1 or keywordLink[1].find('nobr') == None:
          has_no_keyword.append(i)
        else:
          kwNobr = keywordLink[1].find('nobr')
          kwlink = kwNobr.find('a')['href']
          kwPage = 'https://www.imdb.com' + kwlink
          kwReq = requests.get(url=kwPage)
          kwHTML = kwReq.text
          kwPageBf = BeautifulSoup(kwHTML, features='html.parser')
          kwTable = kwPageBf.find_all('td', {'class': {'sodavote'}})
          for oneTd in kwTable:
            full_plot_keywords += oneTd['data-item-keyword'] + '|'

        with open(target_json, 'w') as f:
          json.dump(full_plot_keywords, f)

      except Exception as e:
        print('Cannot load any plot keywords')
        print(keywordLink)
        print(e)

    else:
      with open(target_json) as f:
        full_plot_keywords = json.load(f)


    story_line = ''
    target_json = '../data/storyline/%d.json'%i
    if not path.isfile(target_json) and i not in has_no_storyline:
      #print ('grabbing keywords')
      if req == None:
        req = requests.get(url=lk)
        html = req.text
        bf = BeautifulSoup(html, features="html.parser")        

      try:
          storyLink = bf.find('div', {'id': ['titleStoryLine']})
          
          try:
            storylinediv = storyLink.find('div', {'class': ['inline canwrap']})
            storyline = storylinediv.find('span')
            story_line = storyline.text.strip()
          except AttributeError as e:
              print('Skipping to summary storyline')
              print(lk)
              print(e)
              summaryLink = bf.find('div', {'class': ['summary_text']})
              story_line = storyLink.text.strip()

          with open(target_json, 'w') as f:
            json.dump(story_line, f)

      except Exception as e:
        print('Cannot load any storyline')
        print(storyLink)
        print(e)

    else:
      with open(target_json) as f:
        story_line = json.load(f)

    oneRow.append(full_plot_keywords)
    fullData.append(oneRow)

  with open('full_metadata.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(fullData)


# emiArr = buildFakeEmiArr()
# saveJsonData('../data/jpEmisTopics.json', emiArr)

# imdbDataLoader()
