# Package of parameters. 

#! /usr/bin/perl

package params;

use strict;
use warnings;
use Cwd;
use File::Basename;
use YAML::XS 'LoadFile';


our $debug = 0;

	our $debug_readXMP = 0;
	our $debug_readIn = 0;
	our $debugNewRoot = 0;


our $base_path = cwd();  # Get the directory of this module. 
$base_path =~ m/(.*)\/.*$/;  # Regex to go up one directory.
$base_path = $1 . "/";  # Capture the output and put it in $base_path.

my $YAML_file = $base_path . "config/params.yaml";
our $database = $base_path . "databases/" . "photos_master.db";

my $config = LoadFile($YAML_file);  # YAML is more cross-language.


my $osname = $^O;
our $OS_type;

our $windowsType = $config->{'windowsType'};
our $linuxType = $config->{'linuxType'};

if ($osname =~ m/win/i){
	$OS_type = $windowsType;
}elsif($osname =~ m/linux/i){
	$OS_type = $linuxType;
}else{
	die "OS is not defined. ";
}

# map {if (!$_) { ______ } } $params::debug;

## Table names
	our $photoTableName = $config->{'photoTableName'};
	our $peopleTableName = $config->{'peopleTableName'};
	our $linkerTableName = $config->{'linkerTableName'};
	our $rootTableName = $config->{'rootTableName'};
	our $metadataTableName = $config->{'metadataTableName'};

# Table column names 
	## Photo table
	our $photoKeyColumn = $config->{'photoKeyColumn'};
	our $photoFileColumn = $config->{'photoFileColumn'};
	our $photoDateColumn = $config->{'photoDateColumn'};
	our $photoYearColumn = $config->{'photoYearColumn'};
	our $photoMonthColumn = $config->{'photoMonthColumn'};
	our $photoDayColumn = $config->{'photoDayColumn'};
	our $photoHourColumn = $config->{'photoHourColumn'};
	our $photoMinuteColumn = $config->{'photoMinuteColumn'};
	our $photoGMTColumn = $config->{'photoGMTColumn'};
	our $modifyDateColumn = $config->{'modifyDateColumn'};
	our $rootDirNumColumn = $config->{'rootDirNumColumn'};
	our $insertDateColumn = $config->{'insertDateColumn'};

	## People Table
	our $peopleKeyColumn = $config->{'peopleKeyColumn'};
	our $personNameColumn = $config->{'personNameColumn'};
	# our $personPicasaID = "person_picasa_id";

	## Linker Table
	our $linkerPeopleColumn = $config->{'linkerPeopleColumn'};
	our $linkerPhotoColumn = $config->{'linkerPhotoColumn'};

	## Root Directory Table
	our $rootDirPath;
	our $rootKeyColumn = $config->{'rootKeyColumn'};
		our $windowsRootPath = $config->{'windowsRootPath'};
		our $linuxRootPath = $config->{'linuxRootPath'};
	if ($OS_type == $windowsType){
		$rootDirPath = $windowsRootPath;
	}else{
		$rootDirPath = $linuxRootPath;
	}

	## Metadata Table
	our $metadataNameColumn = $config->{'metadataNameColumn'};
	our $metadataValueColumn = $config->{'metadataValueColumn'};

	### Metadata fields
		our $metadataLastEditedField = $config->{'metadataLastEditedField'};

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