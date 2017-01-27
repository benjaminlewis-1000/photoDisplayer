# Package of parameters. 

#! /usr/bin/perl

package params;

use strict;
use warnings;

our $bar = "This is the package's bar value!";

our $database = "photos_master.db";

our $debug = 0;

our $debug_readXMP = 0;
our $debug_readIn = 1;
our $debugNewRoot = 0;
# map {if (!$_) { ______ } } $params::debug;

## Table names
	our $photoTableName = "Photos";
	our $peopleTableName = "People";
	our $linkerTableName = "Linker";
	our $rootTableName = "Root_Dirs";
	our $metadataTableName = "Metadata";
	our $tempTableName = "TmpPhotoTable";

# Table column names 
	## Photo table
	our $photoKeyColumn = "photo_key";
	our $photoFileColumn = "photo_file";
	our $photoDateColumn = "photo_date";
	our $photoYearColumn = "taken_year";
	our $photoMonthColumn = "taken_month";
	our $photoDayColumn = "taken_day";
	our $photoHourColumn = "taken_hour";
	our $photoMinuteColumn = "taken_minute";
	our $photoGMTColumn = "taken_timezone";
	our $modifyDateColumn = "modification_date";
	our $rootDirNumColumn = "root_dir_num";
	our $insertDateColumn = "inserted_date";

	## People Table
	our $peopleKeyColumn = "people_key";
	our $personNameColumn = "person_name";
	# our $personPicasaID = "person_picasa_id";

	## Linker Table
	our $linkerPeopleColumn = "person";
	our $linkerPhotoColumn = "photo";

	## Root Directory Table
	our $rootKeyColumn = "directory_root_key";
	our $rootDirPath = "root_path";

	## Metadata Table
	our $metadataNameColumn = "item_name";
	our $metadataValueColumn = "item_value";

	### Metadata fields
		our $metadataLastEditedField = "last_edited_date";

# DOESN'T WORK.
# use Data::Dumper::Simple;
# sub getVarName{
# 	my $variable = $_[0];
# 	return (split /=/, Dumper($variable))[0];
# }

1;