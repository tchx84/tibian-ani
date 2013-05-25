#!/usr/bin/python

# Copyright (c) 2010 Martin Abente Lahaye. - martin.abente.lahaye@gmail.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA

import httplib
import sys
import json
import os
import logging
import re

from worldtime import Worldtime

TIBIA_URI = 'www.tibia.com'
TIBIA_WORLD_URI = '/community/?subtopic=worlds&world='
TIBIA_CHAR_URI = '/community/?subtopic=characters&name='

WORLD_SPLIT_STR = '<'
WORLD_STOP_STR = '\" >'

script_path = os.path.abspath(__file__)
SAMPLES_PATH = os.path.join(os.path.dirname(script_path), 'samples/')
LOG_PATH = os.path.join(os.path.dirname(script_path), 'log', 'check.log')

logging.basicConfig(filename=LOG_PATH, level=logging.INFO)


def get_contents(full_uris):
    contents = []
    connection = httplib.HTTPConnection(TIBIA_URI)

    for uri in full_uris:
        uri = uri.replace(' ', '+')
        logging.info('Retrieving content from %s' % TIBIA_URI+uri)

        try:
            connection.request("GET", uri)
            response = connection.getresponse()
            contents.append(response.read())
        except Exception, err:
            logging.error('Could not retrieve content from %s because of %s' %
                         (uri, str(err)))

    connection.close()
    return contents


def get_characters(content, split_str, stop_str):
    characters = []

    for chunk in content.split(split_str):
        l_index = chunk.find(TIBIA_CHAR_URI)
        if l_index != -1:
            r_index = chunk.find(stop_str)
            l_index += len(TIBIA_CHAR_URI)
            name = chunk[l_index:r_index]\
                .replace('+', ' ')\
                .replace('%27', '\'')
            characters.append(name)

    return characters


def dump_sample(characters, name):
    datetime_str = Worldtime.now()
    data = {'name': name, 'datetime': datetime_str, 'characters': characters}

    filename = SAMPLES_PATH+name+'-'+re.sub(r':|\.|\ ', r'-', datetime_str)

    datafile = open(filename, 'w')
    json.dump(data, datafile)
    datafile.close()
    logging.info('Saved file at %s' % filename)


def main():
    contents_uris = []
    names = sys.argv[1:]

    for name in names:
        contents_uris.append(TIBIA_WORLD_URI+name)
    contents = get_contents(contents_uris)

    for index, content in enumerate(contents):
        online_characters = get_characters(content,
                                           WORLD_SPLIT_STR,
                                           WORLD_STOP_STR)
        dump_sample(online_characters, names[index])

if __name__ == "__main__":
    main()
