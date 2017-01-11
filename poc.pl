#! /usr/bin/perl

use Data::Dumper;
use Date::Parse;

require 'poc2.pl';

# my %hash;

# $hash{'1'} = 'test';
# $hash{'ab'} = 't2';

# runTest(\%hash);

# print Dumper(%hash);

# my ($sec,$min,$hour,$mday,$mon,$year) = localtime(time);
# $year += 1900;
# $mon += 1;

# print $mday . "  " . $hour . "\n";

# my $date = sprintf("%04d:%02d:%02d %02d:%02d:%02d", $year, $mon, $mday, $hour, $min, $sec);

# print $date . "\n";

my $str = "foo_bar_not_needed_string_part_123";
$str =~ s/(foo_bar_).*?(_\d+)/$1$2/;
print $str;