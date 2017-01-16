#! /usr/bin/perl

# Simple function: it takes a root directory, $root_dir, and queries the database to see if a database has been modified at a higher level. If no higher level has been inserted and we have not inserted this directory before, then the new root_dir is inserted in the $params::rootTableName. From there, we can list all the directories that are directly off this one and that are not covered by existing root directories. 

use params;
use DBI;
use Tk;
use File::Find;
use Data::Dumper;
require 'read_xmp.pl';
require 'readInImages.pl';

# my $root_dir = Tk::MainWindow->new->chooseDirectory;
# my $root_dir = 'D:\Pictures\2016';
my $root_dir = 'D:\Pictures\\';

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


##############
# Next step: Get a list of all files in the directory and its subdirectories. This will exclude directories that are under other root directories. We will populate two hashes: a %dirNameNumHash, which will give us the root directory's key number for each directory, and a %dirNameRelativeToHash, which gives us the subdirectory relative to the root directory.

# For example, with a directory structure like:
# /main
# /main/testa
# /main/testb
# /main/testc
#
# where /main/testc is already included from a previous inclusion and we are currently adding /main,
# we will get e.g. 2 for the /main directory number. Our directories that will be included are
# /main/testa and /main/testb (but not /main/testc, because it's been seen already). Then, by grepping out the
# root name, we will get dirNamesRelativeToRootHash of testa and testb. 
	my @file_list;

	my %dirNameNumHash; 
	my %dirNameRelativeToRootHash;
	# I don't understand this following line; source is http://www.perlmonks.org/?node_id=677380. 
	# The line gets the list of all images by relative directory from $root_dir. 
	find(sub { push @file_list, $File::Find::name }, $root_dir);

	# Get a list of subdirectories from this root directory, so we can see if they are already in the list. 
	# The regex is looking for the opposite of any file that ends with a .*** extension.
	my @subdirectories = grep(!/\.([a-zA-Z][^\.^\\]+$)/i, @file_list);
	# Remove the root directory. We now have a list of all the subdirectories. This is to help the iteration.
	@subdirectories = grep(/$root_dir/, @subdirectories);
	chomp(@subdirectories);
	# Copy the subdirectories into remainingSubdirs, which we can then remove from with impunity in a for loop. 
	my @remainingSubdirs = @subdirectories;

	for (my $i = 0; $i < scalar @subdirectories; $i++){
		# Query the database to see if it has this specific subdirectory already. If so, get it's key value and put it in $directoryKeyVal.
		my $dirExistsQuery = qq/SELECT $params::rootKeyColumn FROM $params::rootTableName WHERE $params::rootDirPath = "$subdirectories[$i]\/"/;
		my $query = $dbhandle->prepare($dirExistsQuery);

		until(
			$query->execute()
		){
			warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
			warn "Failed on the following query: $dirExistsQuery\n";
			sleep(5);
		}# or die $DBI::errstr;
		my $directoryKeyVal = eval { $query->fetchrow_arrayref->[0] };

		# Now, if the subdirectory is already accounted for, get its key number and base directory and add it to the appropriate hashes. Then remove it and all its subdirectories from the @remainingSubdirs list. 
		if ($directoryKeyVal ne ""){

			# The directory exists, and we need to do something about it.
			#### Get a list of the directory and subdirectory that are already in the database.
			### my @existingDirectories = grep(/$subdirectories[$i]/, @subdirectories); 
			# Remove this directory and its subdirectories from the list of remaining subdirectories. 
			# Because of the magic of grep, we will get subdirectories of the root directory automatically.
			@remainingSubdirs = grep(!/$subdirectories[$i]/, @remainingSubdirs);

			# foreach my $val (@existingDirectories){
			# 	$dirNameNumHash{$val} = $directoryKeyVal;
			# 	$dirNameRelativeToRootHash{$val} = "ss --- " . $subdirectories[$i] . "/";
			# }
		}
	}

	# Output at this level: A list of all subdirectories of the added directory here, not including subdirectories of previously included root directories. 

	# Push the root directory back on the remaining directories.
	push(@remainingSubdirs, $root_dir);
	# print "Subdirectories: are now\n";
	# print join ("\n", @remainingSubdirs) . "\n";

	# # Query the database for the key value for the current 
	# my $rootDirKeyValQuery = qq/SELECT $params::rootKeyColumn FROM $params::rootTableName WHERE $params::rootDirPath = "$root_dir"/;
	# my $query = $dbhandle->prepare($rootDirKeyValQuery);
	# # print $dirExistsQuery . "\n";
	# $query->execute() or die $DBI::errstr;
	# my $directoryKeyVal = eval { $query->fetchrow_arrayref->[0] };

	# We already have the directoryKeyVal from inserting the root directory (we can't get here if we didn't just add the directory.) We will also remove the $root_dir from the subdirectories that are remaining to give us a relative directory.
	foreach my $val (@remainingSubdirs){
		$val =~ s/$root_dir//g;
		# $dirNameNumHash{$val} = $directoryKeyVal;
		$dirNameRelativeToRootHash{$val} = $root_dir;
	}

	# print Dumper(%dirNameNumHash) . "\n";
	# print Dumper(%dirNameRelativeToRootHash);

	open OUTPUT,  ">unhandled_files.txt" or die $!;

	foreach my $localDir (@remainingSubdirs){
		my @filesInDir;
		my $odir = $root_dir . $localDir;
		if ( !($odir =~ m/\/$/ ) ) {
			print OUTPUT "$odir isn't a valid directory. \n";
		}
		opendir my $dir, "$odir" or next; #print "$odir isn't a valid directory. \n";
		# 	next;
		# } #die "Can't open directory " . $odir . ": $!";
		my @filesInDir = readdir $dir;
		closedir $dir; 
		# find(sub { push @filesInDir, $File::Find::name }, $root_dir . $val);
		if ($params::debug and $params::debugNewRoot) { print $localDir . "\t: "; } # grep(!/$subdirectories[$i]/, @remainingSubdirs);
		my @filesInDir =  grep(/\.JPE?G/i, @filesInDir);
		if ($params::debug and $params::debugNewRoot) { print join(',  ', @filesInDir) . "\n\n"; }

		if ($localDir ne "" ){
			$localDir .= "/";
		}

		my %nameHash;

		readImages({
			filelist => \@filesInDir,
			baseDirNum => $directoryKeyVal,
			localDir => $localDir,
			rootDirName => $root_dir,
			nameHash => \%nameHash
		});	

		# readImages({
		# 	filelist => \@filesInDir,
		# 	baseDirNum => $directoryKeyVal,
		# 	localDir => $root_dir . $localDir
		# });	
		# add_images(@filesInDir, $root_dir . $localDir, $directoryKeyVal)

	}

	close OUTPUT;

	# foreach my $val ()
#TODO: Find if the subdirectories are already in the database. Then reject them from this list. 

	# Get only files that have a JPG (case-insensitive) ending. JPG are the majority of my 
	# pictures, and they have EXIF data.
	# @file_list = @jpg_files;

	# # Use regex to take out the 
	# for( my $i = 0; $i < scalar @jpg_files; $i++){
	# 	$jpg_files[$i] =~ s{$root_dir}{}g;
	# }

##############

##############

# Test: Choose one of the images... Just to make sure that replacing back slashes works on Windows.

	# my %data = getImageData({
	# 	filename => $root_dir . $jpg_files[4],
	# 	resX => 0,
	# 	resY => 0
	# 	});

	# print "Names: " . join(";", @{$data{'NameList'}}) . "\n";
##############
