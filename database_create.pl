#! /usr/bin/perl

# cpan DBD::mysql

use warnings;
use strict;

use DBI;
use params;

#TODO: Delete the old database file
#TODO: Database file location better handled
our $dbhandle = DBI->connect("dbi:SQLite:$params::database", "user" , "pass");

# Clean out the old tables so we can create them afresh.
my $dropPhotos = qq/DROP TABLE IF EXISTS $params::photoTableName/;
my $query = $dbhandle->prepare($dropPhotos);
$query->execute() or die $DBI::errstr;

my $dropPeople = qq/DROP TABLE IF EXISTS $params::peopleTableName/;
$query = $dbhandle->prepare($dropPeople);
$query->execute() or die $DBI::errstr;

my $dropLinker = qq/DROP TABLE IF EXISTS $params::linkerTableName/;
$query = $dbhandle->prepare($dropLinker);
$query->execute() or die $DBI::errstr;

create_photo_table();
create_people_table();
create_linker_table();

# End creation of tables.

###############################################
########### subs for table creation ###########
###############################################

# Create the photo primary key and filename table
sub create_photo_table{
	# Create the database table, where photo_key is the primary key and photo_file is the file name 
	my $sql_quer = qq/CREATE TABLE $params::photoTableName (
	    $params::photoKeyColumn  INTEGER PRIMARY KEY AUTOINCREMENT
	                      UNIQUE,
	    $params::photoFileColumn STRING,
	    $params::photoDateColumn STRING
	); /;

	# Prepare and execute the statement
	my $sub_state_handle = $dbhandle->prepare($sql_quer);
	$sub_state_handle->execute() or die $DBI::errstr;
}

# Create the people table
sub create_people_table{
	
	# Create the database table, where photo_key is the primary key and photo_file is the file name 
	my $sql_quer = qq/CREATE TABLE $params::peopleTableName (
	    $params::peopleKeyColumn       BIGINT PRIMARY KEY
	                            UNIQUE,
	    $params::personNameColumn      STRING,
	    $params::personPicasaID BIGINT
	);/;

	my $sub_state_handle = $dbhandle->prepare($sql_quer);
	$sub_state_handle->execute() or die $DBI::errstr;
}

# Create the linkage table
sub create_linker_table{
	my $sql_quer = qq/CREATE TABLE $params::linkerTableName (
	    $params::linkerPhotoColumn  BIGINT REFERENCES $params::photoTableName ($params::photoKeyColumn),
	    $params::linkerPeopleColumn BIGINT REFERENCES $params::peopleTableName ($params::peopleKeyColumn) 
	);/;

	my $sub_state_handle = $dbhandle->prepare($sql_quer);
	$sub_state_handle->execute() or die $DBI::errstr;

}