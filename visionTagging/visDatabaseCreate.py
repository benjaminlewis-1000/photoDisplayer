#! /usr/bin/env python

import sqlite3
from sqlite3 import Error
import os
import xmltodict
import time

project_path = os.path.abspath(os.path.join(__file__,"../.."))
script_path  = os.path.abspath(os.path.join(__file__,".."))

with open(os.path.join(project_path, 'config/params.xml') ) as stream:
    try:
        params = xmltodict.parse(stream.read())
    except Exception as exc:
        print(exc)
        exit(1)



# my $visionBase = $config->{'visionTaggingParams'}->[0];

# our $dbhandle;
# our $dbName = $visionBase->{'database'}->[0]->{'fileName'}->[0];

# my $count_args = @ARGV ;

# if ($count_args == 1) {
#     my $db = $ARGV[0];
#     if ($db =~ /db$/){
#         print "valid";
#         $dbName = $db;
#     }
# }
visionDBParamBase = params['params']['visionTaggingParams']['database']

def connectDB(params):

    visionDBfile = params['params']['visionTaggingParams']['database']['fileName']

    conn = sqlite3.connect(os.path.join(project_path, 'databases', visionDBfile) )
    conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")
    return conn

recordDataTableName = visionDBParamBase['tables']['recordDataTable']['Name']
visionMetaTableName = visionDBParamBase['tables']['visionMetaTable']['Name']

def dropTables(conn):
    # Clean out the old tables so we can create them afresh.
    # tableBase = $visionBase->{'database'}->[0]->{'tables'}->[0];
    dropPhotos = 'DROP TABLE IF EXISTS ' + recordDataTableName

    c = conn.cursor()
    c.execute(dropPhotos)
    conn.commit()


    dropMetadata = 'DROP TABLE IF EXISTS ' + visionMetaTableName
    
    c = conn.cursor()
    c.execute(dropMetadata)
    conn.commit()
    
def createLoggingTable(conn):
    # Create the database table, where photo_key is the primary key and photo_file is the file name 
    recordBase = visionDBParamBase['tables']['recordDataTable']
    logTableCreate = 'CREATE TABLE ' + recordBase['Name'] + ' (' + \
            recordBase['Columns']['File'] + ' STRING, ' + \
            recordBase['Columns']['Checked'] + ' STRING, ' + \
            recordBase['Columns']['Portrait'] + ' BOOL, ' + \
            recordBase['Columns']['Source'] + ' STRING, ' + \
            recordBase['Columns']['Valid'] + ' BOOL); '

    c = conn.cursor()
    c.execute(logTableCreate)
    conn.commit()

def createMetadataTable(conn):
    metaBase = visionDBParamBase['tables']['visionMetaTable']
    metadataCreate = 'CREATE TABLE ' + metaBase['Name'] + ' ( ' + \
        metaBase['Columns']['NameColumn'] + ' STRING, ' + \
        metaBase['Columns']['ValueColumn'] + ' STRING );' 

    c = conn.cursor()
    c.execute(metadataCreate)
    conn.commit()


def populateMetadataTable(conn):

    (year, month, day, hour, minute, second, wday, yearday, isdst) = time.localtime()

    # my $newMonth = "$year-$month-$day";
    newMonth = time.strftime('%Y-%m-%d', time.localtime())

    print newMonth

    googFieldsBase = visionDBParamBase['Fields']['googFields'];
    clarifaiFieldsBase = visionDBParamBase['Fields']['clarifaiFields']
    metaBase = visionDBParamBase['tables']['visionMetaTable']

    populateQuery = 'INSERT INTO ' + metaBase['Name'] + \
        ' ( "' + metaBase['Columns']['NameColumn']  + '" , ' + metaBase['Columns']['ValueColumn'] + ') VALUES ' + \
        ' ( "' + clarifaiFieldsBase['ReadsThisMonth'] + '" , 0),'  + \
        ' ( "' + clarifaiFieldsBase['ReadsPerMonth'] + '" , 5000),' + \
        ' ( "' + clarifaiFieldsBase['NewMonthDate'] + '" , "' + str(newMonth) + '"), ' + \
        ' ( "' + clarifaiFieldsBase['DayLastRead'] + '" , "' + str(newMonth) + '"), ' + \
        ' ( "' + clarifaiFieldsBase['DayOfNewMonth'] + '" , ' + str(day) + '), ' + \
        ' ( "' + googFieldsBase['ReadsThisMonth'] + '" , 0), ' + \
        ' ( "' + googFieldsBase['ReadsPerMonth'] + '" , 10000), ' + \
        ' ( "' + googFieldsBase['NewMonthDate'] + '" , "' + str(newMonth) + '"), ' + \
        ' ( "' + googFieldsBase['DayLastRead'] + '" , "' + str(newMonth) + '"), ' + \
        ' ( "' + googFieldsBase['DayOfNewMonth'] + '" , ' + str(day) + '); '

    print populateQuery

    c = conn.cursor()
    c.execute(populateQuery)
    conn.commit()


conn = connectDB(params)
dropTables(conn)
createLoggingTable(conn)
createMetadataTable(conn)
populateMetadataTable(conn)


# End creation of tables.
