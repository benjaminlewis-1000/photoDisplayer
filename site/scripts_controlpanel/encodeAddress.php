<?php


    $errors = array();
    $warnings = array();
    $debug = array();

    // Set the error handler

    if (isset($_POST['requestedAddress'])){
        $requestedAddress = $_POST['requestedAddress'];
    }else if (isset($_GET['requestedAddress'])){
        $requestedAddress = $_GET['requestedAddress'];
    }else{
        $errors[] = 'No address requested in the POST';
        $retArray = array('errors' => $errors, 'debug' => $debug, 'warnings' => $warnings, 'debug' => $debug );
        echo json_encode($retArray);
        exit();
    }

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

    function exitOut(){

        $retArray = array('errors' => $errors, 'debug' => $debug, 'warnings' => $warnings, 'return' => array() );
        echo json_encode($retArray);
        exit();
    }
    /*

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
    }*/

   /* // Check if the requesting IP is in the network; if not, ignore and give a polite message in the debug.
    if (!ip_in_range($_SERVER['REMOTE_ADDR'], '192.168.0.0/16') && $_SERVER['REMOTE_ADDR'] != '::1'){
        $exceptions[] = "Computer is not on local network";
        $retArray = array('exceptions' => $exceptions, 'debug' => $debug );
        echo json_encode($retArray);
        exit;
    }
*/

    $parentDir = dirname_r(__FILE__, 3);

    try{
        $xml_params = simplexml_load_file($parentDir . '/config/params.xml');
    }catch(Exception $e){
        $errors[] = 'Can\'t load the parameter file...';
        $retArray = array('errors' => $errors, 'debug' => $debug, 'warnings' => $warnings, 'return' => array() );
        echo json_encode($retArray);
        exit;       
    }

/*
    $formedArray = array("On" => "True");

    $parsed_text =  json_encode($formedArray, JSON_UNESCAPED_SLASHES);*/
    /*
    if (!$allValid){
        $exceptions[] = "Not all criteria in the JSON were valid. See console for more info.";
    }else{*/
        // We're good to go! All these have been validated to be good JSON. 
    //echo getenv("GEOSERVER_NAME");

    // This environment variable 
    $serverName = getenv("GEOSERVER_NAME");
    if ( $serverName == ''){
        $errors[] = "The environment variable 'GEOSERVER_NAME' isn't set; this should point to the server name " .
        " of the docker container it is running in (or to localhost). ";
        $retArray = array('errors' => $errors, 'debug' => $debug, 'warnings' => $warnings, 'return' => array() );
        echo json_encode($retArray);
        exit();
    }

    $geocode_url = "http://" . $serverName . ":" . $xml_params->serverParams->geoServerPort . "/RPC2";

    // For Docker, you can either expose the port using -p HP:CP, which allows us to use the 
    // gateway, or else we can assign each container a hostname and a name. We can then use
    // the --link option between containers so that container B can know the routing information
    // of container A and have it added to its iptables automatically. Then we can do 
    // crazy urls like 'http://fred'.
    // See https://docs.docker.com/v17.09/engine/userguide/networking/default_network/configure-dns/ for details
    //$geocode_url = "http://fred:" . $xml_params->serverParams->geoServerPort . "/RPC2";

    // Request that we set the slideshow properties

    $requestArray = array();
    //$optionRequest = xmlrpc_encode_request("turnOnTV" , array("On" => "$requestedAddress"));
    //print_r($optionRequest);
    if (! extension_loaded('xmlrpc')){
        $errors[] = 'XMLRPC is not loaded on this server.';
        $retArray = array('errors' => $errors, 'debug' => $debug, 'warnings' => $warnings );
        echo json_encode($retArray);
        exit();
        exitOut();
    }

    $optionRequest = xmlrpc_encode_request("geoStringStandardize" , array("$requestedAddress"));

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
            $file = file_get_contents($geocode_url, false, $context);
        }catch (Exception $e){
            $errors[] = "It appears that the geo server isn't running.";
            $retArray = array('errors' => $errors, 'debug' => $debug, 'warnings' => $warnings, 'return' => array() );
            echo json_encode($retArray);
            exit();
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

    $retArray = array('errors' => $errors, 'debug' => $debug, 'warnings' => $warnings, 'return' => $response );
    echo json_encode($retArray);

?>
