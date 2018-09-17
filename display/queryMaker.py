#! /usr/bin/env python

import json
import xmltodict
import datetime

class QueryMaker():

    def __init__(self, xmlParamFile):#, xmlParams):
        print "Init query maker..."
        self.xmlParams = xmlParamFile
        
                
        # Get all of the parameters for the different relevant tables and columns in tables.
        # Used to build queries.
        photoLinkerTable =  self.xmlParams['params']['photoDatabase']['tables']['photoLinkerTable']
        self.plTableName      =  photoLinkerTable['Name']
        self.plPerson         =  photoLinkerTable['Columns']['linkerPeople']
        self.plPhoto          =  photoLinkerTable['Columns']['linkerPhoto']

        peopleTable   =  self.xmlParams['params']['photoDatabase']['tables']['peopleTable']
        self.ppTableName   =  peopleTable['Name']
        self.ppKey         =  peopleTable['Columns']['peopleKey']
        self.ppName        =  peopleTable['Columns']['personName']

        photosTable   =  self.xmlParams['params']['photoDatabase']['tables']['photoTable']
        self.phTableName   =  photosTable['Name']
        self.phKey         =  photosTable['Columns']['photoKey']
        self.phTableName   =  photosTable['Name']
        self.phTakenMonth  =  photosTable['Columns']['photoMonth']
        self.phTakenYear   =  photosTable['Columns']['photoYear']
        self.phTakenDate   =  photosTable['Columns']['photoDate']
        self.phTakenDate   =  photosTable['Columns']['photoDate']
        self.phFile        =  photosTable['Columns']['photoFile']
        self.phRootDir     =  photosTable['Columns']['rootDirNum']

        userCommentTable   = self.xmlParams['params']['photoDatabase']['tables']['commentLinkerUserTable']
        self.usComTableName     = userCommentTable['Name']
        self.usComTablePhotoNum = userCommentTable['Columns']['commentLinkerPhoto']
        self.usComTableTagStr   = userCommentTable['Columns']['commentLinkerTag']
        
        print "Init done!"

    def buildQueryFromJSON(self, criteriaJSON):

        # Load the json into a dictionary 
        slideshowParams = json.loads(str(criteriaJSON))

        people = [ ]
        selectedYears = [ ]
        selectedMonths = [ ]
        dateRangeVals = [ ]
        keywordVals = [ ]
        getAll = False
        
        for i in range(len(slideshowParams)):
            # Parse out the json for each parameter. Get the type of criteria,
            # the boolean value requested (i.e. 'is', 'is not') and the values
            # requested. Check to see what type of criteria it is, add it to 
            # the appropriate list, and then use those lists to do type-specific
            # parsing into a SQL query, which can then be built into a larger SQL
            # query.

            critType = slideshowParams[i]['criteriaType']
            boolVal = slideshowParams[i]['booleanValue']
            critVal = slideshowParams[i]['criteriaVal']

            if critType.lower() == 'year':
                assert unicode(critVal).isnumeric()
                selectedYears.append( (critVal, boolVal) )
            if str(critType) == 'Date Range' or str(critType) == "Date%20Range":
                if not (boolVal == "None" and critVal == "None"):
                    dateRangeVals.append( (boolVal, critVal) )
            if critType.lower() == 'person':
                people.append(critVal)
            if critType.lower() == 'month':
                selectedMonths.append( (critVal, boolVal) )
            if critType.lower() == 'keywords':
                keywordVals.append( critVal )
            if critType.lower() == 'all':
                getAll = True
            if critType.lower() not in ['year', 'date range', "date%20Range", 'person', 'month', 'all']:
                print "Error! Type {} not found.".format(critType)
                errs.append('Criteria type {} was not found.'.format(critType) );
                returnDict['exceptions'] = errs;
                returnDict['debug'] = debug;
                return json.dumps(returnDict);
                raise TypeError

        if getAll:
            masterQuery = '''SELECT {}, {}, {}, {} FROM {} '''.format(phKey, phFile, phRootDir, phTakenDate, phTableName)
        else:

            masterQuery = ""

            ## From (Year AND Month) OR DateRange
            if len(selectedMonths) > 0:
                monthQuery = self.__buildMonthQueryOR__(selectedMonths)
                if masterQuery != "":
                    masterQuery += " INTERSECT "
                masterQuery += monthQuery

            if len(dateRangeVals) > 0:
                dateRangeQuery = self.__buildDateRange__(dateRangeVals)
                if masterQuery != "":
                    masterQuery += " UNION "
                masterQuery += dateRangeQuery

            if len(people) > 0: #orPersonQuery != "":
                orPersonQuery = self.__buildPersonQueryOR__(people)
                if masterQuery != "":
                    masterQuery += " INTERSECT "
                masterQuery += orPersonQuery

            if len(selectedYears) > 0:
                yearQuery = self.__handleYear__(selectedYears)
                # UNION the year range with the individual years
                # (i.e. the andYearQuery with the orYearQuery) - but only if applicable.
                if masterQuery != "":
                    masterQuery += " INTERSECT "
                masterQuery += yearQuery

            if len(keywordVals) > 0:
                kwQuery = self.__handleKeyword__(keywordVals)
                if masterQuery != "":
                    masterQuery += " INTERSECT "
                masterQuery += kwQuery
                
            if masterQuery != "":
                #### Preliminary:
                prelimQuery = '''SELECT {}, {}, {}, {} FROM {} WHERE {} IN \n '''.format(self.phKey, self.phFile, self.phRootDir, self.phTakenDate, self.phTableName, self.phKey)
                masterQuery = prelimQuery +  "(" +  masterQuery + ")" 

        return masterQuery

    def __handleKeyword__(self, selectedKeyword):

        # Parentheses and SELECT * to guarantee that UNION takes place before INTERSECT
        keywordQuery = "SELECT * FROM ("

        for keyIdx in range(len(selectedKeyword)):
            eachKeyword = selectedKeyword[keyIdx]
            partQuery = '''SELECT {} FROM {} WHERE UPPER({}) = UPPER("{}")'''.format(self.usComTablePhotoNum, self.usComTableName, self.usComTableTagStr, eachKeyword)
            keywordQuery += partQuery
            # If not the last keyword: 
            if keyIdx != ( len(selectedKeyword) - 1 ):
                keywordQuery += " UNION "

        keywordQuery += ")"
        return keywordQuery


    def __handleYear__(self, selectedYears):
        orYearQuery = '''SELECT {} FROM {} WHERE {} '''.format(self.phKey, self.phTableName, self.phTakenYear)
        andYearQuery = '''SELECT {} FROM {} WHERE {} '''.format(self.phKey, self.phTableName, self.phTakenYear)

        if len(selectedYears) == 0:
            return ""
        yearQueryStart = [False, False]
        andIndex = 0
        orIndex = 1

        for i in range(len(selectedYears)):
            year = selectedYears[i][0]
            modifier = selectedYears[i][1]
            if modifier.lower() in ['is before', 'is after']:
                if yearQueryStart[andIndex]:
                    andYearQuery += ' AND {} '.format(self.phTakenYear)
                if modifier.lower() == 'is before':
                    andYearQuery += ' < '
                else:
                    andYearQuery += ' > '
                andYearQuery += str(year)
                yearQueryStart[andIndex] = True
            elif modifier.lower() in ['is', 'is not']:
                if yearQueryStart[orIndex]:
                    orYearQuery += ' OR {} '.format(self.phTakenYear)
                if modifier.lower() == 'is':
                    orYearQuery += ' = '
                else:
                    orYearQuery += ' != '
                orYearQuery += str(year)
                yearQueryStart[orIndex] = True
            else:
                raise Exception('Year modifier is not valid.')
                
        #returnQuery = ""
        if yearQueryStart[andIndex] and yearQueryStart[orIndex]:
            returnQuery = andYearQuery + " UNION " + orYearQuery + " "
        else:
            if yearQueryStart[andIndex]:
                returnQuery = andYearQuery
            if yearQueryStart[orIndex]:
                returnQuery = orYearQuery

        return returnQuery

    def __buildDateRange__(self, dateRangeVals):
        print dateRangeVals
        orDateRangeQuery = '''SELECT {} FROM {} WHERE {} '''.format(self.phKey, self.phTableName, self.phTakenDate)

        for i in range(len(dateRangeVals)):
            startDate = dateRangeVals[i][0]
            endDate = dateRangeVals[i][1]

            print "Start: {} End: {}".format(startDate, endDate)
            # print startDate
            # print endDate

            # Format the dates, if they aren't "None". 
            if startDate != "None":
                startDate = datetime.datetime.strptime(startDate, "%m/%d/%Y").strftime("%Y-%m-%d 00:00:00") 
            if endDate != "None":
                endDate = datetime.datetime.strptime(endDate, "%m/%d/%Y").strftime("%Y-%m-%d 23:59:59")

            if ( startDate != "None" and endDate != "None" ):
                # Get the ordering right, so we don't have mutually exclusive dates. 
                if endDate < startDate:
                    tmp = startDate
                    startDate = endDate
                    endDate = tmp
                orDateRangeQuery += " > \"" + startDate + "\" AND {} < \"".format(self.phTakenDate) + endDate + "\""
            else:
                if ( startDate != "None" ):
                    orDateRangeQuery += " > \"" + startDate + "\""
                else:
                    orDateRangeQuery += " < \"" + endDate + "\""

            if i != len(dateRangeVals) - 1:
                orDateRangeQuery += " OR {} ".format(self.phTakenDate)

        return orDateRangeQuery

    def __buildPersonQueryOR__(self, orPeople):

        # print "build query or: "
        # print orPeople
    
        orPersonQuery = '''SELECT * FROM ( SELECT {} AS c FROM {} WHERE {} = (SELECT {} FROM {} WHERE {} = '''.format(self.plPhoto, self.plTableName, self.plPerson, self.ppKey, self.ppTableName, self.ppName)

        for i in range(len(orPeople)): #eachPerson in orPeople:
            eachPerson = orPeople[i]
            orPersonQuery += "\"" + eachPerson + "\""
            if i != len(orPeople) - 1:
                ## orPersonQuery += ''' ) UNION SELECT photo AS c FROM photoLinker WHERE person = (SELECT people_key FROM people WHERE person_name = '''
                orPersonQuery += ''' ) UNION SELECT {} AS c FROM {} WHERE {} = (SELECT {} FROM {} WHERE {} = '''.format(self.plPhoto, self.plTableName, self.plPerson, self.ppKey, self.ppTableName, self.ppName)

        orPersonQuery += " ) )"

        print "Or query: {}".format(orPersonQuery)
        return orPersonQuery


    def __buildPersonQueryAND__(self, andPeople):

        andPersonQuery = '''SELECT {} FROM {} AS photo_key_and_var JOIN (SELECT {} AS {} FROM {} WHERE {} = '''.format(self.phKey, self.phTableName, self.plPhoto, self.phKey, self.plTableName, self.plPerson)

        for i in range(len(andPeople)):
            ## personIntermediateQuery = '''(SELECT people_key FROM people WHERE person_name = "'''  + people[i]  + "\" )"
            personIntermediateQuery = '''(SELECT {} FROM {} WHERE {} = "'''.format(self.ppKey, self.ppTableName, self.ppName)  + andPeople[i]  + "\" )"
            andPersonQuery += personIntermediateQuery
            if i != len(andPeople) - 1:
                ## andPersonQuery += ''' INTERSECT SELECT photo AS photo_key FROM photoLinker WHERE person = '''
                andPersonQuery += ''' INTERSECT SELECT {} AS {} FROM {} WHERE {} = '''.format(self.plPhoto, self.phKey, self.plTableName, self.plPerson)

        andPersonQuery += " ) AS linker_tmp_var ON photo_key_and_var.{} = linker_tmp_var.{}".format(self.phKey, self.phKey)

        return andPersonQuery


    def __buildMonthQueryOR__(self, selectedMonths):

        orMonthQuery = '''SELECT {} FROM {} WHERE {} '''.format(self.phKey, self.phTableName, self.phTakenMonth)
        months = {"January" : 1, "February" : 2, "March" : 3, "April" : 4, "May" : 5, "June" : 6, "July" : 7, "August" : 8, "September" : 9, "October" : 10, "November" : 11, "December" : 12}
        i = 0
        for i in range(len(selectedMonths)):
            monthOrdinal =  selectedMonths[i][0] 
            isOrIsnt = selectedMonths[i][1]
            if isOrIsnt == 'is':
                orMonthQuery += '= '
            else:
                orMonthQuery += '!= '
            orMonthQuery +=  str(monthOrdinal)
            if i != len(selectedMonths) - 1:
                orMonthQuery += " OR {} ".format(phTakenMonth)
            i += 1

        return orMonthQuery


if __name__ == '__main__':
    import os
    project_path = os.path.abspath(os.path.join(__file__,"../.."))
    script_path  = os.path.abspath(os.path.join(__file__,".."))

    xmlParamFile = os.path.join(project_path, "config", 'params.xml' )
    with open(xmlParamFile) as stream:
        try:
           xmlParams = xmltodict.parse(stream.read())
        except Exception as exc:
           print(exc)
           exit(1)
    qm = QueryMaker( xmlParams)

            
    criteriaJSON = '''[{"criteriaType": "year", "booleanValue": "is", "criteriaVal": "2001"} , 
    {"criteriaType": "person", "booleanValue": "is", "criteriaVal": "Ben"}, 
    {"criteriaType": "person", "booleanValue": "is", "criteriaVal": "Johnny boy"}]'''
    print qm.buildQueryFromJSON(criteriaJSON)