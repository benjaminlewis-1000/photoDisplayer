#! /usr/bin/perl

# Code to make a huge database and then test read-write operations. 
use strict;
use warnings;

use params;
use DBI;

use String::Random;
my $string_gen = String::Random->new;

our $j = 0;
our $dbhandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");

for (my $i = 0; $i < 1e2; $i++){
	my $name = $string_gen->randregex('[A-Za-z0-9]{8}');#:randpattern("a-z{5}");
	my $insertIntoPhotoTable = qq/INSERT INTO $params::photoTableName ( $params::photoFileColumn, $params::photoDateColumn) VALUES ("$name", "2")/;
	print $insertIntoPhotoTable . "\n ";

	$dbhandle->do($insertIntoPhotoTable) or die $DBI::errstr;
}
