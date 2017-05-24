#! /usr/bin/perl


my $time = localtime;
open OUTPUT, ">>test.txt";
print OUTPUT "$time\n";
close OUTPUT;
