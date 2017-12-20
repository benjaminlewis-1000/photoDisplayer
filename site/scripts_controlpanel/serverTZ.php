<?php
   $timezone = date_default_timezone_get();

   $time = new \DateTime('now', new DateTimeZone($timezone));
   $timezoneOffset = $time->format('P');
   echo $timezoneOffset;
?>
