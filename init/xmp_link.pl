#! /usr/bin/perl

use JSON::Parse 'parse_json_safe';
use warnings;
use strict;
use Data::Dumper;
use Encode qw(encode decode);
use utf8;

# my $file = "D:/Pictures/Peru Trip 2014/100_8169.JPG";
# my %data = %{readExifPython($file)};
# 	print Dumper(%data);

sub readExifPython{
	my $file = $_[0];
	my $ret = '[' . `python getExif.py "$file"` . ']';
	print $ret . "\n";
	my %data;
	if (! parse_json_safe($ret)){
		print "no good\n";
		print $ret . "\n";
		$data{'Status'} = 0;
		return \%data;
	}

	my %jdata = %{parse_json_safe($ret)->[0]};

	my @autoTagsGoog = @{$jdata{'autoTagsGoogle'}};
	my @autoTagsClar = @{$jdata{'autoTagsClarifai'}};
	my @names = @{$jdata{'names'}};
	my @userTags = @{$jdata{'picasaTags'}};

	my %keywordsClarifaiHash;
	my %keywordsGoogHash;
	my %keywordsUserHash;
	for (my $i = 0; $i < scalar @autoTagsClar; $i++){
		$keywordsClarifaiHash{$autoTagsClar[$i][0]} = $autoTagsClar[$i][1];
	}
	for (my $i = 0; $i < scalar @autoTagsGoog; $i++){
		$keywordsGoogHash{$autoTagsGoog[$i][0]} = $autoTagsGoog[$i][1];
	}
	for (my $i = 0; $i < scalar @userTags; $i++){
		$keywordsUserHash{$userTags[$i]} = 1;
	}

	$data{'TakenDate'} = $jdata{'ISO8601'};
	$data{'Year'} = $jdata{'year'};
	$data{'Month'} = $jdata{'month'};
	$data{'Day'} = $jdata{'day'} ;
	$data{'Hour'} = $jdata{'hour'};
	$data{'Minute'} = $jdata{'min'};
	$data{'TimeZone'} = $jdata{'TimeZone'};
	$data{'house_number'} = $jdata{'house_number'};
	$data{'road'} = $jdata{'road'};
	$data{'city'} = $jdata{'city'};
	$data{'state'} = $jdata{'state'};
	$data{'postcode'} = $jdata{'postcode'};
	$data{'country'} = $jdata{'country'};
	$data{'Latitude'} = $jdata{'latitude'};
	$data{'Longitude'} = $jdata{'longitude'};

	$data{'Status'} = 1;

	$data{'keywordsUserHash'} = \%keywordsUserHash;
	$data{'keywordsGoogHash'} = \%keywordsGoogHash;
	$data{'keywordsClarifaiHash'} = \%keywordsClarifaiHash;
	$data{'NameList'} = \@names;

	return \%data;
	# print Dumper(%data) . "\n";

};

1;

# use Inline Python => <<'END';

#    print "hello world"

# END