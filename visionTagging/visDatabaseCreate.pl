#! /usr/bin/perl

# cpan DBD::mysql

use warnings;
use strict;

use DBI;

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


dbConnect();
dropTables();
create_table();

$dbhandle->disconnect;

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
sub create_table{
	# Create the database table, where photo_key is the primary key and photo_file is the file name 
	my $sql_quer = qq/CREATE TABLE visionData (
		    fileName        STRING,
		    lastCheckedDate STRING
		); /;

	# Prepare and execute the statement
	my $create_handle = $dbhandle->prepare($sql_quer);
	$create_handle->execute() or die $DBI::errstr;
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