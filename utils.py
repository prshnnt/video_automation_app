import json
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import random
from moviepy.editor import *
import requests
from bs4 import BeautifulSoup
import os
import re

# Constants
LYRICS_PATH = ".\\config\\lyrics.json"
AUDIO_PATH = ".\\out\\audio\\" 
class Lyrics:
	def __init__(self):
		self.data = []

	#  Append lyrics and append path of photos fetched using keywords
	def append(self,lyric,pics_list):
		self.data.append({
			'lyric':lyric,
			'frame':pics_list
			})
	# Get lyrics object
	def get_lyrics(self):
		return self.data

	# dump lyrics object 
	def save(self):
		json.dump(data,LYRICS_PATH)


class Video :
	def __init__(self,lyrics:list):
		self.lyrics:list = lyrics
		self.frames:list = []

	def make_audioclip(self,text, name ):
		try:
			tts = gTTS(text=text, lang='en')
			if text and not text.isspace():
				tts.save(name)
				return True
			else:
				return False
		except AssertionError:
			return False
	def add_line_breaks(self,text, max_characters_per_line=50):
		words = text.split(" ")
		lines = []
		current_line = ""

		for word in words:
			if len(current_line) + len(word) + 1 <= max_characters_per_line:
				current_line += word + " "
			else:
				lines.append(current_line.strip())
				current_line = word + " "

		if current_line:
			lines.append(current_line.strip())

		return "\n".join(lines)

	def create_image(self,image_path,text):
		background_image = Image.open(image_path)
		font_path = ".\\font\\NightPumpkind-1GpGv.ttf"
		font_size = 10
		font = ImageFont.truetype(font_path, font_size)

		# Create a drawing object
		draw = ImageDraw.Draw(background_image)

		# Calculate text size and position
		text_width, text_height = (10,50)
		image_width, image_height = background_image.size
		text_x = (image_width - text_width) // 2
		text_y = image_height - text_height - 20

		# Add text to the image
		draw.text((1, text_y), text, font=font, fill=(0,0,0))
		# Convert Pillow image to NumPy array
		image_array = np.array(background_image)

		return image_array

	def make_frame(self,data:dict):
		lyric:str = data.get('lyric')
		name =  AUDIO_PATH + "audio"+str(int(random.random()*1000)) + ".wav"

		if self.make_audioclip(lyric,name):
			audio_clip = AudioFileClip(name)
			video_duration = audio_clip.duration

			text = self.add_line_breaks(lyric)
			clip = None
			if data['frame']:
				img =random.choice(data['frame'])
				arr = self.create_image(img,text)
				clip = ImageClip(arr,duration=video_duration)
			else:			
				clip = TextClip(
					text,
					font=random.choice(FONT_TYPE) ,
					fontsize=30,
					color='white',
					bg_color='black',
					size=(1280, 720),
					duration=video_duration,
				)
			clip = clip.set_audio(audio_clip)
			clip = clip.fadein(2)
			self.frames.append(clip)

	def compile_video(self):
		video = concatenate_videoclips(self.frames)
		return video
	def save(self,video):
		print("Compiling...")
		video.write_videofile(".\\out\\video.mp4", codec='libx264',
							  audio_codec='aac', fps=24)
	def run(self):
		for i in self.lyrics:

			self.make_frame(i)
		self.save(self.compile_video())



def scrape_images_urls(query):
	search_url = f'https://commons.wikimedia.org/w/index.php?search={query}&title=Special:MediaSearch&go=Go&type=image'
	response = requests.get(search_url)
	
	if response.status_code == 200:
		soup = BeautifulSoup(response.text, 'html.parser')
		image_elements = soup.find_all('img', class_='sd-image')
		image_urls = [img.get('data-src').replace(r'(\w{3})px-', '600px-') for img in image_elements if img.get('data-src')]
		return image_urls
	else:
		return []

def image_scraper(search_query):
	if not search_query:
		print('Please provide a search query.')
	else:
		image_urls = scrape_images_urls(search_query)

		download_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')
		paths =[]
		# Create the directory if it doesn't exist
		if not os.path.exists(download_path):
			os.makedirs(download_path)

		for index, image_url in enumerate(image_urls):
			response = requests.get(image_url)
			if response.status_code == 200:
				image_filename = f'image_{index + 1}.jpg'
				image_path = os.path.join(download_path, image_filename)
				with open(image_path, 'wb') as f:
					f.write(response.content)
				print(f'Downloaded {image_filename}')
				paths.append(image_path)
			# else:
			# 	print(f'Error downloading image {index + 1}')

		# print(f'Images downloaded and saved to {download_path}')
		return paths
