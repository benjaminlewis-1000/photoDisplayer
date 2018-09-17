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


# People table parameters
peopleTableName = params['params']['photoDatabase']['tables']['peopleTable']['Name']
peopleKeyColumn = params['params']['photoDatabase']['tables']['peopleTable']['Columns']['peopleKey']
personNameColumn = params['params']['photoDatabase']['tables']['peopleTable']['Columns']['personName']

# Linker table parameters
linkerTable = params['params']['photoDatabase']['tables']['photoLinkerTable']
linkerTableName = linkerTable['Name']
linkerPhotoColumn = linkerTable['Columns']['linkerPhoto']
linkerPeopleColumn = linkerTable['Columns']['linkerPeople']

# Root table parameters
rootTableName = params['params']['photoDatabase']['tables']['rootTable']['Name']
rootKeyColumn = params['params']['photoDatabase']['tables']['rootTable']['Columns']['rootKey']
windowsRootPath = params['params']['photoDatabase']['tables']['rootTable']['Columns']['windowsRootPath']
linuxRootPath = params['params']['photoDatabase']['tables']['rootTable']['Columns']['linuxRootPath']

# Metadata table parameters
metadataTableName = params['params']['photoDatabase']['tables']['metadataTable']['Name']
metadataNameColumn = params['params']['photoDatabase']['tables']['metadataTable']['Columns']['metadataName']
metadataValueColumn = params['params']['photoDatabase']['tables']['metadataTable']['Columns']['metadataValue']
metadataLastEditedField = params['params']['photoDatabase']['tables']['metadataTable']['Fields']['metadataLastEditedField']

# Master table of comments/tags -- for deduplication
masterCommentTableName = params['params']['photoDatabase']['tables']['masterComments']['Name']
masterCommentTagIDNum = params['params']['photoDatabase']['tables']['masterComments']['Columns']['tagID']
masterCommentTagString = params['params']['photoDatabase']['tables']['masterComments']['Columns']['tagString']

# Comment linker table parameters -- user
commentLinkerUserTableName = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['Name']
commentLinkerPhotoColumnUser = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['Columns']['commentLinkerPhoto']
commentLinkerTagColumnUser = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['Columns']['commentLinkerTagIDlink']
commentLinkerTagProbabilityColumnUser = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['Columns']['commentLinkerTagProbability']

# Comment linker table parameters -- machine generated 
commentLinkerMachineTableName = params['params']['photoDatabase']['tables']['machineCommentLinker']['Name']
commentLinkerPhotoColumnMachine = params['params']['photoDatabase']['tables']['machineCommentLinker']['Columns']['commentLinkerPhoto']
commentLinkerTagColumnMachine = params['params']['photoDatabase']['tables']['machineCommentLinker']['Columns']['commentLinkerTagIDlink']
commentLinkerTagProbabilityColumnMachine = params['params']['photoDatabase']['tables']['machineCommentLinker']['Columns']['commentLinkerTagProbability']

# commentLinkerGoogleTableName = params['params']['photoDatabase']['tables']['commentLinkerGoogleTable']['Name']
# commentLinkerPhotoColumnGoogle = params['params']['photoDatabase']['tables']['commentLinkerGoogleTable']['Columns']['commentLinkerPhoto']
# commentLinkerTagColumnGoogle = params['params']['photoDatabase']['tables']['commentLinkerGoogleTable']['Columns']['commentLinkerTag']
# commentLinkerTagProbabilityColumnGoogle = params['params']['photoDatabase']['tables']['commentLinkerGoogleTable']['Columns']['commentLinkerTagProbability']

# commentLinkerClarifaiTableName = params['params']['photoDatabase']['tables']['commentLinkerClarifaiTable']['Name']
# commentLinkerPhotoColumnClarifai = params['params']['photoDatabase']['tables']['commentLinkerClarifaiTable']['Columns']['commentLinkerPhoto']
# commentLinkerTagColumnClarifai = params['params']['photoDatabase']['tables']['commentLinkerClarifaiTable']['Columns']['commentLinkerTag']
# commentLinkerTagProbabilityColumnClarifai = params['params']['photoDatabase']['tables']['commentLinkerClarifaiTable']['Columns']['commentLinkerTagProbability']



# Photo table Parameters
photoTableParams = params['params']['photoDatabase']['tables']['photoTable']
phtp = photoTableParams # shorter, but I want it to be clear what it means. 

photoTableName = phtp['Name']
photoTableColumns = phtp['Columns']
phtc = photoTableColumns

photoKeyColumn = phtc['photoKey']
photoFileColumn = phtc['photoFile']
photoDateColumn = phtc['photoDate']

photoYearColumn = phtc['photoYear']
photoMonthColumn = phtc['photoMonth']
photoDayColumn = phtc['photoDay']
photoHourColumn = phtc['photoHour']
photoMinuteColumn = phtc['photoMinute']
photoGMTColumn = phtc['photoGMT']

modifyDateColumn = phtc['modifyDate']
insertDateColumn = phtc['insertDate']
rootDirNumColumn = phtc['rootDirNum']

houseNumColumn = phtc['houseNum']
streetColumn = phtc['street']
cityColumn = phtc['city']
stateColumn = phtc['state']
postcodeCoulumn = phtc['postcode']
countryColumn = phtc['country']
latColumn = phtc['lat']
longColumn = phtc['long']
# End photo table parameters



def connectDB(params):

    dbName = params['params']['photoDatabase']['fileName']

    conn = sqlite3.connect(os.path.join(project_path, 'databases', dbName))
    conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")
    return conn

def dropTables(conn):
    """ create a database connection to a SQLite database """
    cc = conn.cursor()
    dropPhotos = 'DROP TABLE IF EXISTS ' + photoTableName
    cc.execute(dropPhotos)

    dropPeople = 'DROP TABLE IF EXISTS ' + peopleTableName
    cc.execute(dropPeople)

    dropLinker = 'DROP TABLE IF EXISTS ' + linkerTableName
    cc.execute(dropLinker)

    dropRootDirs = 'DROP TABLE IF EXISTS ' + rootTableName
    cc.execute(dropRootDirs)

    dropMetadata = 'DROP TABLE IF EXISTS ' + metadataTableName
    cc.execute(dropMetadata)

    dropCommentLinker = 'DROP TABLE IF EXISTS ' + commentLinkerUserTableName
    cc.execute(dropCommentLinker)

    dropCommentLinker = 'DROP TABLE IF EXISTS ' + commentLinkerMachineTableName
    cc.execute(dropCommentLinker)

    # Must be dropped after the comment linker child tables. 
    dropCommentLinker = 'DROP TABLE IF EXISTS ' + masterCommentTableName
    cc.execute(dropCommentLinker)

    conn.commit()

# # Create the photo primary key and filename table
def create_photo_table(conn):
    # Create the database table, where photo_key is the primary key and photo_file is the file name


    sql_quer = 'CREATE TABLE ' + \
        photoTableName + '(' + \
        photoKeyColumn + '  INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, ' + \
        photoFileColumn + ' STRING, ' + \
        photoDateColumn + ' STRING, ' + \
                                        \
        photoYearColumn + ' STRING, ' + \
        photoMonthColumn + ' STRING, ' + \
        photoDayColumn + ' STRING, ' + \
        photoHourColumn + ' STRING, ' + \
        photoMinuteColumn + ' STRING, ' + \
        photoGMTColumn + ' STRING, ' + \
                                        \
        modifyDateColumn + ' STRING, ' + \
        insertDateColumn + ' STRING, ' + \
        rootDirNumColumn + ' STRING, ' + \
                                        \
        houseNumColumn + ' STRING, ' + \
        streetColumn + ' STRING, ' + \
        cityColumn + ' STRING, ' + \
        stateColumn + ' STRING, ' + \
        postcodeCoulumn + ' STRING, ' + \
        countryColumn + ' STRING, ' + \
        latColumn + ' STRING, ' + \
        longColumn + ' STRING ); '

    c = conn.cursor()
    c.execute(sql_quer)
    conn.commit()

# Create the people table
def create_people_table(conn):
    

    # Create the database table, where photo_key is the primary key and photo_file is the file name 
    sql_quer = 'CREATE TABLE ' + peopleTableName + ' ( ' + \
        peopleKeyColumn + ' INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, ' + \
        personNameColumn + ' STRING  );'

    c = conn.cursor()
    c.execute(sql_quer)
    conn.commit()

    ben_query = 'INSERT INTO ' + peopleTableName + '(' + personNameColumn + ') VALUES ("Benjamin Lewis");'
    jessica_query = 'INSERT INTO ' + peopleTableName + '(' + personNameColumn + ') VALUES ("Jessica Lewis");'

    c.execute(ben_query)
    c.execute(jessica_query)
    conn.commit()

# Create the linkage table
def create_linker_table(conn):


    sql_quer = 'CREATE TABLE ' + linkerTableName + ' ( ' + \
        linkerPhotoColumn  + ' INTEGER REFERENCES ' + photoTableName + ' ( ' + photoKeyColumn  + ' ), ' + \
        linkerPeopleColumn + ' INTEGER REFERENCES ' + peopleTableName + ' ( ' + peopleKeyColumn  + ' ) );'

    c = conn.cursor()
    c.execute(sql_quer)
    conn.commit()

def create_root_dir_table(conn):
    sql_quer = 'CREATE TABLE ' + rootTableName + ' ( ' \
        + rootKeyColumn + ' INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, ' \
        + windowsRootPath + ' STRING, ' \
        + linuxRootPath + ' STRING ); ' 
     
    c = conn.cursor()
    c.execute(sql_quer)
    conn.commit()


def create_metadata_table(conn):
    sql_quer = 'CREATE TABLE ' + metadataTableName + ' ('\
        + metadataNameColumn + '  STRING,  '\
        + metadataValueColumn + ' STRING);'

    c = conn.cursor()
    c.execute(sql_quer)
    conn.commit()

def create_comments_table(conn):


# # Master table of comments/tags -- for deduplication
# masterCommentTableName = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['masterComments']['Name']
# masterCommentTagIDNum = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['masterComments']['Columns']['tagID']
# masterCommentTagString = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['masterComments']['Columns']['tagString']

# # Comment linker table parameters -- user
# commentLinkerUserTableName = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['Name']
# commentLinkerPhotoColumnUser = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['Columns']['commentLinkerPhoto']
# commentLinkerTagColumnUser = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['Columns']['commentLinkerTagIDlink']
# commentLinkerTagProbabilityColumnUser = params['params']['photoDatabase']['tables']['commentLinkerUserTable']['Columns']['commentLinkerTagProbability']

# # Comment linker table parameters -- machine generated 
# commentLinkerMachineTableName = params['params']['photoDatabase']['tables']['machineCommentLinker']['Name']
# commentLinkerPhotoColumnMachine = params['params']['photoDatabase']['tables']['machineCommentLinker']['Columns']['commentLinkerPhoto']
# commentLinkerTagColumnMachine = params['params']['photoDatabase']['tables']['machineCommentLinker']['Columns']['commentLinkerTagIDlink']
# commentLinkerTagProbabilityColumnMachine = params['params']['photoDatabase']['tables']['machineCommentLinker']['Columns']['commentLinkerTagProbability']

    sql_quer = 'CREATE TABLE ' + masterCommentTableName + ' (' + \
        masterCommentTagIDNum + '  INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, ' + \
        masterCommentTagString + ' STRING);'

    c = conn.cursor()
    c.execute(sql_quer)
    conn.commit()


    sql_quer = 'CREATE TABLE ' + commentLinkerUserTableName + ' (' + \
        commentLinkerPhotoColumnUser + ' INTEGER REFERENCES ' + photoTableName + ' ( ' + photoKeyColumn + '), ' + \
        commentLinkerTagColumnUser + ' INTEGER REFERENCES  ' + masterCommentTableName + ' ( ' + masterCommentTagIDNum + '), ' + \
        commentLinkerTagProbabilityColumnUser + ' DOUBLE);'
    
    c.execute(sql_quer)
    conn.commit()


    sql_quer = 'CREATE TABLE ' + commentLinkerMachineTableName + ' (' + \
        commentLinkerPhotoColumnMachine + ' INTEGER REFERENCES ' + photoTableName + ' ( ' + photoKeyColumn + '), ' + \
        commentLinkerTagColumnMachine + ' INTEGER REFERENCES  ' + masterCommentTableName + ' ( ' + masterCommentTagIDNum + '), ' + \
        commentLinkerTagProbabilityColumnMachine + ' DOUBLE);'
    
    c.execute(sql_quer)
    conn.commit()


def update_metadata(conn):

    # (year, month, day, hour, minute, second, wday, yearday, isdst) = time.localtime()

    # my $dateTime = sprintf("%04d-%02d-%02d %02d:%02d:%02d", $year, $mon, $mday, $hour, $min, $sec);
    dateTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    updatedValQuery = 'INSERT INTO ' + metadataTableName + ' VALUES ("' + metadataLastEditedField + '", "' + dateTime + '")'

    c = conn.cursor()
    c.execute(updatedValQuery)
    conn.commit()


conn = connectDB(params)
dropTables(conn)
create_photo_table(conn)
create_people_table(conn)
create_linker_table(conn)
create_root_dir_table(conn)
create_metadata_table(conn)
create_comments_table(conn)

update_metadata(conn)
