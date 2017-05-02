# Package of parameters. 

#! /usr/bin/perl

package params;

use strict;
use warnings;
use Cwd;
use File::Basename;
#use YAML::XS 'LoadFile';
use XML::Simple qw(:strict);
use Data::Dumper;

our $debug = 0;

	our $debug_readXMP = 0;
	our $debug_readIn = 0;
	our $debugNewRoot = 0;


our $base_path = cwd();  # Get the directory of this module. 
$base_path =~ m/(.*)\/.*$/;  # Regex to go up one directory.
$base_path = $1 . "/";  # Capture the output and put it in $base_path.

my $config_file = $base_path . "config/params.xml";
# my $config = LoadFile($YAML_file);  # YAML is more cross-language.

our $config = XMLin( $config_file, ForceArray => 1, KeyAttr=>[]) or die("Sorry! Can't read this XML.");

# print Dumper($config);
#print Dumper($config->{'ostypes'}->[0]) . "\n";


our $database = $base_path . "databases/" . $config->{'photoDatabase'}->[0]->{'fileName'}->[0];

my $osname = $^O;
our $OS_type;

my $osBase = $config->{'ostypes'}->[0];
our $windowsType = $osBase->{'windowsType'};
our $linuxType = $osBase->{'linuxType'};

if ($osname =~ m/win/i){
	$OS_type = $windowsType;
}elsif($osname =~ m/linux/i){
	$OS_type = $linuxType;
}else{
	die "OS is not defined. ";
}

# map {if (!$_) { ______ } } $params::debug;

## Table names
my $pdbBase = $config->{'photoDatabase'}->[0]->{'tables'}->[0];

	our $photoTableName = $pdbBase->{'photoTable'}->[0]->{'Name'}->[0];
	our $peopleTableName = $pdbBase->{'peopleTable'}->[0]->{'Name'}->[0];
	our $linkerTableName = $pdbBase->{'photoLinkerTable'}->[0]->{'Name'}->[0];  #$config->{'Name'};
	our $rootTableName = $pdbBase->{'rootTable'}->[0]->{'Name'}->[0];  #$config->{'Name'};
	our $metadataTableName = $pdbBase->{'metadataTable'}->[0]->{'Name'}->[0];  #$config->{'Name'};
	our $commentLinkerUserTableName = $pdbBase->{'commentLinkerUserTable'}->[0]->{'Name'}->[0];  #$config->{'Name'};
	our $commentLinkerGoogleTableName = $pdbBase->{'commentLinkerGoogleTable'}->[0]->{'Name'}->[0];  #$config->{'Name'};
	our $commentLinkerClarifaiTableName = $pdbBase->{'commentLinkerClarifaiTable'}->[0]->{'Name'}->[0];  #$config->{'Name'};

# Table column names 
	## Photo table
my $photoTableColumnBase = $config->{'photoDatabase'}->[0]->{'tables'}->[0]->{'photoTable'}->[0]->{'Columns'}->[0];

	our $photoKeyColumn = $photoTableColumnBase->{'photoKey'}->[0];
	our $photoFileColumn = $photoTableColumnBase->{'photoFile'}->[0];
	our $photoDateColumn = $photoTableColumnBase->{'photoDate'}->[0];
	our $photoYearColumn = $photoTableColumnBase->{'photoYear'}->[0];
	our $photoMonthColumn = $photoTableColumnBase->{'photoMonth'}->[0];
	our $photoDayColumn = $photoTableColumnBase->{'photoDay'}->[0];
	our $photoHourColumn = $photoTableColumnBase->{'photoHour'}->[0];
	our $photoMinuteColumn = $photoTableColumnBase->{'photoMinute'}->[0];
	our $photoGMTColumn = $photoTableColumnBase->{'photoGMT'}->[0];
	our $modifyDateColumn = $photoTableColumnBase->{'modifyDate'}->[0];
	our $rootDirNumColumn = $photoTableColumnBase->{'rootDirNum'}->[0];
	our $insertDateColumn = $photoTableColumnBase->{'insertDate'}->[0];
	our $houseNumColumn = $photoTableColumnBase->{'houseNum'}->[0];
	our $streetColumn = $photoTableColumnBase->{'street'}->[0];
	our $cityColumn = $photoTableColumnBase->{'city'}->[0];
	our $stateColumn = $photoTableColumnBase->{'state'}->[0];
	our $postcodeCoulumn = $photoTableColumnBase->{'postcode'}->[0];
	our $countryColumn = $photoTableColumnBase->{'country'}->[0];
	our $latColumn = $photoTableColumnBase->{'lat'}->[0];
	our $longColumn = $photoTableColumnBase->{'long'}->[0];

my $peopleTableColumnBase = $config->{'photoDatabase'}->[0]->{'tables'}->[0]->{'peopleTable'}->[0]->{'Columns'}->[0];
	## People Table
	our $peopleKeyColumn = $peopleTableColumnBase->{'peopleKey'}->[0];
	our $personNameColumn = $peopleTableColumnBase->{'personName'}->[0];

my $photoLinkerColumnBase = $config->{'photoDatabase'}->[0]->{'tables'}->[0]->{'photoLinkerTable'}->[0]->{'Columns'}->[0];
	## Photo Linker Table
	our $linkerPeopleColumn = $photoLinkerColumnBase->{'linkerPeople'}->[0];
	our $linkerPhotoColumn = $photoLinkerColumnBase->{'linkerPhoto'}->[0];

my $commentLinkerSharedColumnBase = $config->{'photoDatabase'}->[0]->{'tables'}->[0]->{'commentLinkerUserTable'}->[0]->{'Columns'}->[0];
	## Comment Linker Table
	our $commentLinkerPhotoColumn = $commentLinkerSharedColumnBase->{'commentLinkerPhoto'}->[0];
	our $commentLinkerTagColumn = $commentLinkerSharedColumnBase->{'commentLinkerTag'}->[0];
	our $commentLinkerTagProbabilityColumn = $commentLinkerSharedColumnBase->{'commentLinkerTagProbability'}->[0];

my $rootTableBase = $config->{'photoDatabase'}->[0]->{'tables'}->[0]->{'rootTable'}->[0]->{'Columns'}->[0];
	## Root Directory Table
	our $rootDirPath;
	our $rootKeyColumn = $rootTableBase->{'rootKey'}->[0];
		our $windowsRootPath = $rootTableBase->{'windowsRootPath'}->[0];
		our $linuxRootPath = $rootTableBase->{'linuxRootPath'}->[0];
	if ($OS_type == $windowsType){
		$rootDirPath = $windowsRootPath;
	}else{
		$rootDirPath = $linuxRootPath;
	}

my $metadataTableBase = $config->{'photoDatabase'}->[0]->{'tables'}->[0]->{'metadataTable'}->[0];
	## Metadata Table
	our $metadataNameColumn = $metadataTableBase->{'Columns'}->[0]->{'metadataName'}->[0];
	our $metadataValueColumn = $metadataTableBase->{'Columns'}->[0]->{'metadataValue'}->[0];

	### Metadata fields
		our $metadataLastEditedField = $metadataTableBase->{'Fields'}->[0]->{'metadataLastEditedField'}->[0];

my $visionParamsBase = $config->{'visionTaggingParams'}->[0];
	our $googVisionLabelPrefix = $visionParamsBase->{'googleTagging'}->[0]->{'googVisionLabelPrefix'}->[0];
	our $googImageHistoryPrefix = $visionParamsBase->{'googleTagging'}->[0]->{'googImageHistoryPrefix'}->[0];

	our $clarifaiVisionLabelPrefix = $visionParamsBase->{'clarifaiTagging'}->[0]->{'clarifaiVisionLabelPrefix'}->[0];
	our $clarifaiImageHistoryPrefix = $visionParamsBase->{'clarifaiTagging'}->[0]->{'clarifaiImageHistoryPrefix'}->[0];

	our $geoServerPort = $config->{'serverParams'}->[0]->{'geoServerPort'}->[0];

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