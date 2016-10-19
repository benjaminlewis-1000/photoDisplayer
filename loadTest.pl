#! /usr/bin/perl

# Code to make a huge database and then test read-write operations. 
use strict;
use warnings;

use params;
use DBI;
use DBD::mysql;
use List::Util qw[min max];

use Time::HiRes qw( usleep gettimeofday tv_interval  );

use String::Random;
my $string_gen = String::Random->new;

$params::database = 'test.db';

our $j = 0;
our $dbhandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");

`perl database_create.pl $params::database`;


our $numberOfNames = 10;
our $numberOfPhotos = 10;

our $numPeopleReads = 100;
our $numLinkerTests = 10;

###### Insert a bunch of names 

our @nameList;
my $t0 = [gettimeofday];

for (my $i = 0; $i < $numberOfNames; $i++){
	my $name = $string_gen->randregex('[A-Za-z0-9]{8}');#:randpattern("a-z{5}");
	push @nameList, $name;
	my $insertIntoPhotoTable = qq/INSERT INTO $params::peopleTableName ( $params::personNameColumn) VALUES ("$name")/;
	# print $insertIntoPhotoTable . "\n ";

	$dbhandle->do($insertIntoPhotoTable) or die $DBI::errstr;
}

my $elapsed = tv_interval ( $t0 );
print  $elapsed / $numberOfNames . " seconds per name insertion with $numberOfNames insertions\n";

###### Insert a bunch of photos

our @photoList;
$t0 = [gettimeofday];
for (my $i = 0; $i < $numberOfPhotos; $i++){
	my $name = $string_gen->randregex('[A-Za-z0-9]{8}');#:randpattern("a-z{5}");
	push @photoList, $name;
	my $insertIntoPhotoTable = qq/INSERT INTO $params::photoTableName ( $params::photoFileColumn, $params::photoDateColumn) VALUES ("$name", "2")/;
	# print $insertIntoPhotoTable . "\n ";

	$dbhandle->do($insertIntoPhotoTable) or die $DBI::errstr;
}
$elapsed = tv_interval ( $t0 );
print  $elapsed / $numberOfPhotos . " seconds per photo insertion with $numberOfPhotos insertions\n";

####### Insert random links between the two tables.

our $numLinks = max($numberOfPhotos, $numberOfNames) * 4;
for (my $i = 0; $i < $numLinks; $i++){

	my $randPhoto = int(rand($numberOfPhotos)) + 1;
	my $randPerson = int(rand($numberOfNames)) + 1;
	my $insertLinkInTable = qq/INSERT INTO $params::linkerTableName ($params::linkerPeopleColumn, $params::linkerPhotoColumn) VALUES ($randPhoto, $randPerson)/;
	$dbhandle->do($insertLinkInTable);

}

###### Random access tests


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
print  $elapsed / $numPeopleReads . " seconds per name read with $numPeopleReads reads given $numberOfPhotos photos and $numberOfNames names\n";

###### Linker table test - Pick a random picture, and then get the people that are in it. 


$t0 = [gettimeofday];
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
	print $peopleInPhotoQuery . "  " ;
	$query = $dbhandle->prepare($peopleInPhotoQuery);
	$query->execute() or die $DBI::errstr;

	my $found = 0;
	print "|| ";
	while (my @row = $query->fetchrow_array() ){
		$found = $found + 1;
		print join(',', @row) . " :: ";

	}
	print $found . " people found \n";
}
$elapsed = tv_interval ( $t0 );
print  $elapsed / $numLinkerTests . " seconds per link test with $numLinkerTests complex looks given $numberOfPhotos photos and $numberOfNames names\n";