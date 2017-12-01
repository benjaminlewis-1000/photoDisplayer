<?php

$a = '[{"criteriaType":"Date Range","booleanValue":"None","criteriaVal":"None"}]';
$a = '[{"criteriaType":"Year","booleanValue":"is after","criteriaVal":"2000"}]';
$a = '[{"criteriaType":"Year","booleanValue":"is","criteriaVal":"2015"}]';
$request = xmlrpc_encode_request("buildQuery" , array($a));
$context = stream_context_create(array('http' => array(
    'method' => "POST",
    'header' => "Content-Type: text/xml",
    'content' => $request
)));
	function exception_error_handler($errno, $errstr, $errfile, $errline ) {
	    throw new ErrorException($errstr, $errno, 0, $errfile, $errline);
	}
	set_error_handler("exception_error_handler");

try{
	$file = file_get_contents("http://127.0.0.1:8001", false, $context);
}catch (Exception $e){
	print_r("didn't work");
	exit;
}
$response = xmlrpc_decode($file);
$jsonArray = json_decode($response, true);
$errs = $jsonArray['errs'];
$debugs = $jsonArray['debug'];
if ( sizeof($errs) > 0 ) {
    trigger_error("xmlrpc: $response[faultString] ($response[faultCode])");
} else {
    print_r($response);
}
?>