#!/usr/bin/env python

from bs4 import BeautifulSoup
from urllib2 import urlopen

url = "http://nos.nl/artikel/2025837-rutte-athene-moet-ons-medicijn-slikken.html"

soup = BeautifulSoup(urlopen(url))

possibleCategories = ["Binnenland", "Buitenland", "Politiek", "Economie", "Cultuur & Media", "Opmerkelijk"]

titleTag = {"type": "h1", "class": "article__title"}
categoriesTag = {"type": "a", "class":"link-grey"}
textTag = {"type": "p"}
imageTag = {"type": "img", "class":"media-full"}

def scrape_contents(url):
	soup = BeautifulSoup(urlopen(url))

	# title
	title = soup.find(titleTag["type"], {titleTag.keys()[1]:titleTag.values()[1]}).text

	# categories
	categories = []
	for item in soup.find_all(categoriesTag["type"], {categoriesTag.keys()[1]:categoriesTag.values()[1]}):
		if item.string in possibleCategories:
			categories.append(item.string)

	# body text
	body = ""
	for paragraph in soup.find_all(textTag["type"]):
		body += paragraph.text

	# header image
	image = soup.find(imageTag["type"], {imageTag.keys()[1]:imageTag.values()[1]}).get("src")

	return title, categories, body, image

print scrape_contents(url)