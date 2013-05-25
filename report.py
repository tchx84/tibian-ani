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

import json
import os
import sys
import re
import datetime

from optparse import OptionParser

from checkguild import get_guild_characters

parser = OptionParser()
parser.add_option("-w", "--world", dest="world_name",
                  default=None, help='specify the name of the world')
parser.add_option("-d", "--weekday", dest="weekday",
                  default=None, help='specify the day of the week')
parser.add_option("-c", "--character", dest="char_name",
                  default=None, help='specifiy the name of the character')
parser.add_option("-g", "--guild", dest="guild_name",
                  default=None, help='specifiy the name of the guild')

script_path = os.path.abspath(__file__)
CURRENT_PATH = os.path.dirname(script_path)
SAMPLES_PATH = os.path.join(CURRENT_PATH, 'samples/')
REPORTS_PATH = os.path.join(CURRENT_PATH, 'reports/')
HTML_PATH = os.path.join(CURRENT_PATH, 'html/')

HTML_HEADER = None
with open(os.path.join(HTML_PATH, 'HEADER'), 'r') as f:
    HTML_HEADER = f.read()

HTML_FOOTER = None
with open(os.path.join(HTML_PATH, 'FOOTER'), 'r') as f:
    HTML_FOOTER = f.read()


def load_samples(name):
    samples = []

    for sample in os.listdir(SAMPLES_PATH):
        if sample.startswith(name):
            sample_path = os.path.join(SAMPLES_PATH, sample)
            sample_file = open(sample_path)
            sample_raw = sample_file.read()
            sample_data = json.loads(sample_raw)
            samples.append(sample_data)
            sample_file.close()

    return samples


def _pleasant_exit(msg):
        print msg
        sys.exit(-1)


def _get_weekday(date_str):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    return date.strftime('%A')


def _get_hour(date_str):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    return date.hour


def analyze_activity(samples, weekday=None, names=None, normalized=False):
    stats = {}
    max_activity = None
    min_activity = None

    for sample in samples:

        sample_date = sample['datetime']
        if (weekday is not None) and (weekday != _get_weekday(sample_date)):
            continue

        frame = _get_hour(sample_date)
        if frame not in stats:
            stats[frame] = {'samples': 0.0,
                            'activity': 0.0,
                            'average': 0.0,
                            'value': 0.0}
        stats[frame]['samples'] += 1.0

        for character in sample['characters']:

            if (names is not None) and (character not in names):
                continue

            stats[frame]['activity'] += 1.0

    frames = stats.keys()
    frames.sort()

    for frame in frames:
        average = stats[frame]['activity']/stats[frame]['samples']

        if (max_activity <= average or max_activity is None):
            max_activity = average

        if (min_activity >= average or min_activity is None):
            min_activity = average

        stats[frame]['average'] = average

    if (max_activity == min_activity):
        if (max_activity == 0.0 or min_activity is None):
            _pleasant_exit('Could not find samples for your request')
        if normalized:
            _pleasant_exit('Not enough samples to process'
                           ' or this character is always on')

    for frame in frames:
        if normalized:
            value = (stats[frame]['average'] - min_activity)
            percent = (1.0 / (max_activity - min_activity))
            stats[frame]['value'] = value * percent
        else:
            stats[frame]['value'] = stats[frame]['average']

    return stats


def print_for_google(stats, weekday, name):
    content = HTML_HEADER

    content += '\n[\'Hour\''
    for stat in stats:
        content += ',\'%s\'' % stat['name']
    content += '],\n'

    frames = stats[0]['activity'].keys()
    frames.sort()

    for frame in frames:

        content += '[\'%s\'' % frame
        for stat in stats:
            content += ',%f' % stat['activity'][frame]['value']
        content += '],\n'

    if weekday is None:
        weekday = "All Week"
    content += (HTML_FOOTER % weekday)

    filename = '%s-%s.html' % (name, re.sub(r':|\.|\ ', r'-',
                               str(datetime.datetime.now())))
    filepath = os.path.join(REPORTS_PATH, filename)
    output = open(filepath, 'w')
    output.write(content)
    output.close()
    print 'Output saved at %s' % filepath


def main():
    options, args = parser.parse_args()

    if options.world_name is None:
        print "\nYou must specify the world name"
        parser.print_help()
        sys.exit(-1)

    stats = []
    samples = None
    name = options.world_name
    normalized = options.char_name is not None\
        or options.guild_name is not None

    samples = load_samples(name)
    stat = {'activity': analyze_activity(samples, options.weekday,
            None, normalized), 'name': name}
    stats.append(stat)

    if options.guild_name is not None:
        name = options.guild_name
        names = get_guild_characters(name)
        stat = {'activity': analyze_activity(samples, options.weekday,
                names, normalized), 'name': name}
        stats.append(stat)

    if options.char_name is not None:
        name = options.char_name
        names = [name]
        stat = {'activity': analyze_activity(samples, options.weekday,
                names, normalized), 'name': name}
        stats.append(stat)

    print_for_google(stats, options.weekday, name)

if __name__ == "__main__":
        main()
