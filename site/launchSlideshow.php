<?php

	if (isset($_POST['json'])){
		$jsonText = $_POST['json'];
	}else if (isset($_GET['json'])){
		$jsonText = $_GET['json'];
	}else{
		echo("<script>console.log(\"Invalid JSON\")</script>");
		echo("Not ok");
		exit;
	}

	$xml_params = simplexml_load_file('C:\Users\Benjamin\Dropbox\Perl Code\photoDisplayer\config\params.xml') or die("Can't load this file!");
	//echo $xml_params->photoDatabase->tables->photoTable->Name . "<br>";
	$photoDBname = $xml_params->photoDatabase->fileName;
	//echo $photoDBname;

	$jsonArray = json_decode($jsonText, true);

	$allValid = 1;

	try{
		//echo '../databases/' . $photoDBname;
		$db = new SQLite3('../databases/' . $photoDBname);

		$results = $db->query('SELECT person_name FROM people');
		$people = array();
		while ($row = $results->fetchArray()) {
			if (!empty($row[0])){
				$people[] = $row[0];
			}
		}
	}catch(Exception $e){
		die('connection_unsuccessful: ' . $e->getMessage() . '. File = ' . '../databases/' . $photoDBname);
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
					echo "$boolVal, $criteriaVal not valid in Date_range\n";
					$allValid = 0;
				}

				## Reform the JSON so I know I'm passing it in a given state. 
				if ($boolVal == "<none>"){
					$start_formatted = "<None>";
				}else{
					$start_formatted = $date_start['year'] . '/' . str_pad($date_start['month'], 2, "0", STR_PAD_LEFT) . '/' . str_pad($date_start['day'], 2, "0", STR_PAD_LEFT);
				}
				if ($criteriaVal == "<none>"){
					$end_formatted = "<None>";
				}else{
					$end_formatted = $date_end['year'] . '/' . str_pad($date_end['month'], 2, "0", STR_PAD_LEFT) . '/' . str_pad($date_end['day'], 2, "0", STR_PAD_LEFT);
				}

				$data = array("criteriaType" =>"Date Range", "booleanValue" => $start_formatted, "criteriaVal" =>$end_formatted);
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
					echo("$boolVal, $criteriaVal not valid in Person");
					$allValid = 0;
				}

				$data = array("criteriaType" =>"Person", "booleanValue" => $boolVal, "criteriaVal" =>$criteriaVal);
				array_push($formedArray, $data);
				break;
			case "Year":
				$valid1 = preg_match("/^is|is not|is before|is after$/i", $boolVal, $matches);

				$yearValid = ctype_digit($criteriaVal);

				$year = $criteriaVal;

				if (!$valid1 or !$yearValid){
					echo "$boolVal, $criteriaVal not valid in Year";
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
				$data = array("criteriaType" =>"Year", "booleanValue" => $boolVal, "criteriaVal" =>$year);
				array_push($formedArray, $data);
				break;
			case "Month":
				$valid1 = preg_match("/^is|is not$/i", $boolVal, $matches);
				$month = $criteriaVal < 13 && $criteriaVal > 0 && ctype_digit($criteriaVal) ;

				if (!$valid1 or !$month){
					print_r($month);
					echo("$boolVal, $criteriaVal not valid in Month");
					$allValid = 0;
				}

				break;
		}

	}


	$parsed_text =  json_encode($formedArray, JSON_UNESCAPED_SLASHES);
	
	if (!$allValid){
		echo "Not all criteria in the JSON were valid. See console for more info.\n";
		echo 'var valid=0';
	}else{
		// We're good to go! All these have been validated to be good JSON. 
		echo "Good.";
		exec("python sendJSONtoSlideshow.py $parsed_text", $output, $ret);
		if (count($output) > 0 && $output[0] != "Success"){
			echo "Not a success... " . $output[0];
		}
	}

?>