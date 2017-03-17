<?php

	if (isset($_GET['json'])){
		$jsonVal = $_GET['json'];
	}else{
		echo("<script>console.log(\"Invalid JSON\")</script>");
	}

	if (isset($_GET['playlistName'])){
		$listName = $_GET['playlistName'];
	}else{
		echo("<script>console.log(\"Invalid List Name\")</script>");
	}


	try{
		$db = new SQLite3('../databases/photos_master.db');

		$results = $db->query('SELECT person_name FROM people');
		$people = array();
		while ($row = $results->fetchArray()) {
			if (!empty($row[0])){
				$people[] = $row[0];
			}
		}
	}catch(Exception $e){
		die('connection_unsuccessful: ' . $e->getMessage());
	}
	/*natcasesort ($people);

	$personNames = array();
	foreach ($people as $person){
		$personNames[] = $person;
	}*/

	$passedJSON = json_decode($jsonVal, true); /// True to make it return an array

	//echo("<script>console.log('$jsonVal')</script>");

	$allValid = 1;

	foreach ($passedJSON as $item){
		$type = $item['criteriaType'];
		$boolVal = $item['booleanValue'];
		$criteriaVal = $item['criteriaVal'];

	//["Date Range", "Person", "Year", "Month"]
		switch($type){
			case "Date Range":
				$valid1 = preg_match("/^\d+\/\d+\/\d+|<None>$/i", $boolVal, $matches);
				$valid2	= preg_match("/^\d+\/\d+\/\d+|<None>$/i", $criteriaVal, $matches2);
				//echo($valid1);
				//echo($valid2);
				if (!($valid1 and $valid2)){
					echo("<script>console.log('$boolVal, $criteriaVal not valid in Date_range')</script>");
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
					$allValid = 0;
				}
				break;
			case "Year":
				$valid1 = preg_match("/^is|is not|is before|is after$/i", $boolVal, $matches);
				$valid2 = preg_match("/^\d+$/i", $criteriaVal, $matches2);
				//echo($valid1);
				//echo($valid2);
				if (!($valid1 and $valid2)){
					echo("<script>console.log('$boolVal, $criteriaVal not valid in Year')</script>");
					$allValid = 0;
				}
				break;
			case "Month":
				$valid1 = preg_match("/^is|is not$/i", $boolVal, $matches);
				$valid2 = preg_match("/^January|February|march|april|may|june|july|august|september|october|november|december$/i", $criteriaVal, $matches2);
				//echo($valid1);
				//echo($valid2);
				if (!($valid1 and $valid2)){
					echo("<script>console.log('$boolVal, $criteriaVal not valid in Month')</script>");
					$allValid = 0;
				}

				break;
		}

	}

	if (!$allValid){
		echo 'Not all criteria in the JSON were valid. See console for more info.\n';
		echo 'var valid=0';
	}

	//echo(<script type="text/javascript">console.log("hey!")</script>)


	/*try{
		$db = new SQLite3('site_data.db');
	//INSERT INTO saved_parameters (Name, JSON) VALUES("hey", "there")
		$results = $db->query("INSERT INTO saved_parameters (Name, JSON) VALUES('$listName',  '$jsonVal') ");
		echo "INSERT INTO saved_parameters (Name, JSON) VALUES('$listName',  '$jsonVal') ";
	}catch(Exception $e){
		die('connection_unsuccessful: ' . $e->getMessage());
	}*/

?>