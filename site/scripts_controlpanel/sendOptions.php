<?php

	$exceptions = array();
	$debug = array();

	function dirname_r($path, $count=1){
	    if ($count > 1){
	       return dirname(dirname_r($path, --$count));
	    }else{
	       return dirname($path);
	    }
	}

	$parentDir = dirname_r(__FILE__, 3);


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

	try{
		$xml_params = simplexml_load_file($parentDir . '/config/params.xml');
	}catch(Exception $e){
		$exceptions[] = 'Can\'t load the parameter file...';
		$retArray = array('exceptions' => $exceptions, 'debug' => $debug );
		echo json_encode($retArray);
		exit;		
	}

    $request = xmlrpc_encode_request("setSlideshowProperties" , array($options));
	$context = stream_context_create(array('http' => array(
	    'method' => "POST",
	    'header' => "Content-Type: text/xml",
	    'content' => $request
	)));
	function exception_error_handler($errno, $errstr, $errfile, $errline ) {
	    throw new ErrorException($errstr, $errno, 0, $errfile, $errline);
	}
	set_error_handler("exception_error_handler");
	$url = "http://127.0.0.1:" . $xml_params->serverParams->displayServerPort;

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
	
	$retArray = array('exceptions' => $exceptions, 'debug' => $debug );
	echo json_encode($retArray);

?>