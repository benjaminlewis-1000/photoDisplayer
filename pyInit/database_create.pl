#! /usr/bin/perl

# cpan DBD::mysql

use warnings;
use strict;
use FindBin;
use lib $FindBin::Bin;

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
create_metadata_table();
create_comments_table();

update_metadata();

# Vacuum the database
$dbhandle->do('VACUUM');
$dbhandle->disconnect;

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

	my $dropMetadata = qq/DROP TABLE IF EXISTS $params::metadataTableName/;
	$query = $dbhandle->prepare($dropMetadata);
	$query->execute() or die $DBI::errstr;

	my $dropCommentLinker = qq/DROP TABLE IF EXISTS $params::commentLinkerUserTableName/;
	$query = $dbhandle->prepare($dropCommentLinker);
	$query->execute() or die $DBI::errstr;

	$dropCommentLinker = qq/DROP TABLE IF EXISTS $params::commentLinkerGoogleTableName/;
	$query = $dbhandle->prepare($dropCommentLinker);
	$query->execute() or die $DBI::errstr;

	$dropCommentLinker = qq/DROP TABLE IF EXISTS $params::commentLinkerClarifaiTableName/;
	$query = $dbhandle->prepare($dropCommentLinker);
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

	    $params::photoYearColumn STRING,
	    $params::photoMonthColumn STRING,
	    $params::photoDayColumn STRING,
	    $params::photoHourColumn STRING,
	    $params::photoMinuteColumn STRING,
	    $params::photoGMTColumn STRING,

	    $params::modifyDateColumn STRING,
	    $params::insertDateColumn STRING,
	    $params::rootDirNumColumn STRING,

	    $params::houseNumColumn STRING,
	    $params::streetColumn STRING,
	    $params::cityColumn STRING,
	    $params::stateColumn STRING,
	    $params::postcodeCoulumn STRING,
	    $params::countryColumn STRING,
	    $params::latColumn STRING,
	    $params::longColumn STRING
	); /;

	# Prepare and execute the statement
	my $sub_state_handle = $dbhandle->prepare($sql_quer);
	$sub_state_handle->execute() or die $DBI::errstr;
}

sub create_comments_table{
	my $sql_quer = qq/CREATE TABLE $params::commentLinkerUserTableName (
	    $params::commentLinkerPhotoColumn INTEGER REFERENCES $params::photoTableName ($params::photoKeyColumn),
	    $params::commentLinkerTagColumn STRING,
	    $params::commentLinkerTagProbabilityColumn DOUBLE
	); /;
	
	my $sub_state_handle = $dbhandle->prepare($sql_quer);
	$sub_state_handle->execute() or die $DBI::errstr;


	$sql_quer = qq/CREATE TABLE $params::commentLinkerGoogleTableName (
	    $params::commentLinkerPhotoColumn INTEGER REFERENCES $params::photoTableName ($params::photoKeyColumn),
	    $params::commentLinkerTagColumn STRING,
	    $params::commentLinkerTagProbabilityColumn DOUBLE
	); /;
	
	$sub_state_handle = $dbhandle->prepare($sql_quer);
	$sub_state_handle->execute() or die $DBI::errstr;


	$sql_quer = qq/CREATE TABLE $params::commentLinkerClarifaiTableName (
	    $params::commentLinkerPhotoColumn INTEGER REFERENCES $params::photoTableName ($params::photoKeyColumn),
	    $params::commentLinkerTagColumn STRING,
	    $params::commentLinkerTagProbabilityColumn DOUBLE
	); /;
	
	$sub_state_handle = $dbhandle->prepare($sql_quer);
	$sub_state_handle->execute() or die $DBI::errstr;
}

sub create_root_dir_table{
	my $sql_quer = qq/CREATE TABLE $params::rootTableName (
		$params::rootKeyColumn INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
		$params::windowsRootPath STRING,
		$params::linuxRootPath STRING
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

	my $ben_query = qq/INSERT INTO $params::peopleTableName ($params::personNameColumn) VALUES ("Benjamin Lewis");/;
	my $jessica_query = qq/INSERT INTO $params::peopleTableName ($params::personNameColumn) VALUES ("Jessica Lewis");/;

	$sub_state_handle = $dbhandle->prepare($ben_query);
	$sub_state_handle->execute() or die $DBI::errstr;

	$sub_state_handle = $dbhandle->prepare($jessica_query);
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

sub create_metadata_table{
	my $sql_quer = qq/CREATE TABLE $params::metadataTableName (
		$params::metadataNameColumn  STRING,  
		$params::metadataValueColumn STRING
	);/;

	my $metadata_handle = $dbhandle->prepare($sql_quer);
	$metadata_handle->execute() or die $DBI::errstr;

}

sub update_metadata{

	my ($sec,$min,$hour,$mday,$mon,$year) = localtime(time);
	$year += 1900;
	$mon += 1;

	my $dateTime = sprintf("%04d-%02d-%02d %02d:%02d:%02d", $year, $mon, $mday, $hour, $min, $sec);

	my $updatedValQuery = qq/INSERT INTO $params::metadataTableName VALUES ("$params::metadataLastEditedField", "$dateTime")/;
	
	my $metadata_handle = $dbhandle->prepare($updatedValQuery);
	$metadata_handle->execute() or die $DBI::errstr;

}
