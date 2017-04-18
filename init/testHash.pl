#! /usr/bin/perl

my %hashA;
$hashA{'one'} = 2;

my %hashB;
$hashB{'tw'} = 4;

my %hashC;
$hashC{'th'} = 6;

my @AoH = (\%hashA, \%hashB, \%hashC);

print join(',', @AoH) . "\n";
print %hashC . "\n";

print scalar  @AoH . "\n";
my $numKeys = 3;

print 'here: ' . %hashC . "\n";

for (my $i = 0; $i < $numKeys; $i++){
	my %keyHash = %$AoH[$i];
	print %keyHash . "\n";
	print "ok" . "\n";
}