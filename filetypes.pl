#! /usr/bin/perl

use File::Find;

if (0){
	my $baseFile = 'D:\Pictures\Mission\Penedo 6.04';

	my $fileList = 'files2.txt';
	open (OUT, '>', $fileList);

	my @files;
	find( { wanted => sub { push @files, $_ }, no_chdir => 1 }, $baseFile );

	print scalar @files . "\n";
	print "\n";

	print OUT join ("\n", @files);

	my %extensions;

	for (my $i = 0; $i < scalar @files; $i++){
		# Get file extensions; don't include file paths. 
		# Part of string, after a period
		# Must have alphabetic characters
		# May not have \ / . or !
		$files[$i] =~ /\.([a-zA-Z][^\.!\\]+$)/;
		my $fileExtension = $1;
		# print $1 . " ";
		$extensions{$1}++;
	}

}else{

	open (my $fh, "files.txt");

	while (my $row = <$fh>){
		trim($row);
		$row =~ /\.([a-zA-Z][^\.!\\]+$)/;
		my $fileExtension = $1;
		# print $1 . " ";
		$extensions{$1}++;
	}

}

open (TYPES, '>', 'extensions.txt');

foreach my $k (keys %extensions){
	print TYPES $k . "  ";
	print $k . "  ";
}

print "\n";

sub trim { 
	# Modify the string passed in as a scalar
	# Strip leading and trailing spaces of any form. 
	$_[0] =~ s/^\s+|\s+$//g; 
};