#!/usr/bin/python2
# Movie-manager is a script for renaming movies from imdb
# Copyright (C) 2015 Dylan Baker

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""A small simple script for renaming media using imdb data."""

from __future__ import print_function, division, absolute_import
import os
import re
import argparse

from imdb import IMDb

LOOKUP = IMDb('http')
PARSE_FILE = re.compile(r'(?P<title>[\w\s\,\!\.\-\&\'\:]*)'
                        r'(\([IVX]*\)\s+)?(?P<year>\(\d*\))?')
_KINDS = set([
    'movie',
    'tv series',
    'tv mini series',
    'video game',
    'video movie',
    'tv movie',
    'episode',
])

# A set of files that shouldn't be bothered with.
IGNORE_FILES = set([
    'Thumbs.db',
])


def parse():
    """Parse commandline arguments and return the argparse namespace."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'directory',
        help='A directory to search for movie files and folders')
    parser.add_argument(
        '-k', '--kind',
        choices=_KINDS,
        default='movie',
        help='The kind of files to look for. Default: movie')

    return parser.parse_args()


def select_correct_movie(choices):
    """When there is more than one option print a list of options and allow
    selection.

    This makes use of a recursive closure to force a user to select a valid
    value.

    Note, it is possible to reach maximum recursion by entering bad input too
    many times. There is not gauard against this, as this is a fairly basic
    script meant for a single simple purpose.

    """
    def _reader():
        """Recurisve closure helper."""
        try:
            index = int(raw_input('Choice: '))
            return choices[index]
        except ValueError:
            print("Invalid input, must be a number")
            return _reader()
        except IndexError:
            print("Invalid input, must be one of listed choices")
            return _reader()

    for i, value in enumerate(choices):
        try:
            year = value['year']
        except KeyError:
            # If there is not year there is no point in renaming it.
            continue

        print('{i}: {name} - {year}'.format(
            i=i, name=value['title'].encode('utf-8'), year=year))

    print('Select the correct title')
    return _reader()


def rename(original, new):
    """Rename an old file to a new name."""
    if os.path.exists(new):
        raise Exception('Warning: {} already exists!'.format(new))

    if __debug__:
        print('moving "{}" to "{}"'.format(original, new))

    os.rename(original, new)


def main():
    """Main function."""
    args = parse()

    for filename in os.listdir(args.directory):
        if filename in IGNORE_FILES:
            continue

        m = PARSE_FILE.search(filename)
        if m and not m.group('year'):
            # Filter media that is the incorrect type or that is a hiddne value
            # (starts with _)
            imdb = [i for i in LOOKUP.search_movie(m.group('title')) if
                    i['kind'] == args.kind and not i['title'].startswith('_')]

            if not imdb:
                print('No options found for: {}'.format(filename))
                continue

            if len(imdb) > 1:
                print()  # Add newline for easier reading
                print('Ambigous title: {}'.format(filename))
                movie = select_correct_movie(imdb)
            else:
                movie = imdb[0]
                try:
                    movie['year']
                except KeyError:
                    continue

            new_name = u'{} ({})'.format(movie['title'],
                                         movie['year']).encode('utf-8')
            rename(filename, new_name)

        elif __debug__:
            print('Media already correctly formatted: {}'.format(filename))


if __name__ == '__main__':
    main()
