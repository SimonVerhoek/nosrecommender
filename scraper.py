#!/usr/bin/env python

from bs4 import BeautifulSoup
from urllib2 import urlopen

url = "http://nos.nl/artikel/2025837-rutte-athene-moet-ons-medicijn-slikken.html"

soup = BeautifulSoup(urlopen(url))

possibleCategories = ["Binnenland", "Buitenland", "Politiek", "Economie", "Cultuur & Media", "Opmerkelijk"]

titleElement = {"tag": 	"h1", "class": "article__title"}
categoriesElement = {"tag": "a", "class":"link-grey"}
paragraphs = {"tag": "p"}
images = {"tag": "img"}


title = soup.find(titleElement["tag"], {titleElement.keys()[1]:titleElement.values()[1]}).text

categories = []
for item in soup.find_all(categoriesElement["tag"], {categoriesElement.keys()[1]:categoriesElement.values()[1]}):
	if item.string in possibleCategories:
		categories.append(item.string)

print title
print categories
