#! /usr/bin/env python

import json

class QueryMaker():

    def __init__(self, xmlParams):
        self.xmlParams = xmlParams
        pass

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

    def buildQueryFromJSON(self, criteriaJSON):

        # Load the json into a dictionary 
        slideshowParams = json.loads(str(criteriaJSON))

        people = [ ]
        selectedYears = [ ]
        selectedMonths = [ ]
        dateRangeVals = [ ]
        
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
            if critType.lower() == 'all':
                getAll = True
            if critType.lower() not in ['year', 'date range', "date%20Range", 'person', 'month', 'all']:
                errs.append('Criteria type {} was not found.'.format(critType) );
                returnDict['exceptions'] = errs;
                returnDict['debug'] = debug;
                return json.dumps(returnDict);
                raise TypeError


        if getAll:
            masterQuery = '''SELECT {}, {}, {}, {} FROM {} '''.format(phKey, phFile, phRootDir, phTakenDate, phTableName)
        else:
            orYearQuery, andYearQuery = self.__handleYear__(selectedYears)
            dateRangeQuery = self.__buildDateRange__(dateRangeVals)
            orPersonQuery = self.__buildPersonQueryOR__(people)
            monthQuery = self.__buildMonthQueryOR__(selectedMonths)


            masterQuery = ""

            ## From (Year AND Month) OR DateRange
            if len(selectedYears) > 0:
                # UNION the year range with the individual years
                # (i.e. the andYearQuery with the orYearQuery) - but only if applicable.
                if yearQueryStart[andIndex] and yearQueryStart[orIndex]:
                    masterQuery += andYearQuery + " UNION " + orYearQuery + " "
                else:
                    if yearQueryStart[andIndex]:
                        masterQuery += andYearQuery
                    if yearQueryStart[orIndex]:
                        masterQuery += orYearQuery
            if len(selectedMonths) > 0:
                if masterQuery != "":
                    masterQuery += " INTERSECT "
                masterQuery += orMonthQuery
            if len(dateRangeVals) > 0:
                if masterQuery != "":
                    masterQuery += " UNION "
                masterQuery += orDateRangeQuery

            if len(people) > 0: #orPersonQuery != "":
                if masterQuery != "":
                    masterQuery += " INTERSECT "
                masterQuery += orPersonQuery

            if masterQuery != "":
                #### Preliminary:
                prelimQuery = '''SELECT {}, {}, {}, {} FROM {} WHERE {} IN \n '''.format(phKey, phFile, phRootDir, phTakenDate, phTableName, phKey)
                masterQuery = prelimQuery +  "(" +  masterQuery + ")" 

        return masterQuery

    def __handleYear__(self, selectedYears):
        orYearQuery = '''SELECT {} FROM {} WHERE {} '''.format(self.phKey, self.phTableName, self.phTakenYear)
        andYearQuery = '''SELECT {} FROM {} WHERE {} '''.format(self.phKey, self.phTableName, self.phTakenYear)


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

        return orYearQuery, andYearQuery

    def __buildDateRange__(self, dateRangeVals):
        orDateRangeQuery = '''SELECT {} FROM {} WHERE {} '''.format(self.phKey, self.phTableName, self.phTakenDate)

        for i in range(len(dateRangeVals)):
            startDate = dateRangeVals[i][0]
            endDate = dateRangeVals[i][1]

            # print startDate
            # print endDate

            # Format the dates, if they aren't "None". 
            if startDate != "None":
                startDate = datetime.datetime.strptime(startDate, "%Y/%m/%d").strftime("%Y-%m-%d 00:00:00") 
            if endDate != "None":
                endDate = datetime.datetime.strptime(endDate, "%Y/%m/%d").strftime("%Y-%m-%d 23:59:59")

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
        orPersonQuery = '''SELECT * FROM ( SELECT {} AS c FROM {} WHERE {} = (SELECT {} FROM {} WHERE {} = '''.format(self.plPhoto, self.plTableName, self.plPerson, self.ppKey, self.ppTableName, self.ppName)

        for i in range(len(orPeople)):
            orPersonQuery += "\"" + orPeople[i] + "\""
            if i != len(orPeople) - 1:
                ## orPersonQuery += ''' ) UNION SELECT photo AS c FROM photoLinker WHERE person = (SELECT people_key FROM people WHERE person_name = '''
                orPersonQuery += ''' ) UNION SELECT {} AS c FROM {} WHERE {} = (SELECT {} FROM {} WHERE {} = '''.format(self.plPhoto, self.plTableName, self.plPerson, self.ppKey, self.ppTableName, self.ppName)

        orPersonQuery += " ) )"

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

        orMonthQuery = '''SELECT {} FROM {} WHERE {} '''.format(phKey, phTableName, phTakenMonth)
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