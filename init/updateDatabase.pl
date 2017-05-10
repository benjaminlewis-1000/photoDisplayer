#! /usr/bin/perl

# Update database - A file that gets all the root directories in the database,
# then reads through them and checks that all photos under that root directory
# have been read into the database and that they are up to date. 
# In particular, the photos are checked for modifications since the last
# insertion date (which is handled in readInImages.pl). 

use params;
use DBI;
use Tk;
use Proc::Background;

use warnings;
use strict; 

require 'read_xmp.pl';
require 'readInImages.pl';
require 'filesFromBaseFinder.pl';
if (! -e 'trimDeletedFiles.pl'){
	die "Can't locate file 'trimDeletedFiles.pl'. Exiting.";
}

our @rootDirList;

our $portNum = $params::geoServerPort;
my $geoserverProc = Proc::Background->new("python geoServer.py $portNum");
$geoserverProc->alive;

# Open the database
our $dbhandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");

# Query the database for a list of all root directories in the database. 
my $rootDirQuery = qq/SELECT $params::rootKeyColumn, $params::windowsRootPath, $params::linuxRootPath FROM $params::rootTableName/;
my $query = $dbhandle->prepare($rootDirQuery);
until(
	$query->execute()
){
	warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
	warn "Failed on the following query: $rootDirQuery\n";
	sleep(5);
}# or die $DBI::errstr;

# Bind the results of the query.
our ($rootKey, $winRootDir, $linRootDir);
$query->bind_col(1, \$rootKey);
$query->bind_col(2, \$winRootDir);
$query->bind_col(3, \$linRootDir);

# For each root directory, get the unique subdirectories and call the add file method,
# which will take care of adding or updating the images as necessary. Congrats, you're done!
our $numPassed = 0;
my @rootDirMultiArray;
while ($query->fetch){

	our $root_dir = checkOSFolder({
			linRootDir => $linRootDir,
			winRootDir => $winRootDir,
			dbhandle => $dbhandle,
			rootKey => $rootKey
		});

	# Sorry, this is SUPER hacky; I just want to be able to update all root directories 
	# at once, then go on to process, so you don't have to wait a super long time.
	my @localArray = ($linRootDir, $winRootDir, $rootKey, $root_dir);
	push @rootDirMultiArray, \@localArray;
}

for (my $i = 0; $i < scalar @rootDirMultiArray; $i++ ){
	my @localArray = @{$rootDirMultiArray[$i]};
	my $linRootDir = $localArray[0];
	my $winRootDir = $localArray[1];
	my $rootKey    = $localArray[2];
	my $root_dir = $localArray[3];

	print "Root dir, ud.pl: " . $root_dir . "\n";

	# print $rootKey . "  " . $root_dir . "\n";
	my @unq_subdirs = getUniqueSubdirs($root_dir);
	# my @unq_subdirs;
	# push @unq_subdirs, "Summer 2014 ABQ/Keep";

	print "Got a list of unique subdirectories." . "\n";
	print join (", ", @unq_subdirs) . "\n";

	open OUTPUT,  ">unhandled_files.txt" or die $!;
	addFilesInListOfSubdirs(\@unq_subdirs, $rootKey, $root_dir, \$numPassed, $portNum, \$dbhandle);
	close OUTPUT;
}

$geoserverProc->die;

require 'trimDeletedFiles.pl'; # Automatically runs the trim.