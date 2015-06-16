#!/usr/bin/env python

"""
The categories an article can possibly
fall within.
"""
possibleCategories = [	"Binnenland",
						"Buitenland",
						"Politiek",
						"Economie",
						"Cultuur & Media",
						"Opmerkelijk",
						"Koningshuis"]

"""
The article metadata tags, as where
they can be found in the html document
of the article.
- 	The first item should have the key "type"
	and the value of the html element it is in,
	such as "h1" or "p".
- 	The second item should have a key of a unique
	css identifier of that element, which is usually
	either "class" or "id". The value should then be
	its value.
"""
titleTag = {"type": "h1", "class": "article__title"}
categoriesTag = {"type": "a", "class": "link-grey"}
textTag = {"type": "p"}
imageTag = {"type": "img", "class": "media-full"}
