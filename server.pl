#!/usr/bin/perl
 # sum() server
 
 use strict;
 use warnings;
 use Frontier::Daemon;
 
 my $d = Frontier::Daemon->new(
                   methods => {
                       sum => \&sum,
                      },
                   LocalAddr => '127.0.0.1',
                   LocalPort => 8000,
                   );
 
 sub sum {
   my ($arg1, $arg2) = @_;
 
   return $arg1 + $arg2;
 }