<?php
$doc = new DOMDocument();
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
echo $i2;
?>
