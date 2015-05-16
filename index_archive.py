#!/usr/bin/env python

import json
from sys import exit
from os import path, chdir

from settings.general_settings import archiveName
from classes import Article, Collection

dir = path.dirname(__file__)


def main():
    """
    Imports and builds an archive of news articles.
    """

    # import an existing archive.
    archive = import_archive(archiveName)

    # build ElasticSearch index of archive
    Collection.build_index(archive)
    Collection.index_articles(archive)


def import_archive(fileName):
    """
    Imports an existing news archive.
    -   fileName should be the name of a local JSON file, 
        with an ElasticSearch-friendly format, in the 
        "/files" subfolder. 
    """
    fileName = archiveName + ".json"

    print 'Attempting to import from "files/' + fileName + '"...'

    chdir("files")

    if path.isfile(fileName):
        content = json.loads(open(fileName, "rb").read())

        for k, v in content.iteritems():
            print "Imported: %s, %d articles" % (k, len(v))
            print

        archive = Collection(content.keys()[0], content.values()[0])
        return archive
    else:
        print "File not found."
        exit()

# execute main
if __name__ == "__main__":
    main()
