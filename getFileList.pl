#! /usr/bin/perl

use params;
use DBI;
use Tk;
use File::Find;
use Data::Dumper;
require 'read_xmp.pl';

# my $root_dir = Tk::MainWindow->new->chooseDirectory;
# my $root_dir = 'D:\Pictures\2016';
my $root_dir = 'C:\Users\Benjamin\Dropbox\Perl Code\photoDisplayer\base';

# Add a backslash to the end and create the back/forward slashes as necessary. 
$root_dir = $root_dir . '/';
$root_dir =~ s/\\/\//g;
print $root_dir . "\n";

our $dbhandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");

##############

	#  Check if a higher-up directory is already in the table. If so, we don't need to add this in. 
	my $existingRootDirsQuery = qq/SELECT $params::rootDirPath FROM $params::rootTableName/;
	my $query = $dbhandle->prepare($existingRootDirsQuery);
	$query->execute() or die $DBI::errstr;

	my $higherDirectoryExists = 0;

	my $directoryKeyVal;
	
	while (my @row = $query->fetchrow_array) { # retrieve one row
	    my $registeredRow = join("", @row);
	    if ( $root_dir =~ $registeredRow ){
	    	print "I've put this in already at a higher level. Exiting.\n";
	    	$higherDirectoryExists = 1;

	    	my $dirExistsQuery = qq/SELECT $params::rootKeyColumn FROM $params::rootTableName WHERE $params::rootDirPath = "$registeredRow"/;
			my $query = $dbhandle->prepare($dirExistsQuery);
			# print $dirExistsQuery . "\n";
			$query->execute() or die $DBI::errstr;
			$directoryKeyVal = eval { $query->fetchrow_arrayref->[0] };

			exit();

	    }
	}


# Check if the root directory is already in the table. If so, get its number.
# If not, insert into the table. 
	if (!$higherDirectoryExists){
		my $rootDirExistsQuery = qq/SELECT $params::rootKeyColumn FROM $params::rootTableName WHERE $params::rootDirPath = "$root_dir"/;
		my $query = $dbhandle->prepare($rootDirExistsQuery);
		$query->execute() or die $DBI::errstr;
		$directoryKeyVal = eval { $query->fetchrow_arrayref->[0] };

		if ($directoryKeyVal eq "" ){
			# If the directory doesn't exist, we then have to add it to the root directory table and get its unique key value (for use in adding all the pictures).
			print "Inserting";

			my $insertDirectory = qq/INSERT INTO $params::rootTableName ( $params::rootDirPath)  VALUES ("$root_dir")/;
			$dbhandle->do($insertDirectory) or die $DBI::errstr;

			# Get the value of the autoincremented value for the table; this value is in $directoryKeyVal
			my $keyNumQuery = qq/SELECT last_insert_rowid()/;
			my $query = $dbhandle->prepare($keyNumQuery);
			$query->execute() or die $DBI::errstr;
			$directoryKeyVal = @{$query->fetch()}[0];
			print "Key val is " . $directoryKeyVal . "\n";
		}else{
			# We have the directory already. Its directory key value is in $result.
			print "We have that directory, and the corresponding key value is $directoryKeyVal\n";
		}
	}

	print $directoryKeyVal . "\n";

##############

##############
# Next step: Get a list of all files in the directory and its subdirectories. The 
	my @file_list;

	my %dirNameNumHash; 
	my %dirNameRootHash;
	# I don't understand it; source is http://www.perlmonks.org/?node_id=677380. 
	# The line gets the list of all images by relative directory from $root_dir. 
	find(sub { push @file_list, $File::Find::name }, $root_dir);

	# Get a list of subdirectories, so we can see if they are already in the list. 
	# The regex is looking for the opposite of any file that ends with a .*** extension.
	my @subdirectories = grep(!/\.([a-zA-Z][^\.^\\]+$)/i, @file_list);
	# Remove the root directory. We now have a list of all the subdirectories. 
	@subdirectories = grep(/$root_dir/, @subdirectories);
	chomp(@subdirectories);
	my @remainingSubdirs = @subdirectories;

	print "Subdirectories: \n";
	print join ("\n", @subdirectories) . "\n";


	# for (my $i = 0; $i < scalar @subdirectories; $i++){
	# 	# Query the database to see if it has this specific subdirectory already. If so, get it's key value and put it in $directoryKeyVal.
	# 	my $dirExistsQuery = qq/SELECT $params::rootKeyColumn FROM $params::rootTableName WHERE $params::rootDirPath = "$subdirectories[$i]\/"/;
	# 	my $query = $dbhandle->prepare($dirExistsQuery);
	# 	# print $dirExistsQuery . "\n";
	# 	$query->execute() or die $DBI::errstr;
	# 	my $directoryKeyVal = eval { $query->fetchrow_arrayref->[0] };

	# 	# Now, if the subdirectory is already accounted for, get its key number and base directory and add it to the appropriate hashes. Then remove it and all its subdirectories from the @remainingSubdirs list. 
	# 	if ($directoryKeyVal ne ""){
	# 		# The directory exists, and we need to do something about it.
	# 		# Get a list of the directory and subdirectory that are already in the database.
	# 		my @existingDirectories = grep(/$subdirectories[$i]/, @subdirectories); 
	# 		# Remove it from the list of remaining subdirectories. 
	# 		@remainingSubdirs = grep(!/$subdirectories[$i]/, @remainingSubdirs);

	# 		# foreach my $val (@existingDirectories){
	# 		# 	$dirNameNumHash{$val} = $directoryKeyVal;
	# 		# 	$dirNameRootHash{$val} = "ss --- " . $subdirectories[$i] . "/";
	# 		# }
	# 	}# Else, it's fine. We're just going to be working on it. 
	# }

	# Output at this level: A list of all subdirectories of the added list here 

	print "Subdirectories: \n";
	print join ("\n", @subdirectories) . "\n";

	my $dirExistsQuery = qq/SELECT $params::rootKeyColumn FROM $params::rootTableName WHERE $params::rootDirPath = "$root_dir"/;
	my $query = $dbhandle->prepare($dirExistsQuery);
	# print $dirExistsQuery . "\n";
	$query->execute() or die $DBI::errstr;
	my $directoryKeyVal = eval { $query->fetchrow_arrayref->[0] };

	foreach my $val (@remainingSubdirs){
		$dirNameNumHash{$val} = $directoryKeyVal;
		$dirNameRootHash{$val} = $root_dir;
	}

	print Dumper(%dirNameNumHash) . "\n";
	print Dumper(%dirNameRootHash);
#TODO: Find if the subdirectories are already in the database. Then reject them from this list. 

	# Get only files that have a JPG (case-insensitive) ending. JPG are the majority of my 
	# pictures, and they have EXIF data.
	@jpg_files = grep(/JPG/i, @file_list);
	@file_list = @jpg_files;

	# Use regex to take out the 
	for( my $i = 0; $i < scalar @jpg_files; $i++){
		$jpg_files[$i] =~ s{$root_dir}{}g;
	}

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
