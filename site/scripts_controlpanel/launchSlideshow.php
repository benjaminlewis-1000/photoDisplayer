<?php


	$exceptions = array();
	$debug = array();

	// Set the error handler


	/**
	 * Check if a given ip is in a network
	 * @param  string $ip    IP to check in IPV4 format eg. 127.0.0.1
	 * @param  string $range IP/CIDR netmask eg. 127.0.0.0/24, also 127.0.0.1 is accepted and /32 assumed
	 * @return boolean true if the ip is in this range / false if not.
	 * Source: https://gist.github.com/tott/7684443
	 */
	function ip_in_range( $ip, $range ) {
		if ( strpos( $range, '/' ) == false ) {
			$range .= '/32';
		}
		// $range is in IP/CIDR format eg 127.0.0.1/24
		list( $range, $netmask ) = explode( '/', $range, 2 );
		$range_decimal = ip2long( $range );
		$ip_decimal = ip2long( $ip );
		$wildcard_decimal = pow( 2, ( 32 - $netmask ) ) - 1;
		$netmask_decimal = ~ $wildcard_decimal;
		return ( ( $ip_decimal & $netmask_decimal ) == ( $range_decimal & $netmask_decimal ) );
	}

	// Check if the requesting IP is in the network; if not, ignore and give a polite message in the debug.
	if (!ip_in_range($_SERVER['REMOTE_ADDR'], '192.168.0.0/16') && $_SERVER['REMOTE_ADDR'] != '::1'){
		$exceptions[] = "Computer is not on local network";
		$retArray = array('exceptions' => $exceptions, 'debug' => $debug );
		echo json_encode($retArray);
		exit;
  	}


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

	if (isset($_POST['options'])){
		$options = $_POST['options'];
	}else if (isset($_GET['options'])){
		$options = $_GET['options'];
	}else{
		$exceptions[] = "Invalid Options Passed -- Not OK";
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

	try{
		$site_params = simplexml_load_file($parentDir . '/site/siteConfig.xml');
	}catch(Exception $e){
		$exceptions[] = 'Can\'t load the parameter file siteConfig.xml...';
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

				$nameAliasRoot = $site_params->nameAliases;
				foreach($nameAliasRoot->displayName as $item)
				{
				   $displayName = $item->display;
				   if ($displayName == $criteriaVal){
				   	    foreach($item->aka as $akaPerson){
							$data = array("criteriaType" =>"Person", "booleanValue" => "$boolVal", "criteriaVal" => "$akaPerson");
							array_push($formedArray, $data);
				   	    }
				   }
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
        $debug[] = "All parsed arguments were valid: " . $parsed_text;
        $debug[] = "Slideshow options were: " . $options;

		$url = "http://127.0.0.1:" . $xml_params->serverParams->displayServerPort;

        // Request that we set the slideshow properties

        $requestArray = array();        
        $optionRequest = xmlrpc_encode_request("setSlideshowProperties" , array($options));
        $parameterRequest = xmlrpc_encode_request("buildQuery" , array($parsed_text));

        $requestArray[] = $optionRequest;
        $requestArray[] = $parameterRequest;

        for ($x = 0; $x < count($requestArray); $x++ ){
        	$request = $requestArray[$x];
	        // Request that we query the database and get the files 
			$context = stream_context_create(array('http' => array(
			    'method' => "POST",
			    'header' => "Content-Type: text/xml",
			    'content' => $request
			)));

			try{
				$file = file_get_contents($url, false, $context);
			}catch (Exception $e){
				$exceptions[] = "It appears that the display server isn't running.";
				$retArray = array('exceptions' => $exceptions, 'debug' => $debug );
				echo json_encode($retArray);
				return;
			}
			$response = xmlrpc_decode($file);
			try{	
					$jsonArray = json_decode($response, true);
					$errs = $jsonArray['exceptions'];
					$debugs = $jsonArray['debug'];
					$debug = array_merge($debug, $debugs);
					$exceptions = array_merge($exceptions, $errs);
			}catch (Exception $e){
				$exceptions[] = $response;
			}

	    }

	}

	$debug[] = $_POST;
	$retArray = array('exceptions' => $exceptions, 'debug' => $debug );
	echo json_encode($retArray);

?>
