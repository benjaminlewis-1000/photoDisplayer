

#! /usr/bin/perl

package accessQueries;

use params;

use strict;
use warnings;

# TODO: Get the parameterized versions of fields in here. 

our @accessQueriesList = (
	qq/Select $params::photoKeyColumn from $params::photoTableName WHERE $params::photoYearColumn = 2016 and $params::photoMonthColumn = 6
Intersect SELECT * FROM 
(Select $params::linkerPhotoColumn from $params::linkerTableName WHERE $params::linkerPeopleColumn = 1 
UNION
Select $params::linkerPhotoColumn from $params::linkerTableName where $params::linkerPeopleColumn = 2)/, # Taken in Jan 2016, with $params::linkerPeopleColumn 1 OR $params::linkerPeopleColumn 2 (Ben and Jessica together)

qq/Select $params::photoKeyColumn from $params::photoTableName WHERE $params::photoYearColumn = 2016 and $params::photoMonthColumn = 6
Intersect SELECT * FROM 
(Select $params::linkerPhotoColumn from $params::linkerTableName WHERE $params::linkerPeopleColumn = 1 
INTERSECT
Select $params::linkerPhotoColumn from $params::linkerTableName where $params::linkerPeopleColumn = 2)/, # Taken in Jan 2016, with $params::linkerPeopleColumn 1 AND $params::linkerPeopleColumn 2 (Ben and Jessica together)

	qq/Select $params::photoKeyColumn from $params::photoTableName WHERE $params::photoYearColumn = 2016/, # All $params::photoTableName taken in a given year

	qq/Select $params::linkerPhotoColumn from $params::linkerTableName WHERE $params::linkerPeopleColumn = 1 
INTERSECT 
Select $params::linkerPhotoColumn from $params::linkerTableName where $params::linkerPeopleColumn = 2 /, # $params::photoTableName with BOTH person1 AND person2 in them 

qq/SELECT $params::photoKeyColumn from $params::photoTableName WHERE $params::photoDateColumn >= "2016-09-15 00:00:00" and $params::photoDateColumn <= "2016-09-17 99:99:99"/, # $params::linkerPhotoColumn is on the 15th, 16th, or 17th of Sep. 2016. 9's are for ASCII values. Can obviously be tailored. Easy for date ranges, hard for specific months. 

qq/SELECT $params::photoKeyColumn from $params::photoTableName WHERE $params::photoMonthColumn = 5/,

			);

my $access_filenames = qq/SELECT photo_file, root_dir_num, $params::photoKeyColumn from $params::photoTableName where $params::photoKeyColumn in (5, 6, 7, 8, 9, 10)/;

1;

