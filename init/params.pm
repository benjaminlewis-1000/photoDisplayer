# Package of parameters. 

#! /usr/bin/perl

package params;

use strict;
use warnings;
use Cwd;
use File::Basename;

my $osname = $^O;
our $OS_type;

our $windowsType = 1;
our $linuxType = 0;

if ($osname =~ m/win/i){
	$OS_type = $windowsType;
}elsif($osname =~ m/linux/i){
	$OS_type = $linuxType;
}else{
	die "OS is not defined. ";
}

our $base_path = cwd();  # Get the directory of this module. 

$base_path =~ m/(.*)\/.*$/;  # Regex to go up one directory.
$base_path = $1 . "/";  # Capture the output and put it in $base_path.

our $database = $base_path . "databases/" . "test.db";

our $debug = 0;

our $debug_readXMP = 0;
our $debug_readIn = 0;
our $debugNewRoot = 0;
# map {if (!$_) { ______ } } $params::debug;

## Table names
	our $photoTableName = "Photos";
	our $peopleTableName = "People";
	our $linkerTableName = "Linker";
	our $rootTableName = "Root_Dirs";
	our $metadataTableName = "Metadata";
	our $tempTableName = "TmpPhotoTable";

# Table column names 
	## Photo table
	our $photoKeyColumn = "photo_key";
	our $photoFileColumn = "photo_file";
	our $photoDateColumn = "photo_date";
	our $photoYearColumn = "taken_year";
	our $photoMonthColumn = "taken_month";
	our $photoDayColumn = "taken_day";
	our $photoHourColumn = "taken_hour";
	our $photoMinuteColumn = "taken_minute";
	our $photoGMTColumn = "taken_timezone";
	our $modifyDateColumn = "modification_date";
	our $rootDirNumColumn = "root_dir_num";
	our $insertDateColumn = "inserted_date";

	## People Table
	our $peopleKeyColumn = "people_key";
	our $personNameColumn = "person_name";
	# our $personPicasaID = "person_picasa_id";

	## Linker Table
	our $linkerPeopleColumn = "person";
	our $linkerPhotoColumn = "photo";

	## Root Directory Table
	our $rootDirPath;
	our $rootKeyColumn = "directory_root_key";
		our $windowsRootPath = "root_path_windows";
		our $linuxRootPath = "root_path_linux";
	if ($OS_type == $windowsType){
		$rootDirPath = $windowsRootPath;
	}else{
		$rootDirPath = $linuxRootPath;
	}

	## Metadata Table
	our $metadataNameColumn = "item_name";
	our $metadataValueColumn = "item_value";

	### Metadata fields
		our $metadataLastEditedField = "last_edited_date";

sub getLocalModTime{

	if (moduleIsLoaded('File::stat')){
		print "File::stat is loaded, which severely compromises the system. Die-ing!\n";
		return -1;
	}

	my $file = $_[0];
	return  localtime(  ( stat $file )[9] );
}


sub moduleIsLoaded {
    my ($pkg) = @_;
    (my $file = $pkg) =~ s/::/\//g;
    $file .= '.pm';
    my @loaded = grep { $_ eq $file } keys %INC;
    return @loaded;
}

1;