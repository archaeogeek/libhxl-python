"""
Sort a HXL dataset.
David Megginson
January 2015

The SortFilter class will use numeric sorting for hashtags ending
in _num or _deg, and date-normalised sorting for hashtags ending in
_date.

Warning: this filter reads the entire source dataset into memory
before sorting it.

License: Public Domain
Documentation: https://github.com/HXLStandard/libhxl-python/wiki
"""

import dateutil.parser
from hxl.common import pattern_list
from hxl.model import Dataset, TagPattern


class SortFilter(Dataset):
    """
    Composable filter class to sort a HXL dataset.

    This is the class supporting the hxlsort command-line utility.

    Because this class is a {@link hxl.model.Dataset}, you can use
    it as the source to an instance of another filter class to build a
    dynamic, single-threaded processing pipeline.

    Usage:

    <pre>
    source = HXLReader(sys.stdin)
    filter = SortFilter(source, tags=[TagPattern.parse('#sector'), TagPattern.parse('#org'), TagPattern.parse('#adm1']))
    write_hxl(sys.stdout, filter)
    </pre>
    """

    def __init__(self, source, tags=[], reverse=False):
        """
        @param source a HXL data source
        @param tags list of TagPattern objects for sorting
        @param reverse True to reverse the sort order
        """
        self.source = source
        self.sort_tags = pattern_list(tags)
        self.reverse = reverse
        self._iter = None

    @property
    def columns(self):
        """
        Return the same columns as the source.
        """
        return self.source.columns

    def __iter__(self):
        """
        Sort the dataset first, then return it row by row.
        """

        # Closures
        def make_key(row):
            """Closure: use the requested tags as keys (if provided). """

            def get_value(pattern):
                """Closure: extract a sort key"""
                raw_value = pattern.get_value(row)
                if pattern.tag.endswith('_num') or pattern.tag.endswith('_deg'):
                    # left-pad numbers with zeros
                    try:
                        raw_value = str(float(raw_value)).zfill(15)
                    except ValueError:
                        pass
                elif pattern.tag.endswith('_date'):
                    # normalise dates for sorting
                    raw_value = dateutil.parser.parse(raw_value).strftime('%Y-%m-%d')
                return raw_value.upper() if raw_value else ''

            if self.sort_tags:
                return [get_value(pattern) for pattern in self.sort_tags]
            else:
                return row.values

        # Main method
        return iter(sorted(self.source, key=make_key, reverse=self.reverse))
            
# end