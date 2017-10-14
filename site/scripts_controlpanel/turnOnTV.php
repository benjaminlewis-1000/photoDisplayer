<?php


	$exceptions = array();
	$debug = array();

	// Set the error handler

	function exception_error_handler($errno, $errstr, $errfile, $errline ) {
	    throw new ErrorException($errstr, $errno, 0, $errfile, $errline);
	}
	set_error_handler("exception_error_handler");

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

	$allValid = 1;
/*
	$formedArray = array("On" => "True");

	$parsed_text =  json_encode($formedArray, JSON_UNESCAPED_SLASHES);*/
	/*
	if (!$allValid){
		$exceptions[] = "Not all criteria in the JSON were valid. See console for more info.";
	}else{*/
		// We're good to go! All these have been validated to be good JSON. 

	$url = "http://127.0.0.1:" . $xml_params->serverParams->displayServerPort;

    // Request that we set the slideshow properties

    $requestArray = array();        
    $optionRequest = xmlrpc_encode_request("turnOnTV" , array("On" => "True"));

    $requestArray[] = $optionRequest;

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

	$retArray = array('exceptions' => $exceptions, 'debug' => $debug );
	echo json_encode($retArray);

?>
