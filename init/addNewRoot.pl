#! /usr/bin/perl

# Simple function: it takes a root directory, $root_dir, and queries the database to see if a database has been modified at a higher level. If no higher level has been inserted and we have not inserted this directory before, then the new root_dir is inserted in the $params::rootTableName. From there, we can list all the directories that are directly off this one and that are not covered by existing root directories. 

use params;
use DBI;
use Tk;
use File::Find;
use File::HomeDir;
use Data::Dumper;
use Proc::Background;

use warnings;
use strict; 

require 'read_xmp.pl';
require 'readInImages.pl';
require 'filesFromBaseFinder.pl';

my $homedir = File::HomeDir->my_home;
print $homedir . "\n";

my $mw = MainWindow->new;
$mw->withdraw;  # Hide the main window.

our @rootDirList;

# my $root_dir = 'D:\Pictures\2016';
# my $root_dir = 'C:\Users\Benjamin\Dropbox\Perl Code\photoDisplayer\base\\';

our $answerBool = 1;

our $portNum = 8000;
my $geoserverProc = Proc::Background->new("python geoServer.py");
$geoserverProc->alive;

if (!$answerBool){
	my $root_dir2 = 'C:\Users\Benjamin\Dropbox\Perl Code\photoDisplayer\base';
	$root_dir2 =~ s/\\$//g;
	$root_dir2 =~ s/\/$//g;

	# Add a backslash to the end and replace back/forward slashes as necessary. 
	$root_dir2 = $root_dir2 . '/';
	$root_dir2 =~ s/\\/\//g;
	print $root_dir2 . "\n";
	push(@rootDirList, $root_dir2);
}

while ($answerBool) {
	my $root_dir = $mw->chooseDirectory(-title=>'Hey there! Please choose the highest level root directory from which you wish to choose picture files.', -initialdir=>$homedir);
	if (defined $root_dir and $root_dir ne "/" and $root_dir ne ""){
		# Remove any extraneous end-of-string slashes.
		$root_dir =~ s/\\$//g;
		$root_dir =~ s/\/$//g;

		# Add a backslash to the end and replace back/forward slashes as necessary. 
		$root_dir = $root_dir . '/';
		$root_dir =~ s/\\/\//g;
		push (@rootDirList, $root_dir);
		print $root_dir . "\n";
	}else{
		last;
	}
	my $answer = $mw->messageBox(-title => 'Please Reply', 
	     -message => 'Would you like to add more root directories?', 
	     -type => 'YesNo', -icon => 'question', -default => 'yes');

	$answerBool = (lc($answer) eq 'yes') ? 1 : 0;
	# print $answerBool . "\n";
	# body...
}

if (scalar @rootDirList == 0){
	die "No directories were chosen to add; exiting.\n";
}

$mw->messageBox(-title => 'Warning', -message => 'Please be patient. Adding all pictures in these directories could take a while.', -type=>'OK');

# Open the database
our $dbhandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");

foreach my $root_dir (@rootDirList){

##############

	#  Check if a higher-up directory is already in the table. If so, we don't need to add this in. 
	my $existingRootDirsQuery = qq/SELECT $params::rootDirPath FROM $params::rootTableName/;
	my $query = $dbhandle->prepare($existingRootDirsQuery);
	until(
		$query->execute()
	){
		warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
		warn "Failed on the following query: $existingRootDirsQuery\n";
		sleep(5);
	}# or die $DBI::errstr;

	my $higherDirectoryExists = 0;

	my $directoryKeyVal;
	
	while (my @row = $query->fetchrow_array) { # retrieve one row
	    my $registeredRow = join("", @row);
	    if ( $root_dir =~ $registeredRow ){
	    	print "I've put $root_dir in already at a higher level, at: $registeredRow. Exiting.\n";
	    	$higherDirectoryExists = 1;

	    	my $dirExistsQuery = qq/SELECT $params::rootKeyColumn FROM $params::rootTableName WHERE $params::rootDirPath = "$registeredRow"/;
			my $query = $dbhandle->prepare($dirExistsQuery);
			# print $dirExistsQuery . "\n";
			until(
				$query->execute()
			){
				warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
				warn "Failed on the following query: $dirExistsQuery\n";
				sleep(5);
			}# or die $DBI::errstr;
			$directoryKeyVal = eval { $query->fetchrow_arrayref->[0] };
			if ( ! ( $params::debug and $params::debugNewRoot )){
				exit();
			}
	    }
	}

##############
# Check if the root directory is already in the table. If so, get its number.
# If not, insert into the table. 
	if (!$higherDirectoryExists){
		my $rootDirExistsQuery = qq/SELECT $params::rootKeyColumn FROM $params::rootTableName WHERE $params::rootDirPath = "$root_dir"/;
		my $query = $dbhandle->prepare($rootDirExistsQuery);
		until(
			$query->execute()
		){
			warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
			warn "Failed on the following query: $rootDirExistsQuery\n";
			sleep(5);
		}# or die $DBI::errstr;
		$directoryKeyVal = eval { $query->fetchrow_arrayref->[0] };

		if (!defined $directoryKeyVal or $directoryKeyVal eq "" ){
			# If the directory doesn't exist, we then have to add it to the root directory table and get its unique key value (for use in adding all the pictures).
			my $insertDirectory = qq/INSERT INTO $params::rootTableName ( $params::rootDirPath)  VALUES ("$root_dir")/;
			$dbhandle->do($insertDirectory) or die $DBI::errstr;

			# Get the value of the autoincremented value for the table; this value is in $directoryKeyVal
			my $keyNumQuery = qq/SELECT last_insert_rowid()/;
			my $query = $dbhandle->prepare($keyNumQuery);
			until(
				$query->execute()
			){
				warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
				warn "Failed on the following query: $keyNumQuery\n";
				sleep(5);
			}# or die $DBI::errstr;

			$directoryKeyVal = @{$query->fetch()}[0];
			print "Key val is " . $directoryKeyVal . "\n";
		}else{
			# We have the directory already. Its directory key value is in $result.
			print "We have that directory.\n";
			exit();
		}
	}

	print "We have inserted a new root directory, $root_dir. Its key value is $directoryKeyVal.\n";
}

foreach my $root_dir (@rootDirList){

	#####
		my @subdirectories = getUniqueSubdirs($root_dir);
	##### 

	# Query the database for the key value for the current root directory

 # $dbhandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");
	my $rootDirKeyValQuery = qq/SELECT $params::rootKeyColumn FROM $params::rootTableName WHERE $params::rootDirPath = "$root_dir"/;
	my $query = $dbhandle->prepare($rootDirKeyValQuery);
	until(
		$query->execute()
	){
		warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
		warn "Failed on the following query: $rootDirKeyValQuery\n";
		sleep(5);
	}	
	my $directoryKeyVal = eval { $query->fetchrow_arrayref->[0] };

	our $numPassed = 0;
	#####
		open OUTPUT,  ">unhandled_files.txt" or die $!;
		addFilesInListOfSubdirs(\@subdirectories, $directoryKeyVal, $root_dir, \$numPassed, $portNum);
		close OUTPUT;
	#####

	my ($sec,$min,$hour,$mday,$mon,$year) = localtime(time);
	$year += 1900;
	$mon += 1;

	my $dateTime = sprintf("%04d-%02d-%02d %02d:%02d:%02d", $year, $mon, $mday, $hour, $min, $sec);

	my $updatedValQuery = qq/UPDATE $params::metadataTableName SET $params::metadataValueColumn = "$dateTime" WHERE $params::metadataNameColumn = "$params::metadataLastEditedField"/;
	
	$query = $dbhandle->prepare($updatedValQuery);
	until(
		$query->execute()
	){
		warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
		warn "Failed on the following query: $updatedValQuery\n";
		sleep(5);
	}
}


$geoserverProc->die;

$dbhandle->disconnect;