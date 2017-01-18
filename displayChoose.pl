#! /usr/bin/perl

# Choose the data

use params;
use DBI;
use Data::Dumper;

use accessQueries;

use Tk;

use warnings;
use strict;

	our $dbhandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");

	# Get a list of the people 

	my $peopleQuery = qq/SELECT * FROM $params::peopleTableName/;
	my $query = $dbhandle->prepare($peopleQuery);
	until(
		$query->execute()
	){
		warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
		warn "Failed on the following query: $peopleQuery\n";
		sleep(5);
	}# or die $DBI::errstr;

	my %peopleHash;
	handleQuery();

	# while (my @row = $query->fetchrow_array){
	# 	print join( ",", @row) . "\n";
	# 	$peopleHash{$row[1]} = $row[0];
	# }

	# print Dumper(%peopleHash);

sub handleQuery{

##### Get the root directory hash map
	my %rootHash;
	my $rootHashQuery = qq/SELECT $params::rootKeyColumn, $params::rootDirPath FROM $params::rootTableName/;
	my $query = $dbhandle->prepare($rootHashQuery);
	until(
		$query->execute()
	){
		warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
		warn "Failed on the following query: $rootHashQuery\n";
		sleep(5);
	}# or die $DBI::errstr;

	my ($rootDirNum, $rootDirName); 
	# Note columns start at 1 (not 0).
	$query->bind_col(1, \$rootDirNum);
	$query->bind_col(2, \$rootDirName);

	while($query->fetch){
		$rootHash{$rootDirNum} = $rootDirName;
	}
	
##### Get all photo_keys from the photo database where the query is satisfied
	my $getPhotosQuery = $accessQueries::accessQueriesList[0];
	$query = $dbhandle->prepare("$getPhotosQuery");
	until(
		$query->execute()
	){
		warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
		warn "Failed on the following query: $getPhotosQuery\n";
		sleep(5);
	}# or die $DBI::errstr;

	my @photoNums; 

	my $col1;
	$query->bind_col(1, \$col1);

	while ($query->fetch){
		push(@photoNums, $col1);
	}

	print scalar @photoNums  . "\n";

##### With the list of photo keys that satisfy the criteria, select the photo file column and the root directory number for each of those photos. 
	my $fileNamesQuery = qq/SELECT $params::photoFileColumn, $params::rootDirNumColumn FROM  $params::photoTableName where $params::photoKeyColumn in (/ . join(", ", @photoNums) . ")";
	$query = $dbhandle->prepare($fileNamesQuery);
	until(
		$query->execute()
	){
		warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
		warn "Failed on the following query: $fileNamesQuery\n";
		sleep(5);
	}# or die $DBI::errstr;

	my ($photoFileName, $foundRootDirNum);
	$query->bind_col(1, \$photoFileName);
	$query->bind_col(2, \$foundRootDirNum);

##### Print the output.
	while (my @row = $query->fetchrow_array){
		print $rootHash{$foundRootDirNum} . $photoFileName . "\n";
	}


}

