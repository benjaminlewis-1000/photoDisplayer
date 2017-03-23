use strict; 
use warnings;

use threads;
use threads::shared;

my $current :shared;
$current = 0;

my @threads = (threads->new(\&process, 0), threads->new(\&process2, 1) ) ;
$_->join for @threads;

sub process {
    my ($thr) = @_;
    warn "thread $thr started\n";

    for (my $i = 0; $i < 1e2; $i++) {
    	print "hi from $thr\n";
    }
    warn "thread $thr closed\n";
}

sub process2 {
    my ($thr) = @_;
    warn "thread $thr started\n";

    for (my $i = 0; $i < 1e2; $i++) {
    	print "hi from $thr\n";
    }
    warn "thread $thr closed\n";
}