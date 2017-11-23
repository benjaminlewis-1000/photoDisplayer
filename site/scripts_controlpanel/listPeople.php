

<?php 

	/* This function is designed to be run once, on the load of the page. Hitting the database too frequently
	causes an issue on the raspberry pi (it looks like something along the lines of locking up the database
	to future calls) and I don't know enough to fix it. So instead, this runs once on page load. The result is
	fed into a Javascript variable on the page, which is then used by other processes.

	Considering that, by design, the list of people changes on the order of a day (if there are new people in
	a photo), one load per page load should be completely sufficient. 

	This function returns an array with names as keys and the number of occurences of the name as the value 
	for each key.  */
	$exceptions = array();
	$debug = array();
	$arrayOfSavedShows = array();
	
	if (isset($_POST['minPhotos'])){
		$minPhotos = $_POST['minPhotos'];
	}else if (isset($_GET['minPhotos'])){
		$minPhotos = $_GET['minPhotos'];
	}else{
		$exceptions[] = "minimum number of photos not passed";
		$minPhotos = 1;
	}

	if (! is_numeric($minPhotos) ){
		$minPhotos = 1;
	}

	$parentDir = dirname_r(__FILE__, 3);

	$xml_params = simplexml_load_file($parentDir . '/config/params.xml') or die("Can't load this file!");
	$site_xml_params = simplexml_load_file(dirname_r(__FILE__, 2) . '/siteConfig.xml') or die("Can't load the site config file!");
	$photoDBpath = $parentDir . '/databases/' . $xml_params->photoDatabase->fileName;

/*
	$numPhotosQuery = 'WITH lotsOfPhotos AS ( SELECT person FROM photolinker GROUP BY person HAVING count(*) > '. $minPhotos. ' )
SELECT person_name FROM people WHERE People_key IN lotsOfPhotos';*/
	/* See https://www.w3schools.com/sql/sql_join_left.asp for info on left join.
	This query selects the person and the count of the person from the People table, joining that data to the 
	photoLinker table where people_key on People = person on photoLinker.
	*/

	$peopleTableName = $xml_params->photoDatabase->tables->peopleTable->Name; // "People"
	$peopleTablePersonName = $xml_params->photoDatabase->tables->peopleTable->Columns->personName; // "person_name"
	$peopleTablePersonKey = $xml_params->photoDatabase->tables->peopleTable->Columns->peopleKey; // "people_key"
	$people_personName = $peopleTableName . '.' . $peopleTablePersonName; // People.person_name
	$people_personKey = $peopleTableName . '.' . $peopleTablePersonKey; //People.people_key
	$photoLinkerTableName = $xml_params->photoDatabase->tables->photoLinkerTable->Name; // photoLinker
	$photoLinker_person = $photoLinkerTableName . '.' . $xml_params->photoDatabase->tables->photoLinkerTable->Columns->linkerPeople; // photoLinker.person

	$peoplePlusNumberQuery = 'SELECT ' . $people_personName . ', count('. $people_personName . ') FROM '. $peopleTableName . ' left join ' . $photoLinkerTableName . ' on ' . $people_personKey . ' = '. $photoLinker_person . ' GROUP BY '. $photoLinker_person . ' ORDER BY ' . $people_personName ;


/* dirname_r is for compatibility in PHP 5.0 (available on Raspberry Pi) */
	function dirname_r($path, $count=1){
	    if ($count > 1){
	       return dirname(dirname_r($path, --$count));
	    }else{
	       return dirname($path);
	    }
	}

	/* Get the name of the directory where the project lives */

	$excluded_xml_names = preg_split('/,/', $site_xml_params->excludedNames);
	$excluded_xml_patterns = preg_split('/,/', $site_xml_params->excludedPatterns);
	
	$exceptions = array();
	$personNames = array();

	if (! file_exists($photoDBpath) ){
		$exceptions[] = 'File ' . $photoDBpath . ' does not exist';
	}

	function exception_error_handler($errno, $errstr, $errfile, $errline ) {
	    throw new ErrorException($errstr, $errno, 0, $errfile, $errline);
	}
	set_error_handler("exception_error_handler");

	$debug[] = 'Database located at ' . $photoDBpath;


	try{	
	    $db = new SQLite3($photoDBpath);
	    // Give time for the database to connect - this was causing issues.
	    $db->busyTimeout(1000);
		try{
			$results = $db->query($peoplePlusNumberQuery);
		}catch(Exception $e){
			$exceptions[] = 'The table is not well-formed and probably wasn\'t initialized.';
		}
		$people = array();
		while ($row = $results->fetchArray()) {
			if (!empty($row[0])){
				$people[$row[0]] = $row[1] ;
			}
		}
   
    $db->close();
	}catch(Exception $e){
		$exceptions[] = 'Error when reading database';
	}

	foreach($excluded_xml_names as $excludedName){
		$excludedName = trim($excludedName);
		if (isset($people[$excludedName]) ){
			unset($people[$excludedName]);
		}
	}

	foreach($excluded_xml_patterns as $excludedPattern){
		$excludedPattern = trim($excludedPattern);
		foreach ($people as $key => $value){
			if (preg_match("/$excludedPattern/", $key)){
				unset($people[$key]);
			}
		}
	}

	/* Get the names of aliases, i.e. the person is in there twice under different names, but you only want one display name and the backend will take care of the muliple names. */

	$nameAliasRoot = $site_xml_params->nameAliases;
	$numDisplayNames = count($nameAliasRoot->children() );

	$strikeOutNames = [];
	$substituteNames = [];

	for ($i = 0; $i < $numDisplayNames; $i++){
		$numAlternateNames = count( $nameAliasRoot->displayName[$i]->children() );
		$alternate_count = 0;
		$displayName = trim($nameAliasRoot->displayName[$i]->display);
		//echo $displayName;
		for ($j = 0; $j < $numAlternateNames; $j++){
			$alternateName = trim($nameAliasRoot->displayName[$i]->aka[$j]);
			//echo $alternateName

			# Check if the alternate name is in the array. If so, we want to get its value and
			# add it to the display name. 
			if ( array_key_exists($alternateName, $people)  ){
				$alternate_count += $people[$alternateName];
				// names that are in substituteNames should be put in if they aren't already there
				unset($people[$alternateName]);
			}
		}

		# Add in the count for other alternate names to the display name; that way, the total
		# number is accounted in thresholding number of photos.
		if ( array_key_exists($displayName, $people) ){
			$people[$displayName] += $alternate_count;
		}else{
			$people[$displayName] = $alternate_count;
		}

		$substituteNames[] = $nameAliasRoot->displayName[$i]->display;
	}

	// strikeOutNames has a list of names that should be removed from the list
	for ($i = 0; $i < count($strikeOutNames); $i++){
		$excludedName = trim($strikeOutNames[$i]);
		unset($people[$excludedName]);
	}

	// Sort the list by number of photos with that person.
	arsort($people);

	$retArray = array('personNames' => $people, 'exceptions' => $exceptions, 'debug' => $debug);
	echo json_encode($retArray);

?>
