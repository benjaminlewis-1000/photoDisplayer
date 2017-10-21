

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
/*
	$numPhotosQuery = 'WITH lotsOfPhotos AS ( SELECT person FROM photolinker GROUP BY person HAVING count(*) > '. $minPhotos. ' )
SELECT person_name FROM people WHERE People_key IN lotsOfPhotos';*/
	/* See https://www.w3schools.com/sql/sql_join_left.asp for info on left join.
	This query selects the person and the count of the person from the People table, joining that data to the 
	photoLinker table where people_key on People = person on photoLinker.
	*/
	$peoplePlusNumberQuery = 'SELECT People.person_name, count(people.person_name) FROM PEOPLE left join photolinker on people.people_key = photoLinker.person GROUP BY photoLinker.person ORDER BY people.person_name';

/* dirname_r is for compatibility in PHP 5.0 (available on Raspberry Pi) */
	function dirname_r($path, $count=1){
	    if ($count > 1){
	       return dirname(dirname_r($path, --$count));
	    }else{
	       return dirname($path);
	    }
	}

	/* Get the name of the directory where the project lives */
	$parentDir = dirname_r(__FILE__, 3);

	$xml_params = simplexml_load_file($parentDir . '/config/params.xml') or die("Can't load this file!");
	$photoDBpath = $parentDir . '/databases/' . $xml_params->photoDatabase->fileName;
	
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

	$retArray = array('personNames' => $people, 'exceptions' => $exceptions, 'debug' => $debug);
	echo json_encode($retArray);

?>