#! /usr/bin/env python

def buildQueryFromJSON():

    people = [ ]
    selectedYears = [ ]
    selectedMonths = [ ]
    dateRangeVals = [ ]

    # Get all of the parameters for the different relevant tables
    photoLinkerTable =  self.xmlParams['params']['photoDatabase']['tables']['photoLinkerTable']
    plTableName      =  photoLinkerTable['Name']
    plPerson         =  photoLinkerTable['Columns']['linkerPeople']
    plPhoto          =  photoLinkerTable['Columns']['linkerPhoto']

    peopleTable   =  self.xmlParams['params']['photoDatabase']['tables']['peopleTable']
    ppTableName   =  peopleTable['Name']
    ppKey         =  peopleTable['Columns']['peopleKey']
    ppName        =  peopleTable['Columns']['personName']

    photosTable   =  self.xmlParams['params']['photoDatabase']['tables']['photoTable']
    phTableName   =  photosTable['Name']
    phKey         =  photosTable['Columns']['photoKey']
    phTableName   =  photosTable['Name']
    phTakenMonth  =  photosTable['Columns']['photoMonth']
    phTakenYear   =  photosTable['Columns']['photoYear']
    phTakenDate   =  photosTable['Columns']['photoDate']
    phTakenDate   =  photosTable['Columns']['photoDate']
    phFile        =  photosTable['Columns']['photoFile']
    phRootDir     =  photosTable['Columns']['rootDirNum']

    getAll = False

    for i in range(len(slideshowParams)):
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

    # Build year limits
    for i in range(len(slideshowParams)):
        # print slideshowParams[i]
        paramType = slideshowParams[i]['criteriaType']
        start_Limit = slideshowParams[i]['booleanValue']
        end_Criteria = slideshowParams[i]['criteriaVal']

    ### OR SQL person query
    # orPersonQuery = '''SELECT photo AS c FROM photoLinker WHERE person = (SELECT people_key FROM people WHERE person_name = '''
    orPersonQuery = '''SELECT * FROM ( SELECT {} AS c FROM {} WHERE {} = (SELECT {} FROM {} WHERE {} = '''.format(plPhoto, plTableName, plPerson, ppKey, ppTableName, ppName)
    for i in range(len(people)):
        orPersonQuery += "\"" + people[i] + "\""
        if i != len(people) - 1:
            ## orPersonQuery += ''' ) UNION SELECT photo AS c FROM photoLinker WHERE person = (SELECT people_key FROM people WHERE person_name = '''
            orPersonQuery += ''' ) UNION SELECT {} AS c FROM {} WHERE {} = (SELECT {} FROM {} WHERE {} = '''.format(plPhoto, plTableName, plPerson, ppKey, ppTableName, ppName)

    orPersonQuery += " ) )"

    # print orPersonQuery

    ## The only difference between AND and OR is INTERSECT vs UNION

    ### AND SQL person query
    ## Example: SELECT * FROM photos AS photo_table_var JOIN (SELECT photo AS photo_key FROM photolinker WHERE person = 1 INTERSECT SELECT photo AS photo_key FROM photolinker WHERE person = 2 ) AS linker_tmp_var ON photo_table_var.photo_key = linker_tmp_var.photo_key

    ## andPersonQuery = '''SELECT photo_key FROM photos AS photo_key_and_var JOIN (SELECT photo AS photo_key FROM photoLinker WHERE person = '''
    andPersonQuery = '''SELECT {} FROM {} AS photo_key_and_var JOIN (SELECT {} AS {} FROM {} WHERE {} = '''.format(phKey, phTableName, plPhoto, phKey, plTableName, plPerson)
    for i in range(len(people)):
        ## personIntermediateQuery = '''(SELECT people_key FROM people WHERE person_name = "'''  + people[i]  + "\" )"
        personIntermediateQuery = '''(SELECT {} FROM {} WHERE {} = "'''.format(ppKey, ppTableName, ppName)  + people[i]  + "\" )"
        andPersonQuery += personIntermediateQuery
        if i != len(people) - 1:
            ## andPersonQuery += ''' INTERSECT SELECT photo AS photo_key FROM photoLinker WHERE person = '''
            andPersonQuery += ''' INTERSECT SELECT {} AS {} FROM {} WHERE {} = '''.format(plPhoto, phKey, plTableName, plPerson)

    andPersonQuery += " ) AS linker_tmp_var ON photo_key_and_var.{} = linker_tmp_var.{}".format(phKey, phKey)

    ### Month SQL Query - each month should be unioned, then intersected with the larger query. 
    ### ANDing month queries makes no sense - you can't have a photo that is in two months, and
    ### negating a month is superflous. 
    # orMonthQuery = '''SELECT photo_key FROM Photos WHERE taken_month '''
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

    ### Similar with years - Anding them doesn't make sense for is/is not; 
    ### However, it does make sense with befores/afters.
    # orYearQuery = '''SELECT photo_key FROM photos WHERE taken_year '''
    # andYearQuery = '''SELECT photo_key FROM photos WHERE taken_year '''
    orYearQuery = '''SELECT {} FROM {} WHERE {} '''.format(phKey, phTableName, phTakenYear)
    andYearQuery = '''SELECT {} FROM {} WHERE {} '''.format(phKey, phTableName, phTakenYear)
    yearQueryStart = [False, False]
    andIndex = 0
    orIndex = 1

    for i in range(len(selectedYears)):

        print "year"
        year = selectedYears[i][0]
        modifier = selectedYears[i][1]
        if modifier.lower() in ['is before', 'is after']:
            if yearQueryStart[andIndex]:
                andYearQuery += ' AND {} '.format(phTakenYear)
            if modifier.lower() == 'is before':
                andYearQuery += ' < '
            else:
                andYearQuery += ' > '
            andYearQuery += str(year)
            yearQueryStart[andIndex] = True
        elif modifier.lower() in ['is', 'is not']:
            if yearQueryStart[orIndex]:
                orYearQuery += ' OR {} '.format(phTakenYear)
            if modifier.lower() == 'is':
                orYearQuery += ' = '
            else:
                orYearQuery += ' != '
            orYearQuery += str(year)
            yearQueryStart[orIndex] = True
        else:
            raise Exception('Year modifier is not valid.')

    ### Date ranges - must be or'd. It doesn't make sense to AND date ranges, because the date
    ### range could be changed or another date range selected to get the appropriate values. 

    stream.close()
    orDateRangeQuery = '''SELECT {} FROM {} WHERE {} '''.format(phKey, phTableName, phTakenDate)
    for i in range(len(dateRangeVals)):
        startDate = dateRangeVals[i][0]
        endDate = dateRangeVals[i][1]

        print startDate
        print endDate

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
            orDateRangeQuery += " > \"" + startDate + "\" AND {} < \"".format(phTakenDate) + endDate + "\""
        else:
            if ( startDate != "None" ):
                orDateRangeQuery += " > \"" + startDate + "\""
            else:
                orDateRangeQuery += " < \"" + endDate + "\""

        if i != len(dateRangeVals) - 1:
            orDateRangeQuery += " OR {} ".format(phTakenDate)


    masterQuery = ""
    ### Build a query that encapsulates all of the date ranges and specifics that were requested. 
    buildDates = ""
    ## From (Year AND Month) OR DateRange
    if len(selectedYears) > 0:
        # UNION the year range with the individual years
        # (i.e. the andYearQuery with the orYearQuery) - but only if applicable.
        if yearQueryStart[andIndex] and yearQueryStart[orIndex]:
            buildDates += andYearQuery + " UNION " + orYearQuery + " "
        else:
            if yearQueryStart[andIndex]:
                buildDates += andYearQuery
            if yearQueryStart[orIndex]:
                buildDates += orYearQuery
    if len(selectedMonths) > 0:
        if buildDates != "":
            buildDates += " INTERSECT "
        buildDates += orMonthQuery
    if len(dateRangeVals) > 0:
        if buildDates != "":
            buildDates += " UNION "
        buildDates += orDateRangeQuery

    if buildDates != "":
        masterQuery += buildDates

    if len(people) > 0: #orPersonQuery != "":
        if masterQuery != "":
            masterQuery += " INTERSECT "
        masterQuery += orPersonQuery

    if masterQuery != "":
        #### Preliminary:
        prelimQuery = '''SELECT {}, {}, {}, {} FROM {} WHERE {} IN \n '''.format(phKey, phFile, phRootDir, phTakenDate, phTableName, phKey)
        masterQuery = prelimQuery +  "(" +  masterQuery + ")" 

    return masterQuery