
use Data::Dumper;

sub runTest{
	our $hash = $_[0];

	# print Dumper(%{$hash});

	$_[0]->{'e'} = "tesing";

};

1;