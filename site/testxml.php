<?php
/*$doc = new DOMDocument();
$doc->load('/home/pi/photoDisplayer/config/params.xml');
//echo $doc->saveXML();
echo "done";
//print_r($doc);
$item = $doc->getElementsByTagName('ostypes');
//var_dump( $item);
foreach($item as $i){
  $win = $i->getElementsByTagName('windowsType');
  $winType = $win->item(0)->nodeValue;
  echo $winType;
}
$i2 = $item->item(0)->getElementsByTagName('windowsType')->item(0)->nodeValue;
echo $i2;*/

function exception_error_handler($errno, $errstr, $errfile, $errline ) {
    throw new ErrorException($errstr, $errno, 0, $errfile, $errline);
}
set_error_handler("exception_error_handler");

			$parentDir = dirname(__FILE__,2);
echo $parentDir;
			$xml_params = simplexml_load_file($parentDir . '/config/params.xml') or die("Can't load this file!");
			//echo $xml_params->photoDatabase->tables->photoTable->Name . "<br>";
			$photoDBname = $xml_params->photoDatabase->fileName;
	$photoDBpath = $parentDir . '/databases/' . $xml_params->photoDatabase->fileName;
			echo $photoDBname;

			/*$parentDir = dirname(__FILE__, 2);
			$xml_params = simplexml_load_file($parentDir . '/config/params.xml') or die("Can't load this file!");
			//echo $xml_params->photoDatabase->tables->photoTable->Name . "<br>";
			$photoDBpath = $parentDir . '/databases/' . $xml_params->photoDatabase->fileName;*/
			echo("<script>console.log('hey there!'); </script>");

			try{
				$db = new SQLite3($photoDBpath);

				$results = $db->query('SELECT person_name FROM people');
				$people = array();
				while ($row = $results->fetchArray()) {
					if (!empty($row[0])){
						$people[] = $row[0];
					}
				}
			}catch(Exception $e){
				//echo "<script>console.log( 'meh');</script>";
				echo("'<script> console.log(\"meh\"); </script>'");
				//
			}
			/*
			if (file_exists($photoDBpath) ){
				echo "Exists!";
			}else{
				echo "File " . $photoDBpath . " not found. :( ";
			}*/
?>
