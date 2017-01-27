#! /usr/bin/perl

# TODO: Get time from the internet/make sure time is set properly. Otherwise our modification dates are going to be out of whack. 

use strict;
use warnings;
use DBI;
use File::Stat;

use params;
require 'read_xmp.pl';

my $root_dir = 'C:\Users\Benjamin\Dropbox\Perl Code\photoDisplayer\base\\';
	# Parameters for image size and face size. 
my $baseDirNum = 1;
# my @filesInDir = ('canon pictures 018.JPG');
my @filesInDir = ('dirA\2013-11-05 19.43.48.jpg', 'canon pictures 012.JPG', 'canon pictures 018.JPG', 'dir with spaces and jpg/1235_58205421712_2635_n.jpg');
my $localDir = '';
my %nameHash;

# readImages({
# 	filelist => \@filesInDir,
# 	baseDirNum => $baseDirNum,
# 	localDir => $localDir,
# 	rootDirName => $root_dir,
# 	nameHash => \%nameHash
# });	

# print Dumper(%nameHash);

# sub readImages{

# 	my ($args) = @_;
# 	my $rootDirNum;
# 	my $baseDirName;
# 	my $localDir;
# 	my @filelist;
# 	my $numProcessed;

# 	our $dbhandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");

# 	if (! defined $args->{filelist}){
# 		die("Error: File not passed\n");
# 	}else{
# 		@filelist = @{$args->{filelist}};
# 	}

# 	if (! defined $args->{nameHash}){
# 		die("Error: Hash of names not passed\n");
# 	}

# 	if (defined $args->{baseDirNum}){
# 		$rootDirNum = $args->{baseDirNum};
# 	}

# 	if (defined $args->{localDir}){
# 		$localDir = $args->{localDir};
# 	}

# 	if (defined $args->{rootDirName}){
# 		$baseDirName = $args->{rootDirName};
# 	}

# 	if (scalar (@filelist) == 0){
# 		return;
# 	}

# 	our $dummy = 0;
# 	if (! defined $args->{numProcessed}){
# 		$numProcessed = \$dummy;
# 	}else{
# 		$numProcessed = $args->{numProcessed};
# 	}

# 	# if (! defined $args->{tmpTableMade} or $args->{tmpTableMade} == 0){
# 	# 	print "Temp table hasn't been made. We will now create that.";
# 	# 	# We really want this table to be here. 
# 	# 	my $tmpTableQuery = qq/CREATE TABLE IF NOT EXISTS $params::tempTableName ($params::insertDateColumn STRING, $params::photoFileColumn STRING, $params::rootDirNumColumn STRING)/;
# 	# 	my $query = $dbhandle->prepare($tmpTableQuery);
# 	# 	until(
# 	# 		$query->execute()
# 	# 	){
# 	# 		warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
# 	# 		warn "Failed on the following query: $tmpTableQuery\n";
# 	# 		sleep(5);
# 	# 	}# or die $DBI::errstr;

# 	# 	my $populateQuery = qq/INSERT INTO $params::tempTableName SELECT $params::insertDateColumn, $params::photoFileColumn, $params::rootDirNumColumn FROM $params::photoTableName/;
# 	# 	$query = $dbhandle->prepare($populateQuery);
# 	# 	until(
# 	# 		$query->execute()
# 	# 	){
# 	# 		warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
# 	# 		warn "Failed on the following query: $populateQuery\n";
# 	# 		sleep(5);
# 	# 	}# or die $DBI::errstr;

# 	# }


# 	foreach my $imageFile (@filelist){
# 		${$numProcessed} += 1;
# 		if (${$numProcessed} % 500 == 0){
# 			print "We have read ${$numProcessed} files and processed them accordingly.\n";
# 		}
# 		image_Foobar({
# 			baseDirName => $baseDirName, 
# 			fileName => $localDir . $imageFile, 
# 			rootDirNum => $rootDirNum,
# 			nameHash => $args->{nameHash},
# 			dbhandle => $dbhandle
# 		});
# 	}

# 	# if (! defined $args->{tmpTableMade} or $args->{tmpTableMade} == 0){

# 	# 	# Get rid of the temp table. 
# 	# 	my $deleteTmpQuery = qq/DELETE TABLE $params::tempTableName/;
# 	# 	my $query = $dbhandle->prepare($deleteTmpQuery);
# 	# 	until(
# 	# 		$query->execute()
# 	# 	){
# 	# 		warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
# 	# 		warn "Failed on the following query: $deleteTmpQuery\n";
# 	# 		sleep(5);
# 	# 	}# or die $DBI::errstr;

# 	# }

# };
	# $root_dir = '';

	# Instead of looking up the root directory every time, we should put it in a table. (Have the right length first, then read it in. )

	# my @ls = glob("'.pl || .txt' *");
	# print join(', ', @ls) . "\n";

sub image_Foobar{

	use Time::HiRes qw( usleep gettimeofday tv_interval  );
	use POSIX qw(strftime);

	my ($args) = @_;

	our ($baseDirName, $fileName, $rootDirNum, $nameHashRef, $dbhandle);
	our $insertedDateHashRef;

	if (defined $args->{nameHash}){
		$nameHashRef = $args->{nameHash};
	}

	if (! defined $args->{baseDirNum}){
		print "Root directory number not passed in\n";
		return;
	}else{
		$rootDirNum = $args->{baseDirNum};
	}

	if (! defined $args->{fileName} ){
		print "Filename not passed\n";
		return;
	}else{
		$fileName = $args->{fileName};
	}

	if (! defined $args->{dbhandle}){
		$dbhandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");
	}else{
		$dbhandle = $args->{dbhandle};
	}

	if (! defined  $args->{baseDirName}){
		print "Base dir not passed\n";
		return;
	}else{
		$baseDirName = $args->{baseDirName};
	}

	if (!defined $args->{insertedDateHash} ){
		print "Inserted date hash isn't present.\n";
		return;
	}else{
		$insertedDateHashRef = $args->{insertedDateHash};
	}



	# Get the last modified date. 
	if ( open (my $fh, "<", $baseDirName . $fileName) ){
		# Get the modification date of the file, and format it in ISO 8601 (ish) standard 
	my $sttime = [gettimeofday];
	my $elapse = tv_interval($sttime);
		my $e_ts = (stat($fh))[9];
		my $fileLastEditDate = strftime('%Y-%m-%d %H:%M:%S', localtime( $e_ts ) ) ;

	# $elapse = tv_interval($sttime);
	# print "Elapsed -1 is " . $elapse . "\n";

		# Query the database for the date on which the photo was last updated. 
		# my $editedInDBQuery = qq/SELECT $params::insertDateColumn FROM $params::photoTableName WHERE $params::photoFileColumn = "$fileName" AND $params::rootDirNumColumn = $rootDirNum/;
	# $elapse = tv_interval($sttime);
	# print "Elapsed 0 is " . $elapse . "\n";
		my $dbInsertDate;
		if (defined $insertedDateHashRef->{$fileName} ){
			$dbInsertDate = $insertedDateHashRef->{$fileName};
		}


		# my $query = $dbhandle->prepare($editedInDBQuery);
		# until(
		# 	$query->execute()
		# ){
		# 	warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
		# 	warn "Failed on the following query: $editedInDBQuery\n";
		# 	sleep( 5 );
	 #    }# or die $DBI::errstr;
	# $elapse = tv_interval($sttime);
	# print "Elapsed 0.5 is " . $elapse . "\n";
		# my $dbInsertDate = eval { $query->fetchrow_arrayref->[0] };

		# print $dbInsertDate . "\n";
		# my $dbInsertDate = eval { $query->fetchrow_arrayref->[0] };
	# $elapse = tv_interval($sttime);
	# print "Elapsed 1 is " . $elapse . "\n";

		# If we have the photo in the database, compare the insertion date with the file's modification date.
		# If we have inserted the photo after the last file modification, there is no need to continue. 
		if (defined $dbInsertDate ){
			if ($params::debug and $params::debug_readIn) { 
				print "DB Last edit date: " . $dbInsertDate . "\n";
			}

			if ($dbInsertDate gt $fileLastEditDate){
				if ($params::debug and $params::debug_readIn) { 
					print "Already in\n"; 
				}
	# $elapse = tv_interval($sttime);
	# print "Elapsed 2 is " . $elapse . "\n";

				return;
			}
		}
	# $elapse = tv_interval($sttime);
	# print "Elapsed is " . $elapse . "\n";

# my $stat_epoch = stat( '/home/lewisbp/test.pl' )->ctime;
# print strftime('%Y-%m-%d %H:%M:%S', localtime( $stat_epoch ) );
	}

	# print Dumper(%nameHash);
	print "Currently processing image: " . $baseDirName . $fileName  . "\n";

	my $sttime = [gettimeofday];

	my %data = getImageData({
		filename => $baseDirName . $fileName,
		resX => 0,
		resY => 0
		});

	if ($params::debug and $params::debug_readIn) { 
		my $elapse = tv_interval($sttime);
		print "Elapsed is " . $elapse . "\n";
	}

	if (!$data{'Status'} ){
		print "Read XMP has failed - $!\n";
		exit;
	}

	my ($sec,$min,$hour,$mday,$mon,$year) = localtime(time);
	$year += 1900;
	$mon += 1;
	my $dbInsertionDate = sprintf("%04d-%02d-%02d %02d:%02d:%02d", $year, $mon, $mday, $hour, $min, $sec);

	# Quick check to make sure that the system time is set properly. I'm writing this code in 2017, 
	# so this is fairly accurate right now. In the future, it may only catch systems that are set 
	# to epoch time (1/1/1970ish), but we're looking for best effort right now. 
	if ($year < 2017){
		die("Your time zone is not correct. It must be correct for this function to work.\n");
	}

	if ($params::debug and $params::debug_readIn) { 
		print "Names: " . join(";", @{$data{'NameList'}}) . "\n"; 
		print $data{'TakenDate'} . "\n";
	}

	# With the file: 

	# ISO8601 strings ("YYYY-MM-DD HH:MM:SS.SSS")

	# our $taken_date = sprintf("%04d-%02d-%02d %02d:%02d:%02d", $data{'Year'}, $data{'Month'}, $data{'Day'}, $data{'Hour'}, $data{'Minute'}, $data{'Second'});


	# print "Date is " . $taken_date . "\n";

	our %peopleToKeyHash;

	my $checkPhotoInTableQuery = qq/SELECT * FROM $params::photoTableName WHERE $params::photoFileColumn = "$fileName" AND $params::rootDirNumColumn = $rootDirNum/;

	my $query = $dbhandle->prepare($checkPhotoInTableQuery);
	until(
		$query->execute()
	){
		warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
		warn "Failed on the following query: $checkPhotoInTableQuery\n";
		sleep( 5 * 60 );
    }# or die $DBI::errstr;
	my $photoExists = eval { $query->fetchrow_arrayref->[0] };
		# print $photoExists ? "Photo Exists\n" : "Photo doesn't exist\n";

				# my $query = $dbhandle->prepare($dirExistsQuery);
				# # print $dirExistsQuery . "\n";
				# $query->execute() or die $DBI::errstr;
				# $directoryKeyVal = eval { $query->fetchrow_arrayref->[0] };

		# print $checkPhotoInTableQuery . "\n";

	our $upToDate = 0;

	if ($photoExists){
		# Get the date when the photo was inserted from the table. 
		my $lastModifiedQuery = qq/SELECT $params::insertDateColumn FROM $params::photoTableName WHERE $params::photoFileColumn = "$fileName" AND $params::rootDirNumColumn = $rootDirNum/;
		$query = $dbhandle->prepare($lastModifiedQuery);
		until(
			$query->execute()
		){
			warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
			warn "Failed on the following query: $lastModifiedQuery\n";
			sleep(5);
		}# or die $DBI::errstr;
		my $lastModDate = eval {$query->fetchrow_arrayref->[0] };

		# Even though we haven't included time zone/GMT into this comparison, it is sufficiently robust for systems that are on the correct time... oh... anyway, if we have modified the picture on the same system that it is now being stored in, the "modify date" will be relative to each other. 
		# TODO: Make sure the system that is adding is on a correct time relative to the world (1970 won't work)
		if ($lastModDate gt $data{'ModifyDate'}) {
			if ($params::debug and $params::debug_readIn){
				print $lastModDate . "   " . $data{'ModifyDate'}  . "\n";
				print "We have inserted this in the table at a later date than the photo was modified.\n";
			}
			$upToDate = 1;
		}else{
			if ($params::debug and $params::debug_readIn){
				print $lastModDate . "   " . $data{'ModifyDate'}  . "\n";
				print "The photo has been modified since we inserted it in the table.\n";
			}

			# Remove the old data from the table. 
			my $photoKeyQuery = qq/SELECT * FROM $params::photoTableName WHERE $params::photoFileColumn = "$fileName" AND $params::rootDirNumColumn = $rootDirNum/ ;
			$query = $dbhandle->prepare($photoKeyQuery);
			until(
				$query->execute()
			){
				warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
				warn "Failed on the following query: $photoKeyQuery\n";
				sleep(5);
			}# or die $DBI::errstr;
			my $photoKeyNum = eval {$query->fetchrow_arrayref->[0] };

			my $unlinkLinkerQuery = qq/DELETE FROM $params::linkerTableName WHERE $params::linkerPhotoColumn = $photoKeyNum/;
			$query = $dbhandle->prepare($unlinkLinkerQuery);
			until(
				$query->execute()
			){
				warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
				warn "Failed on the following query: $unlinkLinkerQuery\n";
				sleep(5);
			}# or die $DBI::errstr;
			my $deletePhotoQuery = qq/DELETE FROM $params::photoTableName WHERE $params::photoKeyColumn = $photoKeyNum/;
			$query = $dbhandle->prepare($deletePhotoQuery);
			until(
				$query->execute()
			){
				warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
				warn "Failed on the following query: $deletePhotoQuery\n";
				sleep(5);
			}# or die $DBI::errstr;


		}

		# If we are debugging and are up to date, print the message; else, silently return.
		if ( ( $params::debug  and $params::debug_readIn ) or !$upToDate){ # Get in this loop if we ARE debugging OR if we ARE NOT up to date.
			if ($upToDate){ # Print this message if we ARE debugging AND ARE up to date. 
				print "Would be exiting here b/c photo exists\n";}
			} else{ # Return if we ARE NOT debugging AND we ARE up to date. 
			  return; 
			} 
		} 

	# Insert the data about the photo (date and filename) into the appropriate table. 
	my $insertIntoPhotoTable = qq/
	INSERT INTO $params::photoTableName ( 
		$params::photoFileColumn, $params::photoDateColumn, 
		$params::modifyDateColumn, $params::rootDirNumColumn, 
		$params::photoYearColumn, $params::photoMonthColumn, 
		$params::photoDayColumn, $params::photoHourColumn, 
		$params::photoMinuteColumn, $params::photoGMTColumn,
		$params::insertDateColumn)  
	VALUES ("$fileName", 
		"$data{'TakenDate'}", "$data{"ModifyDate"}", 
		$rootDirNum, $data{'Year'}, 
		$data{'Month'}, $data{'Day'}, 
		$data{'Hour'}, $data{'Minute'}, 
		$data{'TimeZone'}, "$dbInsertionDate"
	)/;
		# print $insertIntoPhotoTable . "\n ";

	$dbhandle->do($insertIntoPhotoTable) or die $DBI::errstr;

	# Get the value of the autoincremented value for the table; this value is in $photoKeyVal
	my $keyNumQuery = qq/SELECT last_insert_rowid()/;
	$query = $dbhandle->prepare($keyNumQuery);
	until(
		$query->execute()
	){
		warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
		warn "Failed on the following query: $keyNumQuery\n";
		sleep(5);
	}# or die $DBI::errstr;
	my $photoKeyVal = @{$query->fetch()}[0];
	# print $photoKeyVal . "\n";

	# Now we need to tackle inserting names into the database. I want to have a hash with the names and check it. 
	# If the name has already been encountered, we should read its public key from the hash. Else, we need to add 
	# it to the hash, add it to the people database, and save the public key for future use. 

	# I need to be able to pass in the $peopleToKeyHash effectively between pictures. Otherwise I will be putting
	# it together for each photo, and that's not good. 

#### ## FAIRLY TESTED TO HERE ## #### 

	foreach (@{$data{'NameList'}}){
		our $peopleKeyVal = -1;
		if ($params::debug and $params::debug_readIn) { print "Name is : " . $_ . " : " ; }

		# $_[0]->{'e'} = "tesing";
		# print "\nFirst person: " . $args->{nameHash}->{'a'} . "\n";
		# The name hash keeps a hash of people and their unique ID's. It is passed into the function
		# by reference and should be initialized from scratch at the beginning of batch processing 
		# (so that we know that the unique ID's are correct.) Reading from the database to initialize
		# is acceptable. 
		if (exists($nameHashRef->{$_})){
			if ($params::debug and $params::debug_readIn) { print "$_ exists\n"; }
			$peopleKeyVal = $nameHashRef->{$_};
		}
		else{

			# Check if person exists in the database if they're not in the hash. This is for redundancy
			# in case the hash hasn't been initialized from the database. 

			# SQL Query : Ask for the unique key for the person from the database, and store it in 
			# $peopleKeyVal if the peron exists. 
			# If they do, then get their unique key and add it to the hash so that we don't have to find it 
			# ever again. 
			my $personExistsQuery = qq/SELECT $params::peopleKeyColumn FROM $params::peopleTableName WHERE $params::personNameColumn = "$_"/;

			my $query = $dbhandle->prepare($personExistsQuery);
			until(
				$query->execute()
			){
				warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
				warn "Failed on the following query: $personExistsQuery\n";
				sleep(5);
			}# or die $DBI::errstr;
			my $result = eval { $query->fetchrow_arrayref->[0] }; # Can be an uninitialized value. 
							# The uninitialized value would mean that we haven't seen that person. 

			# Find the number of people in the database with that name; should be only one. 
			# TODO: Work out how to distinguish people with the exact same name... 
			my $numQuery = qq/SELECT COUNT(*) FROM $params::peopleTableName WHERE $params::personNameColumn = "$_"/;
			$query = $dbhandle->prepare($numQuery);
			until(
				$query->execute()
			){
				warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
				warn "Failed on the following query: $numQuery\n";
				sleep(5);
			}# or die $DBI::errstr;
			my $numPeopleWithName = eval { $query->fetchrow_arrayref->[0] };
			if ($params::debug and $params::debug_readIn) { print $numPeopleWithName . " people have that name.". "\n"; }

			if($result and $numPeopleWithName == 1){
				$peopleKeyVal = $result;
				$nameHashRef->{$_} = $result;
			}

			# If we well and truly can't find the person in the database, insert their name in the database with a unique identifier and 
			# add the identifier to the hash. 
			else {

				if ($numPeopleWithName > 1){ # Handle this bug when we get there. 
					die("Error! Getting more than one person with this name: $_.");
				}

				my $insertPersonInPersonTable = qq/INSERT INTO $params::peopleTableName ($params::personNameColumn) VALUES ("$_")/;

				$dbhandle->do($insertPersonInPersonTable) or die $DBI::errstr;

				# Get the unique ID of the person entered and place it in the hash by reference. 
				my $keyNumQuery = qq/SELECT last_insert_rowid()/;
				my $query = $dbhandle->prepare($keyNumQuery);
				until(
					$query->execute()
				){
					warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
					warn "Failed on the following query: $keyNumQuery\n";
					sleep(5);
				}# or die $DBI::errstr;
				$peopleKeyVal = @{$query->fetch()}[0];
				$nameHashRef->{$_} = $peopleKeyVal;
			}
		}

		# Add to linker table: 

		my $insertLinkInTable = qq/INSERT INTO $params::linkerTableName ($params::linkerPeopleColumn, $params::linkerPhotoColumn) VALUES ($peopleKeyVal, $photoKeyVal)/;
		$dbhandle->do($insertLinkInTable);

	}

};

1;



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