#! /usr/bin/perl

# Read the XMP data from a file.

use Image::Magick;
use Image::ExifTool qw(ImageInfo);
use Time::HiRes qw( usleep gettimeofday tv_interval  );
use Date::Parse;
use params;
use Data::Dumper;

# use Image::EXIF;

use warnings;
use strict; 

# getImageData({
# # 	filename => "C:\\Users\\Benjamin\\Dropbox\\Perl Code\\photoDisplayer\\base\\canon pictures 018.JPG",
# 	filename => "/home/lewis/Pictures/Soph-Junior Years/theWard2.jpg",
# 	debug => 1
# 	});

sub getImageData{
	my $d = 0;

	my $sttime = [gettimeofday];

	my ($args) = @_;
	our %returnData;
	$returnData{'Status'} = 0;

	if (! defined $args->{filename}){
		print "Error: File not passed\n";
		return %returnData;
	}

	if (! defined $args->{resX}){
		$args->{resX} = 0;
	}

	if (! defined $args->{resY}){
		$args->{resY} = 0;
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

	if ($params::debug and $params::debug_readXMP ) { print "Minimum size is: " . $args->{minSize} . "\n"; print $args->{filename} . "\n"; }

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

	# $elapsed = tv_interval($sttime);
	# print "Elapsed adgh" . $d++ . ": " . $elapsed . "\n";

	my $exif = Image::ExifTool->new();
	# $elapsed = tv_interval($sttime);
	# print "Elapsed asd " . $d++ . ": " . $elapsed . "\n";

	my $info = ImageInfo($file);
	# $elapsed = tv_interval($sttime);
	# print "Elapsed adhjfsef " . $d++ . ": " . $elapsed . "\n";
	my %infoHash = %$info;

	# print ref( $exif->ImageInfo($file) ) . "\n\n";

	delete $infoHash{"ThumbnailImage"};
	# print Dumper %infoHash;

	# print $elapsed . "\n";
	if ($params::debug and $params::debug_readXMP ) {
		foreach my $k (keys %infoHash){
			if ($k =~ m/date/i){
				print $k . " : " . $infoHash{$k} . "\n";
			}
		}
	}
	# Parse the XMP data. 

	my $namelist = $infoHash{'RegionName'};
	my $regionWidth = $infoHash{'RegionAreaW'};
	my $regionHeight = $infoHash{'RegionAreaH'};

    my $takenDate;
    my $modifyDate;
    if ( $params::OS_type == $params::windowsType ){
        $takenDate = $infoHash{'FileCreateDate'};
		$modifyDate = $infoHash{'FileModifyDate'};
    }else{
        $takenDate = $infoHash{'CreateDate'};
        if (!defined $takenDate or  $infoHash{'CreateDate'} !~ m/\d/ ){  # No numeric
        	undef $takenDate;
        	if ( $infoHash{'CreateDate (1)'} ){  # Alt
        		$takenDate = $infoHash{'CreateDate (1)'};
        	}
        }
        $modifyDate = $infoHash{'ModifyDate'};
        if (!defined $modifyDate or $infoHash{'ModifyDate'} !~ m/\d/ ){  # No numeric
        	undef $modifyDate;
        	if ( $infoHash{'FileModifyDate'} ){  # Alt
        		$modifyDate = $infoHash{'FileModifyDate'};
        	}
        }

         # Because of course windows and linux have to do perl, which is system agnostic, differently. Actually, it's probably more of an underlying XMP representation problem.
        
    }

    if (!defined $takenDate){
    	$takenDate = "1969:01:01 00:00:00-00:00";
    }


	# my $elapsed = tv_interval($sttime);
	# print "Elapsed " . $d++ . ": " . $elapsed . "\n";

	# Parse the date. 

    # print "Taken on: " . $takenDate . "\n";
	our ($ss, $mm, $hh, $day, $month, $year, $zone);
	my $time = str2time($takenDate);
	($ss, $mm, $hh, $day, $month, $year, $zone) = strptime($takenDate);
	$year += 1900;
	$month += 1;
	# print $takenDate . "\n";
	# print $year . " , " .  $day . " , " . $month . "\n";
	

	my $fileSize = $infoHash{'FileSize'};
	my $imWidth = $infoHash{'ImageWidth'};
	my $imHeight = $infoHash{'ImageHeight'};

	# $elapsed = tv_interval($sttime);
	# print "Elapsed " . $d++ . ": " . $elapsed . "\n";

	if ($imWidth < $minResX || $imHeight < $minResY){
		print "Insufficient Resolution!\n";
		# exit;
		return %returnData;
	}

	# print $elapsed . "\n";

	# foreach my $k (keys %infoHash){
	# 	print "$k\n";#; $infoHash{$k}\n";
	# }


	my (@names, @widths, @heights);
	if (defined $namelist){
		@names = split(',', $namelist);
		@widths = split(',', $regionWidth);
		@heights = split(',', $regionHeight);
	}


	my %seenFaces; # Hash for de-duplication.
	my @namesWithLargeAreas; 

	for (my $i = 0; $i < scalar @names; $i++){
		# Gets the names, widths, and heights of the faces. Calculate the area as
		# a proportion of the image. 
		my $name = $names[$i];
		trim($name);

		# Capitalize the first letter of each name, and preserve irish-type names like O'Whatever. Just because. 
		$name =~ s/((?<!\')[a-zA-Z'\s,])/\L$1/g;
		$name =~ s/([A-Za-z']+)/\u$1/g;
		# print $name . "\n";

		my $width = $widths[$i];
		trim($width);
		my $height = $heights[$i];
		trim($height);
		my $area = $width * $height;

		if ($params::debug and $params::debug_readXMP) {print $name . "  " . $area . "\n"; }

		my %seen;

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

	# print Dumper(@namesWithLargeAreas) . "\n";

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
    if (!defined $zone){
        $zone = 0;
    }
	$returnData{'TimeZone'} = $zone / 3600;
	$returnData{'Status'} = 1;


	# $elapsed = tv_interval($sttime);
	# print "Elapsed: " . $elapsed . "\n";

	return %returnData;

};

sub trim { 
	# Modify the string passed in as a scalar
	# Strip leading and trailing spaces of any form. 
	$_[0] =~ s/^\s+|\s+$//g; 
};

1; # Required if the script is included in another script. (/'require'd)