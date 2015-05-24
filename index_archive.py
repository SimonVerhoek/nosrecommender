#!/usr/bin/env python

from settings.general_settings import archiveName
from classes import Article, Collection


def main():
    """
    Imports and builds an archive of news articles.
    """

    # import an existing archive.
    #archive = import_archive(archiveName)
    archive = Collection(archiveName)
    archive.import_from_json(archiveName)

    # build ElasticSearch index of archive
    Collection.build_index(archive)
    Collection.index_articles(archive)

# execute main
if __name__ == "__main__":
    main()
