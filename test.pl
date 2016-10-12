#! /usr/bin/perl

use strict;
use warnings;

use DBI;
use Config::INI::Reader;

use params;

require 'read_xmp.pl';

my $file = 'D:\Pictures\Family Pictures\2011\2011 (7) July\DSC_0036.JPG';

# my @ls = glob("'.pl || .txt' *");
# print join(', ', @ls) . "\n";

my %data = getImageData({
	filename => $file,
	resX => 0,
	resY => 0
	});

if (!$data{'Status'} ){
	print "$!\n";
	exit;
}

# foreach my $k (keys %data){
# 	print $k . ", ";
# }
# print "\n";

# print "Year" . " : " . $data{'Year'} . "\n";
# print "Size" . " : " . $data{'ImageSize'} . "\n";
# print "Width" . " : " . $data{'Width'} . "\n";
# print "Height" . " : " . $data{'Height'} . "\n";
# print "Year" . " : " . $data{'Year'} . "\n";
# print "Month" . " : " . $data{'Month'} . "\n";
# print "Day" . " : " . $data{'Day'} . "\n";
# print "Hour" . " : " . $data{'Hour'} . "\n";
# print "Min" . " : " . $data{'Minute'} . "\n";
# print "Sec" . " : " . $data{'Second'} . "\n";
# print "Status" . " : " . $data{'Status'} . "\n";
# print "Modify date" . " : " . $data{'ModifyDate'} . "\n";
# print join(";", @{$data{'NameList'}}) . "\n";

# With the file: 

our %peopleToKeyHash;

our $dbhandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");

# Insert the data about the photo (date and filename) into the appropriate table. 
	my $insertIntoPhotoTable = qq/INSERT INTO $params::photoTableName ( $params::photoFileColumn, $params::photoDateColumn)  VALUES ("$file", "$data{'TakenDate'}")/;
	print $insertIntoPhotoTable . "\n ";

	$dbhandle->do($insertIntoPhotoTable) or die $DBI::errstr;

# Get the value of the autoincremented value for the table; this value is in $photoKeyVal
	my $keyNumQuery = qq/SELECT last_insert_rowid()/;
	my $query = $dbhandle->prepare($keyNumQuery);
	$query->execute() or die $DBI::errstr;
	my $photoKeyVal = @{$query->fetch()}[0];
	print $photoKeyVal . "\n";

# Now we need to tackle inserting names into the database. I want to have a hash with the names and check it. If the name
# has already been encountered, we should read its public key from the hash. Else, we need to add it to the hash, add
# it to the people database, and save the public key for future use. 

foreach (@{$data{'NameList'}}){
	our $peopleKeyVal = -1;
	print $_ . " : " ;
	if (exists($peopleToKeyHash{$_})){
		print "$_ exists\n";
		$peopleKeyVal = $peopleToKeyHash{$_};
	}
	else{

		# Check if person exists in the database if they're not in the hash, for partial building purposes. 

		# SQL Query : Ask for the unique key for the person from the database, and store it in $peopleKeyVal if the peron exists. 
		# If they do, then get their unique key and add it to the hash so that we don't have to find it ever again. 
		my $personExistsQuery = qq/SELECT $params::peopleKeyColumn FROM $params::peopleTableName WHERE $params::personNameColumn = "$_"/;

		my $query = $dbhandle->prepare($personExistsQuery);
		$query->execute() or die $DBI::errstr;
		my $result = eval { $query->fetchrow_arrayref->[0] };

		# Find the number of people in the database with that name; should be only one. 
		# TODO: Work out how to distinguish people. 
		my $numQuery = qq/SELECT COUNT(*) FROM $params::peopleTableName WHERE $params::personNameColumn = "$_"/;
		$query = $dbhandle->prepare($numQuery);
		$query->execute() or die $DBI::errstr;
		my $numPeopleWithName = eval { $query->fetchrow_arrayref->[0] };
		print $numPeopleWithName . "\n";

		if($result and $numPeopleWithName == 1){
			$peopleKeyVal = $result;
			$peopleToKeyHash{$_} = $result;
		}

		# If we well and truly can't find the person in the database, insert their name in the database with a unique identifier and 
		# add the identifier to the hash. 
		else {

			if ($numPeopleWithName > 1){
				die("Error! Getting more than one person with this name: $_.");
			}

			my $insertPersonInPersonTable = qq/INSERT INTO $params::peopleTableName ($params::personNameColumn) VALUES ("$_")/;

			$dbhandle->do($insertPersonInPersonTable) or die $DBI::errstr;

			my $keyNumQuery = qq/SELECT last_insert_rowid()/;
			my $query = $dbhandle->prepare($keyNumQuery);
			$query->execute() or die $DBI::errstr;
			$peopleKeyVal = @{$query->fetch()}[0];
			$peopleToKeyHash{$_} = $peopleKeyVal;
		}
	}

	# Add to linker table: 

	my $insertLinkInTable = qq/INSERT INTO $params::linkerTableName ($params::linkerPeopleColumn, $params::linkerPhotoColumn) VALUES ($peopleKeyVal, $photoKeyVal)/;
	$dbhandle->do($insertLinkInTable);

}

exit();