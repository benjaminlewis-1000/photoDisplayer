#!/usr/bin/perl 

 use strict;
 use warnings;
 use Frontier::Client;
 
 my $url  = "http://127.0.0.1:8000/RPC2";
 my @args = (40.23384, -111.65853);
 
 my $client = Frontier::Client->new( url   => $url,
                     debug => 0,
                   );
my $res = 'undef';

while ($res =~ 'undef'){
	print "effort:\n";
	eval{
		$res = $client->call('geoLookup', @args) ;
	};
}



print "res: " . $res . "\n";