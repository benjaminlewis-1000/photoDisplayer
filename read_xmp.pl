#! /usr/bin/perl

# Read the XMP data from a file.

use Image::Magick;
use Image::ExifTool;
use Time::HiRes qw( usleep gettimeofday tv_interval  );
use Date::Parse;
use params;


# getImageData({
# 	filename => "/home/lewis/gitRepos/photoDisplayer/base/canon pictures 018.JPG",
# 	debug => 0
# 	});

sub getImageData{
	my ($args) = @_;
	my %returnData;
	$returnData{'Status'} = 0;

	if (! defined $args->{filename}){
		print "Error: File not passed\n";
		return %returnData;
	}

	if (! defined $args->{resX}){
		$args->{resX} = 1000;
	}

	if (! defined $args->{resY}){
		$args->{resY} = 1000;
	}

	if (! defined $args->{minSize}){
		$args->{minSize} = 0.0;
	}

	if ( defined $args->{debug}){
		if ($args->{debug}){
			$params::debug = 1;
			$params::debug_readXMP = 1;
		}
	}

	if ($params::debug and $params::debug_readXMP ) { print "Minimum size is: " . $args->{minSize} . "\n"; }

	if (! -e $args->{filename}){
		print "File does not exist! $args->{filename}\n";
		return %returnData;
	}

	my $file = $args->{filename};
	# Parameters for image size and face size. 
	my $minSize = $args->{minSize};
	my $minResX = $args->{resX};
	my $minResY = $args->{resY};

	# print "Min size is $minSize \n";

	my $t0 = [gettimeofday];

	#my $file = 'D:\Pictures\Picasa\Collages\New folder.jpg';
	# $file = 'D:\Pictures\Family Pictures\2011\2011 (10) October\DSC_0138.JPG';

	my $im = Image::Magick->new();
	$im->read($args->{filename}) ;#or die "Cannot open '$args->{filename}': $!\n";

	my $elapsed = tv_interval ( $t0 );
	# print $elapsed . "\n";

	my $exif = Image::ExifTool->new();
	my $info = $exif->ImageInfo($file);
	my %infoHash = %$info;

	# print ref( $exif->ImageInfo($file) ) . "\n\n";

	use Data::Dumper;
	delete $infoHash{"ThumbnailImage"};
	# print Dumper %infoHash;

	$elapsed = tv_interval ( $t0 );
	# print $elapsed . "\n";

	# foreach my $k (keys %infoHash){
	# 	if ($k =~ m/Mod/){
	# 		print $k . " : " . $infoHash{$k} . "\n";
	# 	}
	# }

	# Parse the XMP data. 

	my $namelist = $infoHash{'RegionName'};
	my $regionWidth = $infoHash{'RegionAreaW'};
	my $regionHeight = $infoHash{'RegionAreaH'};

	my $takenDate = $infoHash{'FileCreateDate'};
	my $modifyDate = $infoHash{'FileModifyDate'};

	{ # Parse the date. 
		my $time = str2time($takenDate);
		($ss, $mm, $hh, $day, $month, $year, $zone) = strptime($takenDate);
		$year += 1900;
		$month += 1;
		# print $year . "\n";
	}

	my $fileSize = $infoHash{'FileSize'};
	my $imWidth = $infoHash{'ImageWidth'};
	my $imHeight = $infoHash{'ImageHeight'};

	if ($imWidth < $minResX || $imHeight < $minResY){
		print "Insufficient Resolution!\n";
		# exit;
		return $returnData;
	}

	$elapsed = tv_interval ( $t0 );
	# print $elapsed . "\n";

	# foreach my $k (keys %infoHash){
	# 	print "$k\n";#; $infoHash{$k}\n";
	# }

	$elapsed = tv_interval ( $t0 );
	# print $elapsed . "\n";

	#print $namelist . "\n";
	my @names = split(',', $namelist);
	my @widths = split(',', $regionWidth);
	my @heights = split(',', $regionHeight);

	my %seenFaces; # Hash for de-duplication.
	my @namesWithLargeAreas; 

	for (my $i = 0; $i < scalar @names; $i++){
		# Gets the names, widths, and heights of the faces. Calculate the area as
		# a proportion of the image. 
		my $name = $names[$i];
		trim($name);
		my $width = $widths[$i];
		trim($width);
		my $height = $heights[$i];
		trim($height);
		my $area = $width * $height;

		if ($params::debug and $params::debug_readXMP) {print $name . "  " . $area . "\n"; }

		if (exists $seenFaces{$name}){
			# If the name is already in a hash, do this:
			# 1) Evaluate if we've already found a region with this face that's larger
			# than $minSize. If so, we're done. 
			if ($params::debug and $params::debug_readXMP) {print "Seen in the hash" . "\n"; }
			my $storedArea = $seen{$name};
			if ($storedArea > $minSize){
				# Do nothing; we've found a big enough area already. 
				next;
			}else{
				# If we haven't found a large enough area, update the largest seen area. 
				# If the area is now large enough, add the name to the deduplicated list
				# of appreciably sized faces. Otherwise, don't bother even updating the 
				# seen area size, because it doesn't really matter. 
				if ($area > $storedArea){
					$seen{$name} = $area;
					if ($area > $minSize){
						push(@namesWithLargeAreas, $name);
					}
					next;
				}else{
					next;
				}
			}
		}else{
			# If we haven't seen the name yet, add it to the hash. If 
			# the area is large enough, push the name to the list 
			# of acceptably-sized faces. 
			if ($params::debug and $params::debug_readXMP) { print "Adding to the hash" . "\n"; }
			$seen{$name} = $area;
			if ($area > $minSize){
				push(@namesWithLargeAreas, $name);
			}
		}

		# Output of this for loop: A de-duplicated list of faces
		# with a size above $minSize. 
	}

	# Other info: Orientation

	$returnData{'NameList'} = \@namesWithLargeAreas;

	if ($params::debug and $params::debug_readXMP) {print join (",", @namesWithLargeAreas); }

	$returnData{'ImageSize'} = $fileSize;
	$returnData{'Width'} = $imWidth;
	$returnData{'Height'} = $imHeight;

	# Remove the time zone from the modify and taken dates. 
	$modifyDate =~ s/[+-]\d\d:\d\d$//g;
	$takenDate =~ s/[+-]\d\d:\d\d$//g;
	# Make the dates follow a YYYY-MM-DD hh:mm:ss pattern
	$modifyDate =~ s/(.*?):(.*?):(.*?) /$1-$2-$3 /g;
	$takenDate =~ s/(.*?):(.*?):(.*?) /$1-$2-$3 /g;

	$returnData{'ModifyDate'} = $modifyDate;
	$returnData{'TakenDate'} = $takenDate;

	$returnData{'Year'} = $year;
	$returnData{'Month'} = $month;
	$returnData{'Day'} = $day;
	$returnData{'Hour'} = $hh;
	$returnData{'Minute'} = $mm;
	$returnData{'Second'} = $ss;
	$returnData{'TimeZone'} = $zone / 3600;
	$returnData{'Status'} = 1;

	return %returnData;

};

sub trim { 
	# Modify the string passed in as a scalar
	# Strip leading and trailing spaces of any form. 
	$_[0] =~ s/^\s+|\s+$//g; 
};

1; # Required if the script is included in another script. (/'require'd)