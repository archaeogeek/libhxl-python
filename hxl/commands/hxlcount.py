"""
Script to count distinct values in a HXL dataset.
David Megginson
October 2014

Counts all combinations of the tags specified on the command line. In
the command-line version, you may omit the initial '#' from tag names
to avoid the need to quote them.

Only the *first* column with each hashtag is currently used.

Command-line usage:

  python -m hxl.scripts.count <tag> <tag...> < DATA_IN.csv > DATA_OUT.csv

Program usage:

  import sys
  from hxl.scripts.hxlcount import hxlcount

  hxlcount(sys.stdin, sys.stdout, tags)

License: Public Domain
Documentation: http://hxlstandard.org
"""

import sys
import csv
import json
import argparse
from hxl.commands import parse_tags
from hxl.parser import HXLReader

def hxlcount(input, output, tags):
    """
    Count occurances of value combinations for a set of tags.
    """

    parser = HXLReader(input)
    writer = csv.writer(output)

    stats = {}

    # Add up the value combinations in the rows
    for row in parser:
        values = []
        for tag in tags:
            value = row.get(tag)
            if value is not False:
                values.append(value)

        if values:
            # need to use a tuple as a key
            key = tuple(values)
            if stats.get(key):
                stats[key] += 1
            else:
                stats[key] = 1

    # Write the HXL hashtag row
    tags.append('#x_total_num')
    writer.writerow(tags)

    # Write the stats, sorted in value order
    for aggregate in sorted(stats.items()):
        data = list(aggregate[0])
        data.append(aggregate[1])
        writer.writerow(data)

def run(args, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr):
    """
    Run hxlcount with command-line arguments.
    @param args A list of arguments, excluding the script name
    @param stdin Standard input for the script
    @param stdout Standard output for the script
    @param stderr Standard error for the script
    """

    # Command-line arguments
    parser = argparse.ArgumentParser(description = 'Generate aggregate counts for a HXL dataset')
    parser.add_argument(
        'infile',
        help='HXL file to read (if omitted, use standard input).',
        nargs='?',
        type=argparse.FileType('r'),
        default=stdin
        )
    parser.add_argument(
        'outfile',
        help='HXL file to write (if omitted, use standard output).',
        nargs='?',
        type=argparse.FileType('w'),
        default=stdout
        )
    parser.add_argument(
        '-t',
        '--tags',
        help='Comma-separated list of column tags to count.',
        metavar='tag,tag...',
        type=parse_tags,
        default='loc,org,sector,adm1,adm2,adm3'
        )
    args = parser.parse_args(args)

    hxlcount(args.infile, args.outfile, args.tags)


# end
