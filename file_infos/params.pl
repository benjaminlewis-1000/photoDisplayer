# Package 

#! /usr/bin/perl

package params;

use strict;
use warnings;
use Exporter;

our @EXPORT = qw(photoTableName peopleTableName linkerTableName);

## Table names
our $photoTableName = "Photos";
our $peopleTableName = "People";
our $linkerTableName = "Linker";


1;