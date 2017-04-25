<?php

	if (isset($_GET['json'])){
		$jsonText = $_GET['json'];
	}else{
		echo("<script>console.log(\"Invalid JSON\")</script>");
		echo("Not ok");
		//exit;
	}

	//echo($jsonVal);

	$jsonArray = json_decode($jsonText, true);

	$allValid = 1;

	foreach ($jsonArray as $item){
		$type = $item['criteriaType'];
		$boolVal = $item['booleanValue'];
		$criteriaVal = $item['criteriaVal'];

	//["Date Range", "Person", "Year", "Month"]
		switch($type){
			case "Date Range":
				$date_start = date_parse($boolVal);
				$date_end = date_parse($criteriaVal);

				$validity = !($date_start["error_count"] || $date_end["error_count"]);

				if (!($validity)){
					echo("<script>console.log('$boolVal, $criteriaVal not valid in Date_range')</script>");
					echo "$boolVal, $criteriaVal not valid in Date_range\n";
					$allValid = 0;
				}
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
					echo("<script>console.log('$boolVal, $criteriaVal not valid in Person')</script>");
					echo("$boolVal, $criteriaVal not valid in Person");
					$allValid = 0;
				}
				break;
			case "Year":
				$valid1 = preg_match("/^is|is not|is before|is after$/i", $boolVal, $matches);

				$year = date_parse($criteriaVal);
				//print_r($year);

				if (!$valid1 or $year["error_count"]){
					echo("<script>console.log('$boolVal, $criteriaVal not valid in Year')</script>");
					echo "$boolVal, $criteriaVal not valid in Year";
					$allValid = 0;
				}
				break;
			case "Month":
				$valid1 = preg_match("/^is|is not$/i", $boolVal, $matches);
				$month = date_parse($criteriaVal);

				if (!$valid1 or $month["error_count"]){
					print_r($month);
					echo("<script>console.log('$boolVal, $criteriaVal not valid in Month')</script>");
					echo("$boolVal, $criteriaVal not valid in Month");
					$allValid = 0;
				}

				break;
		}

	}

	if (!$allValid){
		echo "Not all criteria in the JSON were valid. See console for more info.\n";
		echo 'var valid=0';
	}else{
		// We're good to go! All these have been validated to be good JSON. 
		shell_exec("python sendJSONtoSlideshow.py $jsonText");
	}
?>