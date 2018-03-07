#! /usr/bin/env python
import os
import sqlite3
import xmltodict

def insertName(name, conn, photoKeyID, params, nameDict):
    c = conn.cursor()

    if name in nameDict:
        print nameDict[name]

    else:

        photoTableName = params['params']['photoDatabase']['tables']['photoTable']['Name']
        photoCols = params['params']['photoDatabase']['tables']['photoTable']['Columns']
        photoKeyCol = photoCols['photoKey']

        personTableName = params['params']['photoDatabase']['tables']['peopleTable']['Name']
        personKeyCol = params['params']['photoDatabase']['tables']['peopleTable']['Columns']['peopleKey']
        personNameCol = params['params']['photoDatabase']['tables']['peopleTable']['Columns']['personName']

        # TODO: Name in UTF-8
        utf_name = unicode(name, "utf-8")
        ## Check if the person exists
        personExistsQuery = '''SELECT {} FROM {} WHERE {} = ?'''.format(personKeyCol, personTableName, personNameCol)

        c.execute(personExistsQuery, (utf_name,))

        row = c.fetchone()

        if row != None:
            print "found"
            personID = row[0]
            # Sanity check - make sure only one person has that name in the database
            numPeopleQuery = '''SELECT COUNT(*) FROM {} WHERE {} = ?'''.format(personTableName, personNameCol)
            c.execute(numPeopleQuery, (utf_name,))
            numRow = c.fetchone()
            assert numRow[0] == 1
            nameDict[name] = personID

        else:
            print "not found"
            newPersonQuery = '''INSERT INTO {} ({}) VALUES (?)'''.format(personTableName, personNameCol)
            c.execute(newPersonQuery, (utf_name,))
            conn.commit()
            personID = c.lastrowid
            nameDict[name] = personID

    print personID

if __name__ == '__main__':

    project_path = os.path.abspath(os.path.join(__file__,"../.."))
    script_path  = os.path.abspath(os.path.join(__file__,".."))
    ## Open the params.xml file for the configuration parameters
    with open(os.path.join(project_path, 'config/params.xml') ) as stream:
        try:
            params = xmltodict.parse(stream.read())
        except Exception as exc:
            print(exc)
            exit(1)

    dbName = params['params']['photoDatabase']['fileName']

    ## Connect to the database. Also set up Ctrl-C Handling
    conn = sqlite3.connect(os.path.join(project_path, 'databases', dbName))
    conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")

    nameDict = {}
    insertName('Tim', conn, 1, params, nameDict)
    print nameDict