<?php 
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

	$numPhotosQuery = 'WITH lotsOfPhotos AS ( SELECT person FROM photolinker GROUP BY person HAVING count(*) > '. $minPhotos. ' )
SELECT person_name FROM people WHERE People_key IN lotsOfPhotos';

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
		$exceptions[] = 'File $photoDBpath does not exist';
	}

	function exception_error_handler($errno, $errstr, $errfile, $errline ) {
	    throw new ErrorException($errstr, $errno, 0, $errfile, $errline);
	}
	set_error_handler("exception_error_handler");

	$debug[] = 'Database located at $numPhotosQuery'
	try{
		$db = new SQLite3($photoDBpath);
		try{
			$results = $db->query($numPhotosQuery);
		}catch(Exception $e){
			$exceptions[] = 'The table is not well-formed and probably wasn\'t initialized.';
		}
		$people = array();
		while ($row = $results->fetchArray()) {
			if (!empty($row[0])){
				$people[] = $row[0];
			}
		}
		natcasesort ($people);
		foreach ($people as $person){
			$personNames[] = $person;
		}
	}catch(Exception $e){
		//die('connection_unsuccessful: ' . $e->getMessage());
		$exceptions[] = 'Error when reading database';
	}

	$retArray = array('personNames' => $personNames, 'exceptions' => $exceptions);
	echo json_encode($retArray);

?>