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
	print $photoKeyVal;



# $dbhandle->do('INSERT INTO $params::photoTableName ($params::photoKeyColumn, $params::photoFileColumn, $params::photoDateColumn) VALUES (?, ?, ?)',
#   undef,
#   1, $file, $data{'ModifyDate'});

exit();