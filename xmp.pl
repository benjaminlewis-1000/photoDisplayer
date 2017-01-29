#! /usr/bin/perl


use Time::HiRes qw( usleep gettimeofday tv_interval  );
use Date::Parse;
use params;
use Data::Dumper;

use Image::EXIF;

use warnings;
use strict; 

my $file = "C:\\Users\\Benjamin\\Dropbox\\Perl Code\\photoDisplayer\\base\\canon pictures 012.JPG";

	my $d = 0;
	my $sttime = [gettimeofday];

	my $exif = new Image::EXIF($file);

	my $elapsed = tv_interval($sttime);
	print "Elapsed " . $d++ . ": " . $elapsed . "\n";

	my $imInfo = $exif->get_image_info();

	my $elapsed = tv_interval($sttime);
	print "Elapsed " . $d++ . ": " . $elapsed . "\n";

	print Dumper(%{$imInfo}) . "\n";

	print $imInfo->{'Image Height'} . "\n";

	my $unk = $exif->get_all_info();

	print Dumper(%{$unk}) . "\n";

	my $elapsed = tv_interval($sttime);
	print "Elapsed " . $d++ . ": " . $elapsed . "\n";
use Image::Magick;
 my $im = Image::Magick->new();
	my $elapsed = tv_interval($sttime);
	print "Elapsed " . $d++ . ": " . $elapsed . "\n";
 $im->Read($file);
	my $elapsed = tv_interval($sttime);
	print "Elapsed " . $d++ . ": " . $elapsed . "\n";
 my $x =  $im->Identify();
	my $elapsed = tv_interval($sttime);
	print "Elapsed " . $d++ . ": " . $elapsed . "\n";