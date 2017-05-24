#! /usr/bin/perl

use DBI;
use Cwd;

my $dir = "/mnt/NAS/Photos/Mission/Pickup";

$dbhandle = DBI->connect("dbi:SQLite:tmp.db", "user" , "pass");

my $tname = "tableTEST";
my $col = "colname";

	my $dropPhotos = qq/DROP TABLE IF EXISTS $tname/;
	my $query = $dbhandle->prepare($dropPhotos);
	$query->execute() or die $DBI::errstr;

my $sql_quer = qq/CREATE TABLE $tname(
	    $col STRING
	); /;
	
	my $sub_state_handle = $dbhandle->prepare($sql_quer);
	$sub_state_handle->execute() or die $DBI::errstr;

    opendir (DIR, $dir) or die $!;
 while (my $file = readdir(DIR)) {

        print "$file\n";
   my $quer = qq/INSERT INTO $tname ($col) VALUES ("$file")/;
   my $hh = $dbhandle->prepare($quer);
   $hh->execute() or die $DBI::errstr;

    }


my $rquer = qq/SELECT * FROM $tname/;

my $rtmp = $dbhandle->prepare($rquer);
$rtmp->execute();

while ( my ($field1) = $rtmp->fetchrow_array() ) {
     print STDOUT "Field 1: $field1\n";
}


