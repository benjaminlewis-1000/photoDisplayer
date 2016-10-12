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

# Table column names 
	## Photo table
	our $photoKeyColumn = "photo_key";
	our $photoFileColumn = "photo_file";
	our $photoDateColumn = "photo_date";

	## People Table
	our $peopleKeyColumn = "people_key";
	our $personNameColumn = "person_name";
	# our $personPicasaID = "person_picasa_id";

	## Linker Table
	our $linkerPeopleColumn = "person";
	our $linkerPhotoColumn = "photo";


1;