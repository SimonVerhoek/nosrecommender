#!/usr/bin/env python

import re
from bs4 import BeautifulSoup
from urllib2 import urlopen

url = "http://nos.nl/artikel/2025837-rutte-athene-moet-ons-medicijn-slikken.html"

soup = BeautifulSoup(urlopen(url))

possibleCategories = ["Binnenland", "Buitenland", "Politiek", "Economie", "Cultuur & Media", "Opmerkelijk"]

titleElement = {"tag": 	"h1", "class": "article__title"}
categoriesElement = {"tag": "a", "class":"link-grey"}
paragraphs = {"tag": "p"}
images = {"tag": "img"}


#title = soup.find("h1", {"class":titleClass}).text

#categories = []
#for sibling in soup.find_all("span", {"class":"icon-tag ico-space-right link-grey"})[0].next_siblings:
#	# filter out comma
#	if "," not in sibling:
#		categories.append(sibling.string)
categories = []

for item in soup.find_all(categoriesElement["tag"], {categoriesElement.keys()[1]:categoriesElement.values()[1]}, href=re.compile("/nieuws/")):
	print categories.append(item.string)

print categories
