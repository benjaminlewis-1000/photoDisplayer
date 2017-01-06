#! /usr/bin/perl

# cpan DBD::mysql

use warnings;
use strict;

use DBI;
use params;

#TODO: Delete the old database file
#TODO: Database file location better handled
our $dbhandle;

my $count_args = @ARGV ;

if ($count_args == 1) {
	my $db = $ARGV[0];
	if ($db =~ /db$/){
		print "valid";
		$params::database = $db;
	}
} 


dbConnect();
dropTables();
create_photo_table();
create_people_table();
create_linker_table();
create_root_dir_table();

# End creation of tables.

sub dbConnect{
	$dbhandle = DBI->connect("dbi:SQLite:$params::database", "user" , "pass");
}

sub dropTables{
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

	my $dropRootDirs = qq/DROP TABLE IF EXISTS $params::rootTableName/;
	$query = $dbhandle->prepare($dropRootDirs);
	$query->execute() or die $DBI::errstr;
	
}

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
	    $params::photoDateColumn STRING,
	    $params::modifyDateColumn STRING,
	    $params::rootDirNumColumn STRING
	); /;

	# Prepare and execute the statement
	my $sub_state_handle = $dbhandle->prepare($sql_quer);
	$sub_state_handle->execute() or die $DBI::errstr;
}

sub create_root_dir_table{
	my $sql_quer = qq/CREATE TABLE $params::rootTableName (
		$params::rootKeyColumn INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
		$params::rootDirPath STRING
	); /;

	my $sub_state_handle = $dbhandle->prepare($sql_quer);
	$sub_state_handle->execute() or die $DBI::errstr;
}

# Create the people table
sub create_people_table{
	
	# Create the database table, where photo_key is the primary key and photo_file is the file name 
	my $sql_quer = qq/CREATE TABLE $params::peopleTableName (
	    $params::peopleKeyColumn  INTEGER PRIMARY KEY AUTOINCREMENT
	                            UNIQUE,
	    $params::personNameColumn STRING
	);/;

	#,$params::personPicasaID BIGINT

	my $sub_state_handle = $dbhandle->prepare($sql_quer);
	$sub_state_handle->execute() or die $DBI::errstr;
}

# Create the linkage table
sub create_linker_table{
	my $sql_quer = qq/CREATE TABLE $params::linkerTableName (
	    $params::linkerPhotoColumn  INTEGER REFERENCES $params::photoTableName ($params::photoKeyColumn),
	    $params::linkerPeopleColumn INTEGER REFERENCES $params::peopleTableName ($params::peopleKeyColumn) 
	);/;

	my $sub_state_handle = $dbhandle->prepare($sql_quer);
	$sub_state_handle->execute() or die $DBI::errstr;

}