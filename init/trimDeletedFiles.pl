#! /usr/bin/perl

use params;
use DBI;

use warnings;
use strict;

require 'read_xmp.pl';
require 'readInImages.pl';
require 'filesFromBaseFinder.pl';

trimDeletedFiles();

sub trimDeletedFiles {

    print "Trimming files..." . "\n";
    our @rootDirList;

    # Open the database
    our $dbhandle
        = DBI->connect( "DBI:SQLite:$params::database", "user", "pass" );

    # Get a list of all the root directories and their key columns.
    my $rootDirQuery
        = qq/SELECT $params::rootKeyColumn, $params::rootDirPath FROM $params::rootTableName/;
    my $query = $dbhandle->prepare($rootDirQuery);
    until ( $query->execute() ) {
        warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
        warn "Failed on the following query: $rootDirQuery\n";
        sleep(5);
    }    # or die $DBI::errstr;

    # Bind the columns to given variables.
    our ( $rootKey, $root_dir );
    $query->bind_col( 1, \$rootKey );
    $query->bind_col( 2, \$root_dir );

    # Associate the root key value and the root directory using a hash.
    our %rootHash;

    while ( $query->fetch ) {
        $rootHash{$rootKey} = $root_dir;
    }

    my $allFilesQuery
        = qq/SELECT $params::photoFileColumn, $params::rootDirNumColumn, $params::photoKeyColumn FROM $params::photoTableName/;
    $query = $dbhandle->prepare($allFilesQuery);
    until ( $query->execute() ) {
        warn "Can't connect: $DBI::errstr. Pausing before retrying.\n";
        warn "Failed on the following query: $allFilesQuery\n";
        sleep(5);
    }    # or die $DBI::errstr;

    our ( $fileName, $rootDirNum, $photoKey );
    $query->bind_col( 1, \$fileName );
    $query->bind_col( 2, \$rootDirNum );
    $query->bind_col( 3, \$photoKey );

    our $numProcessed = 0;
    while ( $query->fetch ) {
        $numProcessed += 1;
        if ( $numProcessed % 500 == 0 ) {
            print "We have processed $numProcessed files while trimming."
                . "\n";
        }
        my $file = $rootHash{$rootDirNum} . $fileName;
        if ( !-e $file ) {
            print $file . " does not exist. Trimming." . "\n";

            my $unlinkQuery
                = qq/DELETE FROM $params::linkerTableName WHERE $params::linkerPhotoColumn = $photoKey/;
            my $query = $dbhandle->prepare($unlinkQuery);
            until ( $query->execute() ) {
                warn
                    "Can't connect: $DBI::errstr. Pausing before retrying.\n";
                warn "Failed on the following query: $unlinkQuery\n";
                sleep(5);
            }    # or die $DBI::errstr;

            my $deletePhotoQuery
                = qq/DELETE FROM $params::photoTableName WHERE $params::photoFileColumn = "$fileName" AND $params::rootDirNumColumn = $rootDirNum/;
            $query = $dbhandle->prepare($deletePhotoQuery);
            until ( $query->execute() ) {
                warn
                    "Can't connect: $DBI::errstr. Pausing before retrying.\n";
                warn "Failed on the following query: $deletePhotoQuery\n";
                sleep(5);
            }    # or die $DBI::errstr;
        }
    }

}

1;
