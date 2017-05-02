#! /usr/bin/perl

# cpan DBD::mysql

use warnings;
use strict;

use Cwd;
use DBI;
use Time::localtime;

# use YAML::XS 'LoadFile';
use XML::Simple qw(:strict);

our $base_path = cwd();  # Get the directory of this module. 
$base_path =~ m/(.*)\/.*$/;  # Regex to go up one directory.
$base_path = $1 . "/";  # Capture the output and put it in $base_path.

our $config_file = $base_path . "config/params.xml";
# our $config = LoadFile($YAML_file);  # YAML is more cross-language.


our $config = XMLin( $config_file, ForceArray => 1, KeyAttr=>[]) or die("Sorry! Can't read this XML.");

#TODO: Delete the old database file
#TODO: Database file location better handled

my $visionBase = $config->{'visionTaggingParams'}->[0];

our $dbhandle;
our $dbName = $visionBase->{'database'}->[0]->{'fileName'}->[0];

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
createLoggingTable();
createMetadataTable();
populateMetadataTable();

$dbhandle->disconnect;

# End creation of tables.

sub dbConnect{
	$dbhandle = DBI->connect("dbi:SQLite:$dbName", "user" , "pass");
}

sub dropTables{
	# Clean out the old tables so we can create them afresh.
	my $tableBase = $visionBase->{'database'}->[0]->{'tables'}->[0];
	my $dropPhotos = qq/DROP TABLE IF EXISTS $tableBase->{'recordDataTable'}->[0]->{'Name'}->[0] /;
	my $query = $dbhandle->prepare($dropPhotos);
	$query->execute() or die $DBI::errstr;


	my $dropMetadata = qq/DROP TABLE IF EXISTS $tableBase->{'visionMetaTable'}->[0]->{'Name'}->[0] /;
	$query = $dbhandle->prepare($dropMetadata);
	$query->execute() or die $DBI::errstr;
	
}

###############################################
########### subs for table creation ###########
###############################################

# Create the photo primary key and filename table
sub createLoggingTable{
	# Create the database table, where photo_key is the primary key and photo_file is the file name 
	my $recordBase = $visionBase->{'database'}->[0]->{'tables'}->[0]->{'recordDataTable'}->[0];
	my $sql_quer = qq/CREATE TABLE $recordBase->{'Name'}->[0] (
		    $recordBase->{'Columns'}->[0]->{'File'}->[0] 			STRING,
		    $recordBase->{'Columns'}->[0]->{'Checked'}->[0] 		STRING,
		    $recordBase->{'Columns'}->[0]->{'Portrait'}->[0] 		BOOL,
		    $recordBase->{'Columns'}->[0]->{'Source'}->[0] 			STRING,
		    $recordBase->{'Columns'}->[0]->{'Valid'}->[0]			BOOL
		); /;

	# Prepare and execute the statement
	my $create_handle = $dbhandle->prepare($sql_quer);
	$create_handle->execute() or die $DBI::errstr;
}

sub createMetadataTable{
	my $metaBase = $visionBase->{'database'}->[0]->{'tables'}->[0]->{'visionMetaTable'}->[0];
	my $sql_quer = qq/CREATE TABLE $metaBase->{'Name'}->[0](
		$metaBase->{'Columns'}->[0]->{'NameColumn'}->[0]  STRING,
		$metaBase->{'Columns'}->[0]->{'ValueColumn'}->[0]  STRING
	); /;

	my $create_handle = $dbhandle->prepare($sql_quer);
	$create_handle->execute() or die $DBI::errstr;
}

sub populateMetadataTable{
	my $tm = localtime;
	my $year = $tm->year + 1900;
	my $month = sprintf("%02d", $tm->mon + 1);
	my $day = sprintf("%02d", $tm->mday);
	my $newMonth = "$year-$month-$day";

	my $googFieldsBase = $visionBase->{'database'}->[0]->{'Fields'}->[0]->{'googFields'}->[0];
	my $clarifaiFieldsBase = $visionBase->{'database'}->[0]->{'Fields'}->[0]->{'googFields'}->[0];
	my $metaBase = $visionBase->{'database'}->[0]->{'tables'}->[0]->{'visionMetaTable'}->[0];

	my $populateQuery = qq/INSERT INTO $metaBase->{'Name'}->[0] 
		('$metaBase->{'Columns'}->[0]->{'NameColumn'}->[0]', '$metaBase->{'Columns'}->[0]->{'ValueColumn'}->[0]') VALUES
		('$clarifaiFieldsBase->{'ReadsThisMonth'}->[0]', '0'), 
		('$clarifaiFieldsBase->{'ReadsPerMonth'}->[0]', '5000'),
		('$clarifaiFieldsBase->{'NewMonthDate'}->[0]', '$newMonth'),
		('$clarifaiFieldsBase->{'DayLastRead'}->[0]', '$newMonth'),
		('$clarifaiFieldsBase->{'DayOfNewMonth'}->[0]', '$day'),
		('$googFieldsBase->{'ReadsThisMonth'}->[0]', '0'), 
		('$googFieldsBase->{'ReadsPerMonth'}->[0]', '1000'),
		('$googFieldsBase->{'NewMonthDate'}->[0]', '$newMonth'),
		('$googFieldsBase->{'DayLastRead'}->[0]', '$newMonth'),
		('$googFieldsBase->{'DayOfNewMonth'}->[0]', '$day'); 
		/;

	my $create_handle = $dbhandle->prepare($populateQuery);
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