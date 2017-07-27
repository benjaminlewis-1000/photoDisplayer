
<?php 
/* dirname_r is for compatibility in PHP 5.0 (available on Raspberry Pi) */

	$exceptions = array();

	if (isset($_POST['queryType'])){
		$queryType = $_POST['queryType'];
	}else if (isset($_GET['queryType'])){
		$queryType = $_GET['queryType'];
	}else{
		echo("<script>console.log(\"Invalid JSON\")</script>");
		echo("Not ok");
		exit;
	}
	
	if (isset($_POST['selectedVal'])){
		$selectedVal = $_POST['selectedVal'];
	}else if (isset($_GET['selectedVal'])){
		$selectedVal = $_GET['selectedVal'];
	}else{
		$selectedVal = '';
	}

	if (isset($_POST['name'])){
		$name = $_POST['name'];
	}else if (isset($_GET['name'])){
		$name = $_GET['name'];
	}else{
		$name = '';
	}


	if ($queryType == "loadShowNames"){
		$query = 'SELECT showNames FROM Slideshows';

		$queries = array($query);
	}elseif ($queryType == "loadJSONofName"){
		$query = 'SELECT savedJSON FROM Slideshows WHERE showNames = "' . $selectedVal . '"';

		$queries = array($query);
	}elseif ($queryType == "saveValue"){
		// If we have a show by that name, just assume that we are overwriting the show name with new criteria; then save the new show. 
		$query1 = 'DELETE FROM Slideshows WHERE showNames = "' . $name . '"';
		$query2 = 'INSERT INTO Slideshows (showNames, savedJSON) VALUES ("' . $name . '", \'' . $selectedVal . '\')';

		$queries = array($query1, $query2);
	}elseif ($queryType == "removeShow"){
		$query = 'DELETE FROM Slideshows WHERE showNames = "' . $selectedVal . '"';

		$queries = array($query);
	}

	function dirname_r($path, $count=1){
	    if ($count > 1){
	       return dirname(dirname_r($path, --$count));
	    }else{
	       return dirname($path);
	    }
	}

	/* Get the name of the directory where the project lives */
	$parentDir = dirname_r(__FILE__, 2);
	$siteDir = dirname_r(__FILE__, 1);

	//$xml_params = simplexml_load_file($parentDir . '/config/params.xml') or die("Can't load this file!");
	$photoDBpath = $siteDir . '/savedSlideshows.db';


	if (! file_exists($photoDBpath) ){
		$exceptions[] = 'File $photoDBpath does not exist';
	}
	function exception_error_handler($errno, $errstr, $errfile, $errline ) {
	    throw new ErrorException($errstr, $errno, 0, $errfile, $errline);
	}
	set_error_handler("exception_error_handler");

	try{
		$db = new SQLite3($photoDBpath);
	}catch(Exception $e){
		$exceptions[] = "Unable to create new database in " . $photoDBpath;
		$retArray = array('exceptions' => $exceptions, 'debug' => $debug );
		echo json_encode($retArray);
		exit;
	}
	$arrayOfSavedShows = array();

	for ($i = 0; $i < count($queries); $i++){
		// Iterate through all the queries sequentially. 

		$query = $queries[$i];
		try{
			$results = $db->query($query);
			if ($queryType != "saveValue"){
				while ($savedShowNames = $results->fetchArray() ){
					$currentName = $savedShowNames[0];
					$arrayOfSavedShows[] = $currentName;
				}
			}
		}catch(Exception $e){
			//print_r("console.log('The table is not well-formed and probably wasn\'t initialized.')\n");
			//$exceptions[] = 'The table is not well-formed and probably wasn\'t initialized.';
			$errmesg = $e->getMessage();
			if (strpos($errmesg, 'Unable to execute statement: UNIQUE constraint failed') !== false) {
				$exceptions[] = 'Key is not unique.';
			}else{
				$exceptions[] = $errmesg;
			}
			$query = 'SELECT name FROM sqlite_master WHERE type=\'table\'';
			//print_r("console.log(\"$query\");\n");
			$exceptions[] = $query;
			$existingTables = $db->query($query);

			$row = $existingTables->fetchArray();
			$tableName = $row[0];
			if (!empty($row[0])){
				if ($tableName != 'Slideshows'){
					$makeTableQuery = 'CREATE TABLE Slideshows (   showNames  TEXT UNIQUE,  savedJSON TEXT);';
					$db->query($makeTableQuery);					
				}
			}else{
				$makeTableQuery = 'CREATE TABLE Slideshows (   showNames  TEXT UNIQUE,  savedJSON TEXT);';
				$db->query($makeTableQuery);
			}
			$arrayOfSavedShows[] = '';
		}
	}


	/// At this point, we have an array of saved shows that we can pass back to javascript. 
	//echo 'var savedShows = ' . json_encode($arrayOfSavedShows) . ';';

	$retArray = array('savedVals' => $arrayOfSavedShows, 'exceptions' => $exceptions);
	echo json_encode($retArray);

?>