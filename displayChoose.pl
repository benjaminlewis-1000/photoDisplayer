#! /usr/bin/perl

# Choose the data

use params;
use DBI;
use Data::Dumper;

use Tk;

use warnings;
use strict;

	our $dbhandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");

	# Get a list of the people 

	my $peopleQuery = qq/SELECT * FROM $params::peopleTableName/;
	my $query = $dbhandle->prepare($peopleQuery);
	$query->execute() or die $DBI::errstr;

	my %peopleHash;

	while (my @row = $query->fetchrow_array){
		print join( ",", @row) . "\n";
		$peopleHash{$row[1]} = $row[0];
	}

	print Dumper(%peopleHash);