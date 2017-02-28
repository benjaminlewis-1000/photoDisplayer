 <html>

Hey there!
<select>
 <?php 

	try{
		$db = new SQLite3('photos_master.db');

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
	natcasesort ($people);

	foreach ($people as $person){
		echo "<option value=\"" . $person . "\">" . $person . "</option>\n";
	}

    ?>
</select>
    </html>