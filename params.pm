# Package of parameters. 

#! /usr/bin/perl

package params;

use strict;
use warnings;

our $bar = "This is the package's bar value!";

our $database = "photos.db";

## Table names
	our $photoTableName = "Photos";
	our $peopleTableName = "People";
	our $linkerTableName = "Linker";
	our $rootTableName = "Root_Dirs";

# Table column names 
	## Photo table
	our $photoKeyColumn = "photo_key";
	our $photoFileColumn = "photo_file";
	our $photoDateColumn = "photo_date";
	our $modifyDateColumn = "modification_date";
	our $rootDirNumColumn = "root_dir_num";

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

1;