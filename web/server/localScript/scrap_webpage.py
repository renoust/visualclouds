import os
import subprocess
import csv
from PIL import Image
from progress.bar import Bar



def loadCSV(fileName):
  res = []
  with open(fileName, 'r') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in spamreader:
      res.append(row)
  return res


web_path = 'http://www.imdb.com/title/tt0073195/?ref_=fn_tt_tt_1'
image_path = '/work/news/FaceCloud/Web_imbd/server/data/thumbs/1.png'

def scrap_image(web_path, image_path):
    cmd = ['webkit2png', '-T', '-s', '0.10', web_path, '-o', image_path]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    o, e = proc.communicate()

    #print('Output: ' + o.decode('ascii'))
    #print('Error: '  + e.decode('ascii'))
    #print('code: ' + str(proc.returncode))

    margin_width = 197
    box = [margin_width,0,0,0]


    try:
        im = Image.open(image_path+'-thumb.png')
        size = im.size
        box[2] = size[0]-margin_width
        box[3] = 400

        im = im.crop(box)
        im.save(image_path, "PNG")
        os.remove(image_path+'-thumb.png')

    except IOError as e:
        print "cannot create thumbnail for '%s'" % image_path
        print e

    

d = loadCSV('/work/news/FaceCloud/Web_imbd/server/data/movie_metadata.csv')

thumb_output = '/work/news/FaceCloud/Web_imbd/server/data/thumbs/'

bar = Bar('Processing', max=len(d))

for i, val in enumerate(d):
    if i == 0:
        continue
    web_path = val[17]
    image_path = thumb_output+'%d.png'%i
    if os.path.isfile(image_path):
        print 'skipp', i, web_path
        continue
    scrap_image(web_path, image_path)
    print i, web_path
    bar.next()
bar.finish()
#print d[0].index('movie_imdb_link')
#print d[1][17]

#scrap_image(web_path, image_path)