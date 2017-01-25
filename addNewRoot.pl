#! /usr/bin/perl

# Simple function: it takes a root directory, $root_dir, and queries the database to see if a database has been modified at a higher level. If no higher level has been inserted and we have not inserted this directory before, then the new root_dir is inserted in the $params::rootTableName. From there, we can list all the directories that are directly off this one and that are not covered by existing root directories. 

use params;
use DBI;
use Tk;
use File::Find;
use Data::Dumper;
require 'read_xmp.pl';
require 'readInImages.pl';
require 'filesFromBaseFinder.pl';

# my $root_dir = Tk::MainWindow->new->chooseDirectory;
# my $root_dir = 'D:\Pictures\2016';
my $root_dir = 'C:\Users\Benjamin\Dropbox\Perl Code\photoDisplayer\base\\';

# Remove any extraneous end-of-string slashes.
$root_dir =~ s/\\$//g;
$root_dir =~ s/\/$//g;

# Add a backslash to the end and replace back/forward slashes as necessary. 
$root_dir = $root_dir . '/';
$root_dir =~ s/\\/\//g;
print $root_dir . "\n";

# Open the database
our $dbhandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");

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
	    	print "I've put this in already at a higher level, at: $registeredRow. Exiting.\n";
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

		if ($directoryKeyVal eq "" ){
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

	#####
		open OUTPUT,  ">unhandled_files.txt" or die $!;
		addFilesInListOfSubdirs(\@subdirectories, $directoryKeyVal, $root_dir);
		close OUTPUT;
	#####

	my ($sec,$min,$hour,$mday,$mon,$year) = localtime(time);
	$year += 1900;
	$mon += 1;

	my $dateTime = sprintf("%04d-%02d-%02d %02d:%02d:%02d", $year, $mon, $mday, $hour, $min, $sec);

	my $updatedValQuery = qq/UPDATE $params::metadataTableName SET $params::metadataValueColumn = "$dateTime" WHERE "$params::metadataLastEditedField")/;
	
	my $metadata_handle = $dbhandle->prepare($updatedValQuery);
	$metadata_handle->execute() or die $DBI::errstr;

	$dbhandle->disconnect;