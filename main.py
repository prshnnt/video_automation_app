from data import text
from utils import *
lyrics = Lyrics()
text =  text.split('\n')
keyword = "india"
pics_list =  image_scraper(keyword)

for i in text:
	if i=="" or i.isspace():
		continue
	print(i)
	lyrics.append(i,pics_list)

video = Video(lyrics.get_lyrics())
video.run()