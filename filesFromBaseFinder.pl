#! /usr/bin/perl

use params;
require 'readInImages.pl';

#############  REUSABLE METHODS  ##################################


sub getUniqueSubdirs{
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

	my $base_directory = $_[0];

	our $localDBHandle = DBI->connect("DBI:SQLite:$params::database", "user" , "pass");

	my @file_list;

	my %dirNameNumHash; 
	my %dirNameRelativeToRootHash;
	# I don't understand this following line; source is http://www.perlmonks.org/?node_id=677380. 
	# The line gets the list of all images by relative directory from $base_directory. 
	find(sub { push @file_list, $File::Find::name }, $base_directory);

	# Get a list of subdirectories from this root directory, so we can see if they are already in the list. 
	# The regex is looking for the opposite of any file that ends with a .*** extension.
	my @subdirectories = grep(!/\.([a-zA-Z][^\.^\\]+$)/i, @file_list);
	# Remove the root directory. We now have a list of all the subdirectories. This is to help the iteration.
	@subdirectories = grep(/$base_directory/, @subdirectories);
	chomp(@subdirectories);
	# Copy the subdirectories into remainingSubdirs, which we can then remove from with impunity in a for loop. 
	my @remainingSubdirs = @subdirectories;

	for (my $i = 0; $i < scalar @subdirectories; $i++){
		# Query the database to see if it has this specific subdirectory already. If so, get it's key value and put it in $directoryKeyVal.
		# Remember that we've taken out this specific root directory, so we are in no danger of removing legitimate subdirectories. 
		my $dirExistsQuery = qq/SELECT $params::rootKeyColumn FROM $params::rootTableName WHERE $params::rootDirPath = "$subdirectories[$i]\/"/;
		my $query = $localDBHandle->prepare($dirExistsQuery);

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
			# Remove this directory and its subdirectories from the list of remaining subdirectories. 
			# Because of the magic of grep, we will remove subdirectories of the root directory automatically.
			@remainingSubdirs = grep(!/$subdirectories[$i]/, @remainingSubdirs);

		}
	}

	# Output at this level: A list of all subdirectories of the added directory here, not including subdirectories of other included root directories. 

	# Push the root directory back on the remaining directories.
	push(@remainingSubdirs, $base_directory);

	# We already have the directoryKeyVal from inserting the root directory (we can't get here if we didn't just add the directory.) We will also remove the $base_directory from the subdirectories that are remaining to give us a relative directory.
	foreach my $val (@remainingSubdirs){
		$val =~ s/$base_directory//g;
		$dirNameNumHash{$val} = $directoryKeyVal;
		$dirNameRelativeToRootHash{$val} = $base_directory;
	}

	$localDBHandle->disconnect;

	return @remainingSubdirs;

}

sub addFilesInListOfSubdirs{
#### Find a list of the files that are in each subdirectory. Call the readImages method on each of the files. 

	my @subdirectories = @{$_[0]}; 
	my $dirKeyVal = $_[1];
	my $rootDirectory = $_[2];

	foreach my $localDir (@subdirectories){
		my @filesInDir;
		my $odir = $rootDirectory . $localDir;
		if ( !($odir =~ m/\/$/ ) ) {
			print OUTPUT "$odir isn't a valid directory. \n";
		}
		opendir my $dir, "$odir" or next; #print "$odir isn't a valid directory. \n";
		# 	next;
		# } #die "Can't open directory " . $odir . ": $!";
		my @filesInDir = readdir $dir;
		closedir $dir; 

		if ($params::debug and $params::debugNewRoot) { print $localDir . "\t: "; } # grep(!/$subdirectories[$i]/, @subdirectories);
		my @filesInDir =  grep(/\.JPE?G/i, @filesInDir);
		if ($params::debug and $params::debugNewRoot) { print join(',  ', @filesInDir) . "\n\n"; }

		if ($localDir ne "" ){
			$localDir .= "/";
		}

		my %nameHash;

		readImages({
			filelist => \@filesInDir,
			baseDirNum => $dirKeyVal,
			localDir => $localDir,
			rootDirName => $rootDirectory,
			nameHash => \%nameHash
		});	

	}

}

1;