#! /usr/bin/perl 

use params;
require 'read_xmp.pl';

sub readImages{

	my ($args) = @_;

	if (! defined $args->{filelist}){
		print "Error: File not passed\n";
	}

	if (! defined $args->{baseDirNum}){
		$args->{resX} = 1000;
	}

	if (! defined $args->{localDir}){
		$args->{resY} = 1000;
	}

	my @filelist = @{$args->{filelist}};

	if (scalar (@filelist) == 0){
		return;
	}
	# Parameters for image size and face size. 
	my $baseDirNum = $args->{baseDirNum};
	my $localDir = $args->{localDir};

	print $localDir . "  " . $baseDirNum . "  " . join(" ~ ", @filelist) . "\n";

	foreach my $picture (@filelist){
		my %data = getImageData({
			filename => $localDir . "/" . $picture,
			resX => 0,
			resY => 0
			});

		if (!$data{'Status'} ){
			print "$!\n";
			exit;
		}
		print "Names: " . join(";", @{$data{'NameList'}}) . "\n";

	}

};

1;