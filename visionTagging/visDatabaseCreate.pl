#! /usr/bin/perl

# cpan DBD::mysql

use warnings;
use strict;

use DBI;
use Time::localtime;

use YAML::XS 'LoadFile';

our $base_path = cwd();  # Get the directory of this module. 
$base_path =~ m/(.*)\/.*$/;  # Regex to go up one directory.
$base_path = $1 . "/";  # Capture the output and put it in $base_path.

our $YAML_file = $base_path . "config/params.yaml";
our $config = LoadFile($YAML_file);  # YAML is more cross-language.


#TODO: Delete the old database file
#TODO: Database file location better handled
our $dbhandle;
our $dbName = 'visionDatabase.db';

my $count_args = @ARGV ;

if ($count_args == 1) {
	my $db = $ARGV[0];
	if ($db =~ /db$/){
		print "valid";
		$dbName = $db;
	}
}


# dbConnect();
# dropTables();
# createLoggingTable();
# createMetadataTable();
populateMetadataTable();

# $dbhandle->disconnect;

# End creation of tables.

sub dbConnect{
	$dbhandle = DBI->connect("dbi:SQLite:$dbName", "user" , "pass");
}

sub dropTables{
	# Clean out the old tables so we can create them afresh.
	my $dropPhotos = qq/DROP TABLE IF EXISTS visionData/;
	my $query = $dbhandle->prepare($dropPhotos);
	$query->execute() or die $DBI::errstr;
	
}

###############################################
########### subs for table creation ###########
###############################################

# Create the photo primary key and filename table
sub createLoggingTable{
	# Create the database table, where photo_key is the primary key and photo_file is the file name 
	my $sql_quer = qq/CREATE TABLE visionData (
		    fileName        STRING,
		    lastCheckedDate STRING,
		    readAsPortrait BOOL,
		    machineVisionSource STRING
		); /;

	# Prepare and execute the statement
	my $create_handle = $dbhandle->prepare($sql_quer);
	$create_handle->execute() or die $DBI::errstr;
}

sub createMetadataTable{
	my $sql_quer = qq/CREATE TABLE Variables(
		Name   STRING,
		Value  STRING
	); /;

	my $create_handle = $dbhandle->prepare($sql_quer);
	$create_handle->execute() or die $DBI::errstr;
}

sub populateMetadataTable{
	my $tm = localtime;
	my $year = $tm->year + 1900;
	my $month = $tm->mon + 1;
	my $day = $tm->mday;
	print $day . " " . $month . " " . $year . "\n";
}

# sub update_metadata{

# 	my ($sec,$min,$hour,$mday,$mon,$year) = localtime(time);
# 	$year += 1900;
# 	$mon += 1;

# 	my $dateTime = sprintf("%04d-%02d-%02d %02d:%02d:%02d", $year, $mon, $mday, $hour, $min, $sec);

# 	my $updatedValQuery = qq/INSERT INTO $params::metadataTableName VALUES ("$params::metadataLastEditedField", "$dateTime")/;
	
# 	my $metadata_handle = $dbhandle->prepare($updatedValQuery);
# 	$metadata_handle->execute() or die $DBI::errstr;

# }