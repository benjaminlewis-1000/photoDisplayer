#! /usr/bin/perl

# Code to make a huge database and then test read-write operations. 
use strict;
use warnings;

use params;
use DBI;
use DBD::mysql;
use List::Util qw[min max];
use threads;

use Time::HiRes qw( usleep gettimeofday tv_interval  );

use String::Random;
my $string_gen = String::Random->new;

my $create_new = 0;

our $j = 0;

our $numberOfNames = 2000;
our $numberOfPhotos = 2e5;

our $numPeopleReads = 1000;
our $numLinkerTests = 1000;

our $dbhandle;

print "\n***************************************************\n";

	our @photoList;
	our @nameList;
	our $t0;
	our $numLinks;
	our $elapsed;

if ($create_new){
	$params::database = 'test.db';
	`perl database_create.pl $params::database`;
	$dbhandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");


	###### Insert a bunch of names 

	$t0 = [gettimeofday];

	print "Inserting $numberOfNames names\n";
	for (my $i = 0; $i < $numberOfNames; $i++){
		my $name = $string_gen->randregex('[A-Za-z0-9]{8}');#:randpattern("a-z{5}");
		push @nameList, $name;
		my $insertIntoPhotoTable = qq/INSERT INTO $params::peopleTableName ( $params::personNameColumn) VALUES ("$name")/;
		# print $insertIntoPhotoTable . "\n ";

		$dbhandle->do($insertIntoPhotoTable) or die $DBI::errstr;
	}

	$elapsed = tv_interval ( $t0 );
	print  $elapsed / $numberOfNames . " seconds per name insertion with $numberOfNames insertions\n\n";


	###### Insert a bunch of photos

	print "Inserting $numberOfPhotos photos\n";
	$t0 = [gettimeofday];
	for (my $i = 0; $i < $numberOfPhotos; $i++){
		my $name = $string_gen->randregex('[A-Za-z0-9]{8}');#:randpattern("a-z{5}");
		push @photoList, $name;
		my $insertIntoPhotoTable = qq/INSERT INTO $params::photoTableName ( $params::photoFileColumn, $params::photoDateColumn) VALUES ("$name", "2")/;
		# print $insertIntoPhotoTable . "\n ";

		$dbhandle->do($insertIntoPhotoTable) or die $DBI::errstr;
	}
	$elapsed = tv_interval ( $t0 );
	print  $elapsed / $numberOfPhotos . " seconds per photo insertion with $numberOfPhotos insertions\n\n";

	####### Insert random links between the two tables.

	$t0 = [gettimeofday];
	$numLinks = $numberOfPhotos * 2;
	print "Inserting $numLinks links\n";
	for (my $i = 0; $i < $numLinks; $i++){

		my $randPhoto = int(rand($numberOfPhotos)) + 1;
		my $randPerson = int(rand($numberOfNames)) + 1;
		my $insertLinkInTable = qq/INSERT INTO $params::linkerTableName ($params::linkerPeopleColumn, $params::linkerPhotoColumn) VALUES ($randPerson, $randPhoto)/;
		$dbhandle->do($insertLinkInTable);

	}
	print "Done linking!\n";
	$elapsed = tv_interval ( $t0 );
	print  $elapsed / $numLinks . " seconds per link with $numLinks links\n\n";

}

else{
	$params::database = 'large_test_database.db';
	$dbhandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");

	# Get the list of names, then get the list of photos. 

	my $people_query = qq/SELECT $params::personNameColumn FROM $params::peopleTableName/;
	my $photos_query = qq/SELECT $params::photoFileColumn FROM $params::photoTableName/;

	my $people_sql = $dbhandle->prepare($people_query);
	$people_sql->execute() or die $DBI::errstr;
	my $photos_sql = $dbhandle->prepare($photos_query);
	$photos_sql->execute() or die $DBI::errstr;

	$numberOfNames = 0;
	while (my @row = $people_sql->fetchrow_array() ){
		$numberOfNames = $numberOfNames + 1;
		my $person_name = $row[0];
		push @nameList, $person_name;
	}

	$numberOfPhotos = 0;
	while (my @row = $photos_sql->fetchrow_array() ){
		$numberOfPhotos = $numberOfPhotos + 1;
		my $photo_name = $row[0];
		push @photoList, $photo_name;
	}

	my $numLinksQuery = qq/SELECT COUNT(*) FROM $params::linkerTableName/;
	my $link_sql = $dbhandle->prepare($numLinksQuery);
	$link_sql->execute() or die $DBI::errstr;

	my @val = $link_sql->fetchrow_array();
	$numLinks = $val[0];

}


###### Random access tests


print "Checking the names $numPeopleReads times\n";
$t0 = [gettimeofday];
for (my $i = 0; $i < $numPeopleReads; $i++){
 	my $num = int(rand($numberOfNames));
 	# print $num . "   " ;
	my $person = $nameList[$num];
	my $query = qq/SELECT * FROM $params::peopleTableName where $params::personNameColumn = "/ . $person . "\""; 
	# print $query . "\n";
	$dbhandle->do($query);
	# my $numPeopleWithName = eval { $query->fetchrow_arrayref->[0] };
	# print $numPeopleWithName . "\n";
}
$elapsed = tv_interval ( $t0 );
print  $elapsed / $numPeopleReads . " seconds per name read with $numPeopleReads reads given $numberOfPhotos photos and $numberOfNames names\n\n";

###### Linker table test - Pick a random picture, and then get the people that are in it. 


$t0 = [gettimeofday];

print "Checking links from photo to names $numLinkerTests times\n";
for (my $i = 0; $i < $numLinkerTests; $i++){
	my $photoNum = int(rand($numberOfPhotos));
	my $photo = $photoList[$photoNum];

	# Query: Look up the unique key corresponding to the photo and store it in $photoKey.
	my $linkQuery = qq/SELECT $params::photoKeyColumn FROM $params::photoTableName WHERE $params::photoFileColumn = "/ . $photo . "\"";
	my $query = $dbhandle->prepare($linkQuery);
	$query->execute() or die $DBI::errstr;

	my $photoKey = eval {$query->fetchrow_arrayref->[0] };

	if ($photoKey != $photoNum + 1){
		print $photoNum + 1 . "  " . $photoKey . "\n";
	}

	my $peopleInPhotoQuery = qq/SELECT $params::linkerPeopleColumn FROM $params::linkerTableName WHERE $params::linkerPhotoColumn = $photoKey/;
	# print $peopleInPhotoQuery . "  " ;
	$query = $dbhandle->prepare($peopleInPhotoQuery);
	$query->execute() or die $DBI::errstr;

	my $found = 0;

	while (my @row = $query->fetchrow_array() ){
		$found = $found + 1;
		# print join(',', @row) . " :: ";
		my $person_id = $row[0];
		my $personNameQuery = qq/SELECT $params::personNameColumn FROM $params::peopleTableName WHERE $params::peopleKeyColumn = $person_id/;
		my $subQuery = $dbhandle->prepare($personNameQuery);
		$subQuery->execute() or die $DBI::errstr;
		my @name = $subQuery->fetchrow_array();
		# print $name[0] . ", ";
	}
	print $found . " people found \n";
}
$elapsed = tv_interval ( $t0 );
print  $elapsed / $numLinkerTests . " seconds per link test with $numLinkerTests complex looks given $numberOfPhotos photos and $numberOfNames names\n\n";

#### Reverse link test - for each person, see which photos they're in.

$t0 = [gettimeofday];

my $count = 0;

print "Checking links from names to photos $numberOfNames times, one for each name.\n";
for (my $i = 0; $i < $numberOfNames; $i++){
	# my $nameNum = int(rand($numberOfNames));
	my $name = $nameList[$i];

	print "Checking name $name\n";
	# print $name . ";; \n";

	# Query: Look up the unique key corresponding to the photo and store it in $photoKey.
	my $linkQuery = qq/SELECT $params::peopleKeyColumn FROM $params::peopleTableName WHERE $params::personNameColumn = "/ . $name . "\"";
	my $query = $dbhandle->prepare($linkQuery);
	$query->execute() or die $DBI::errstr;

	my $personKey = eval {$query->fetchrow_arrayref->[0] };

	if ($personKey != $i + 1){
		print $i + 1 . "  " . $personKey . "\n";
	}

	my $photosWithPersonQuery = qq/SELECT $params::linkerPhotoColumn FROM $params::linkerTableName WHERE $params::linkerPeopleColumn = $personKey/;
	$query = $dbhandle->prepare($photosWithPersonQuery);
	$query->execute() or die $DBI::errstr;

	my $found = 0;

	while (my @row = $query->fetchrow_array() ){
		$found = $found + 1;
		# print join(',', @row) . " :: ";
		my $photo_id = $row[0];
		my $photoLocation = qq/SELECT $params::photoFileColumn FROM $params::photoTableName WHERE $params::photoKeyColumn = $photo_id/;
		my $subQuery = $dbhandle->prepare($photoLocation);
		$subQuery->execute() or die $DBI::errstr;
		my @photos = $subQuery->fetchrow_array();
		# print $photos[0] . ", ";
	}
	print $found . " photos found \n";
	$count += $found;
}
$elapsed = tv_interval ( $t0 );
print  $elapsed / $numLinkerTests . " seconds per link test with $numLinkerTests complex looks given $numberOfPhotos photos and $numberOfNames names\n";

print "There were $count photos linked to the names. For comparison, there were $numLinks links.\n\n***************************************************\n\n";

=cut