<?php


	$exceptions = array();
	$debug = array();

	// Set the error handler

	function exception_error_handler($errno, $errstr, $errfile, $errline ) {
	    throw new ErrorException($errstr, $errno, 0, $errfile, $errline);
	}
	set_error_handler("exception_error_handler");

	if (isset($_POST['json'])){
		$jsonText = $_POST['json'];
	}else if (isset($_GET['json'])){
		$jsonText = $_GET['json'];
	}else{
		$exceptions[] = "Invalid JSON -- Not OK";
		$retArray = array('exceptions' => $exceptions, 'debug' => $debug );
		echo json_encode($retArray);
		exit;
	}

	function dirname_r($path, $count=1){
	    if ($count > 1){
	       return dirname(dirname_r($path, --$count));
	    }else{
	       return dirname($path);
	    }
	}

	$parentDir = dirname_r(__FILE__, 3);

	try{
		$xml_params = simplexml_load_file($parentDir . '/config/params.xml');
	}catch(Exception $e){
		$exceptions[] = 'Can\'t load the parameter file...';
		$retArray = array('exceptions' => $exceptions, 'debug' => $debug );
		echo json_encode($retArray);
		exit;		
	}
	//echo $xml_params->photoDatabase->tables->photoTable->Name . "<br>";
	$photoDBpath = $parentDir . '/databases/' . $xml_params->photoDatabase->fileName;
	
	$jsonArray = json_decode($jsonText, true);

	$allValid = 1;

	try{
		//echo '../databases/' . $photoDBname;
		$db = new SQLite3($photoDBpath);

		$fieldBasestruct = $xml_params->photoDatabase->tables;
		//$results = $db->query('SELECT person_name FROM people');
		$results = $db->query('SELECT ' . $fieldBasestruct->peopleTable->Columns->personName . ' FROM ' . $fieldBasestruct->peopleTable->Name);
		$people = array();
		while ($row = $results->fetchArray()) {
			if (!empty($row[0])){
				$people[] = $row[0];
			}
		}
	}catch(Exception $e){
		$exceptions[] = 'connection_unsuccessful: ' . $e->getMessage() . '. File = ' . '../databases/' . $photoDBname;
		$retArray = array('exceptions' => $exceptions, 'debug' => $debug );
		echo json_encode($retArray);
		exit;
	}

	$formedArray = array();

	foreach ($jsonArray as $item){
		$type = $item['criteriaType'];
		$boolVal = $item['booleanValue'];
		$criteriaVal = $item['criteriaVal'];

	//["Date Range", "Person", "Year", "Month"]
		switch($type){
			case "Date Range":
				$boolVal = strtolower($boolVal);
				$criteriaVal = strtolower($criteriaVal);
				$date_start = date_parse($boolVal);
				$date_end = date_parse($criteriaVal);

				//print_r($date_start);
				//echo empty($date_start['year']);

				$validStrings = !( ( !$date_start["error_count"] || $boolVal == "<none>" ) && ( !$date_end["error_count"] || $criteriaVal == "<none>" )  );
				$validDMY1 = !empty($date_start['year']) && !empty($date_start['day']) && !empty($date_start['month']);
				$validDMY2 = !empty($date_end['year']) && !empty($date_end['day']) && !empty($date_end['month']);

				$validity = $validStrings && $validDMY1 && $validDMY2;

				if ($validity){
					$exceptions[] = "$boolVal, $criteriaVal not valid in Date_range\n";
					$allValid = 0;
				}

				## Reform the JSON so I know I'm passing it in a given state. 
				if ($boolVal == "<none>"){
					$start_formatted = "None";
				}else{
					$start_formatted = $date_start['year'] . '/' . str_pad($date_start['month'], 2, "0", STR_PAD_LEFT) . '/' . str_pad($date_start['day'], 2, "0", STR_PAD_LEFT);
				}
				if ($criteriaVal == "<none>"){
					$end_formatted = "None";
				}else{
					$end_formatted = $date_end['year'] . '/' . str_pad($date_end['month'], 2, "0", STR_PAD_LEFT) . '/' . str_pad($date_end['day'], 2, "0", STR_PAD_LEFT);
				}

				$data = array("criteriaType" =>"Date Range", "booleanValue" => "$start_formatted", "criteriaVal" => "$end_formatted");
				array_push($formedArray, $data);
				break;
			case "Person":
				$valid1 = preg_match("/^is|is not$/i", $boolVal, $matches);
				if(in_array($criteriaVal, $people)){ // For some reason in_array isn't returning false.
					$valid2 = 1;
				}else{
					$valid2 = 0;
				}
				//echo($valid1);
				//echo($valid2);
				if (!($valid1 and $valid2)){
					$exceptions[] = "$boolVal, $criteriaVal not valid in Person";
					$allValid = 0;
				}

				$data = array("criteriaType" =>"Person", "booleanValue" => "$boolVal", "criteriaVal" => "$criteriaVal");
				array_push($formedArray, $data);
				break;
			case "Year":
				$valid1 = preg_match("/^is|is not|is before|is after$/i", $boolVal, $matches);

				$yearValid = ctype_digit($criteriaVal);

				$year = $criteriaVal;

				if (!$valid1 or !$yearValid){
					//echo "$boolVal, $criteriaVal not valid in Year";
					$allValid = 0;
					break;
				}

				if ( (int)$criteriaVal < 50){
					$year += 2000;
				}
				if ( (int)$criteriaVal > 50 && (int)$criteriaVal < 100){
					$year += 1900;
				}

				$year = strval($year);

				//print_r($year);
				$data = array("criteriaType" =>"Year", "booleanValue" => "$boolVal", "criteriaVal" =>"$year");
				array_push($formedArray, $data);
				break;
			case "Month":
				$valid1 = preg_match("/^is|is not$/i", $boolVal, $matches);
				$month = $criteriaVal < 13 && $criteriaVal > 0 && ctype_digit($criteriaVal) ;

				if (!$valid1 or !$month){
					//print_r($month);
					$exceptions[] = "$boolVal, $criteriaVal not valid in Month";
					$allValid = 0;
				}
				$data = array("criteriaType" =>"Month", "booleanValue" => "$boolVal", "criteriaVal" =>"$criteriaVal");
				array_push($formedArray, $data);

				break;
		}

	}


//print_r($formedArray);
	$parsed_text =  json_encode($formedArray, JSON_UNESCAPED_SLASHES);
	//echo $parsed_text;
	
	if (!$allValid){
		$exceptions[] = "Not all criteria in the JSON were valid. See console for more info.";
		//echo 'var valid=0';
	}else{
		// We're good to go! All these have been validated to be good JSON. 
        $debug[] = "All parsed arguments are valid: " . $parsed_text;

        $request = xmlrpc_encode_request("buildQuery" , array($parsed_text));
		$context = stream_context_create(array('http' => array(
		    'method' => "POST",
		    'header' => "Content-Type: text/xml",
		    'content' => $request
		)));

		$url = "http://127.0.0.1:" . $xml_params->serverParams->displayServerPort;
		$file = file_get_contents($url, false, $context);
		$response = xmlrpc_decode($file);
		//$debug[] = "Full response was: " . $response;
	
		$jsonArray = json_decode($response, true);
		$errs = $jsonArray['errs'];
		$debugs = $jsonArray['debug'];
		$debug = array_merge($debug, $debugs);
		$exceptions = array_merge($exceptions, $errs);
	}

	$retArray = array('exceptions' => $exceptions, 'debug' => $debug );
	echo json_encode($retArray);

?>
