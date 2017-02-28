<html>

<input type="hidden" value="0" id="divNumID" />

	<title>
		Picture Perfect Pi Photo Phrame
	</title>

<head>

<script src="jquery.js" type="text/javascript"></script>

	<style>
		/* Dropdown Button */
		.dropbtn {
		    background-color: #4CAF50;
		    color: white;
		    padding: 16px;
		    font-size: 16px;
		    border: none;
		    cursor: pointer;
		}

		/* Dropdown button on hover & focus */
		.dropbtn:hover, .dropbtn:focus {
		    background-color: #3e8e41;
		}

		/* The container <div> - needed to position the dropdown content */
		.dropdown {
		    position: relative;
		    display: inline-block;
		}

		/* Dropdown Content (Hidden by Default) */
		.dropdown-content {
		    display: none;
		    position: absolute;
		    background-color: #f9f9f9;
		    min-width: 160px;
		    box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
		    z-index: 1;
		}

		/* Links inside the dropdown */
		.dropdown-content a {
		    color: black;
		    padding: 12px 16px;
		    text-decoration: none;
		    display: block;
		}

/*
		#test{
			max-width: 1000px;
			margin 20px auto;
			padding: 10px;
			border: solid blue 2px;
			--webkit-box-sizing: border-box;float: 
			-moz-box-sizing: border-box;
			box-sizing: border-box;
		}
*/
		/* Change color of dropdown links on hover */
		.dropdown-content a:hover {background-color: #f1f1f1}

		/* Show the dropdown menu (use JS to add this class to the .dropdown-content container when the user clicks on the dropdown button) */
		.show {display:block;}
	</style>
</head>

<style type="text/css">

	.fieldParent{
		position:relative;
	    height: 70px;
	    max-width: 1000px;
	    /*border: 4px solid black;*/
		margin 20px auto;
		padding: 10px;
		border: solid blue 2px;
		--webkit-box-sizing: border-box;float: 
		-moz-box-sizing: border-box;
		box-sizing: border-box;
	}

	.fieldChild{
	    background-color: #FFFCE0;
	    color: #200954;
	    padding: 16px;
	    font-size: 16px;
	    border: 20px;
	    cursor: pointer;

	    left: 20px;
	    flex: 1;
	    height: 50px;
	    max-width: 200px;
	    float: left;
	    border-radius: 15px;

	    margin-left: 10px;
	    margin-right: 10px;

	    transition: 1.5s ease;
	    padding: 16px;
	    font-size: 16px;
	    border: none;
	    cursor: pointer;
	}

	.fieldChild:hover {
	    background-color: #eeefba;
	}
</style>


<!-- var text = jQuery.ajax({
    type: "POST",
    url: 'get_php.php',
    dataType: 'text',
    data: {functionname: 'add', arguments: [1, 2]},

    success: function (obj, textstatus) {
                  if( !('error' in obj) ) {
                      yourVariable = obj.result;
                  }
                  else {
                      console.log(obj.error);
                  }
            }

            
});

var myData = "";

function getData(response){
	myData = response
}

$.ajaxSetup({async:false})
$.post(
	'get_php.php', {},
	 function(data){
	 	getData(data)
	 	// Or here, I would create my field.
	 }
	)
console.log(myData) -->
<!-- New criteria line script -->

<script type="text/javascript">

	function addCriteriaLine(divOfFields){


		var mainDiv = document.getElementById(divOfFields);

  		var num = (document.getElementById('divNumID').value -1)+ 2;
  		document.getElementById('divNumID').value = num;

		var lineDiv = document.createElement('div');
		mainDiv.appendChild(lineDiv);

		lineDiv.id = 'criteriaBox' + num;
		lineDiv.className = "fieldParent";

		console.log(name)

		var subdiv1 = document.createElement('div');
			lineDiv.appendChild(subdiv1);
			subdiv1.id = 'typeBox' + num

			var select = document.createElement("select");


			var list = ["Date", "Person", "Year", "Month"]

			for (var i = 0; i < list.length; i++){
				select.options.add(new Option(list[i], list[i]));
			}

			select.className = "fieldChild";
			select.id = "selectCriteriaMenu" + num

			subdiv1.appendChild(select);

			select.addEventListener("change", function(){
				constructSelectionLine(num, lineDiv)
			})


		var subdiv2 = document.createElement('div')
		subdiv2.id = 'binarySelect' + num
		lineDiv.appendChild(subdiv2)

				var binarySelect = document.createElement('select')
				binarySelect.id = 'binarySelectValues' + num
				subdiv2.appendChild(binarySelect)
				binarySelect.className = "fieldChild"

		var subdiv3 = document.createElement("div")
		subdiv3.id = 'selectionValue' + num
		lineDiv.appendChild(subdiv3)



		constructSelectionLine(num, lineDiv)


		var removeSubdiv = document.createElement('div');
		lineDiv.appendChild(removeSubdiv);
		removeSubdiv.id = 'removeSubdiv' + num;

			var removeLineButton = document.createElement('BUTTON');
			removeLineButton.id = 'button';
			var t = document.createTextNode('Remove Criteria');
			removeLineButton.appendChild(t);

			removeLineButton.className = "fieldChild";
			removeSubdiv.appendChild(removeLineButton);

			var name = 'removeButton' + num
			var re = /.?(\d+)$/

			var num1 = re.exec(name)
			var value = num1[1]
			console.log(value)

			removeLineButton.onclick = function() { removeElement(removeSubdiv.id);};//removeElement//(subdiv3.id)

	}

	function constructSelectionLine(divNumber, lineDiv){

		//var lineDiv = document.getElementById('criteriaBox' + divNumber)
		<?php 
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
			natcasesort ($people);

			$personNames = array();
			foreach ($people as $person){
				$personNames[] = $person;
			}

			echo 'var personNames = ' . json_encode($personNames) . ';';
		?>

		subdiv1Select_ID = 'selectCriteriaMenu' + divNumber
		selectionValue = document.getElementById(subdiv1Select_ID).value

		console.log('Selection value is ' + selectionValue)
		console.log()

		switch(selectionValue){
			case "Date":

				var subdiv2 = document.getElementById('binarySelect' + divNumber)
				var subdiv3 = document.getElementById('selectionValue' + divNumber)

				while (subdiv2.firstChild) {
				    subdiv2.removeChild(subdiv2.firstChild);
				}
				while (subdiv3.firstChild) {
				    subdiv3.removeChild(subdiv3.firstChild);
				}

				var binarySelect = document.createElement('select')
				binarySelect.id = 'binarySelectValues' + divNumber
				subdiv2.appendChild(binarySelect)
				binarySelect.className = "fieldChild"

				binarySelect.options.add(new Option("is before", "is before", true, true));
				binarySelect.options.add(new Option("is after", "is after", true, true));



				break;
			case "Person":
				var subdiv2 = document.getElementById('binarySelect' + divNumber)
				var subdiv3 = document.getElementById('selectionValue' + divNumber)

				while (subdiv2.firstChild) {
				    subdiv2.removeChild(subdiv2.firstChild);
				}
				while (subdiv3.firstChild) {
				    subdiv3.removeChild(subdiv3.firstChild);
				}
				
				var binarySelect = document.createElement('select')
				binarySelect.id = 'binarySelectValues' + divNumber
				subdiv2.appendChild(binarySelect)
				binarySelect.className = "fieldChild"

				binarySelect.options.add(new Option("is", "is", true, true));
				binarySelect.options.add(new Option("is not", "is not", true, true));

				var personSelect = document.createElement('select')
				personSelect.id = 'personSelectValue' + divNumber
				subdiv2.appendChild(personSelect)
				personSelect.className = "fieldChild"

				for (var i = 0; i < personNames.length; i++){
					personSelect.options.add(new Option(personNames[i], personNames[i], true, true))
				}


				break;
			case "Year":
				var subdiv2 = document.getElementById('binarySelect' + divNumber)
				var subdiv3 = document.getElementById('selectionValue' + divNumber)


				while (subdiv2.firstChild) {
				    subdiv2.removeChild(subdiv2.firstChild);
				}
				while (subdiv3.firstChild) {
				    subdiv3.removeChild(subdiv3.firstChild);
				}

				var binarySelect = document.createElement('select')
				binarySelect.id = 'binarySelectValues' + divNumber
				subdiv2.appendChild(binarySelect)
				binarySelect.className = "fieldChild"


				var yearSelect = document.createElement('select')
				yearSelect.id = 'selectionValue' + divNumber
				lineDiv.appendChild(yearSelect)
				yearSelect.className = "fieldChild"


				break;
			case "Month":
				var subdiv2 = document.getElementById('binarySelect' + divNumber)
				var subdiv3 = document.getElementById('selectionValue' + divNumber)

				while (subdiv2.firstChild) {
				    subdiv2.removeChild(subdiv2.firstChild);
				}
				while (subdiv3.firstChild) {
				    subdiv3.removeChild(subdiv3.firstChild);
				}

				var binarySelect = document.createElement('select')
				binarySelect.id = 'binarySelectValues' + divNumber
				subdiv2.appendChild(binarySelect)
				binarySelect.className = "fieldChild"


				break;
		}
/*
		var subdiv2 = document.createElement('div');
		lineDiv.appendChild(subdiv2);

			var select2 = document.createElement('select');
			select2.options.add(new Option("m23", "adfds", true, true));
			select2.options.add(new Option("m562", "sdAU", true, true));
			select2.options.add(new Option("m356", "A2U", true, true));

			select2.className = "fieldChild";

			subdiv2.appendChild(select2);

			subdiv2.id = 'optionsBox' + divNumber
*/


	}

	function listenMetaCategory(subdivName){

		var re = /.?(\d+)/ // Match the number at the end of the ID. 
		var num1 = re.exec(subdivName)
		var value = num1[1]

		var newVal = document.getElementById("selectCriteriaMenu" + value).value

		console.log(newVal)
	}

	function removeElement(boxIDName){

		console.log(boxIDName)
		var re = /.?(\d+)/ // Match the number at the end of the ID. 
		var num1 = re.exec(boxIDName)
		console.log(num1)
		var value = num1[1]

		parentName = 'criteriaBox' + value
		console.log(parentName)
		var parent = document.getElementById(parentName);
		parent.remove();

/*
 if (childDiv == parentDiv) {
      alert("The parent div cannot be removed.");
 }
 else if (document.getElementById(childDiv)) {     
      var child = document.getElementById(childDiv);
      var parent = document.getElementById(parentDiv);
      parent.removeChild(child);
 }
 else {
      alert("Child div has already been removed or does not exist.");
      return false;
 }*/



  
	}

</script>
<!-- New criteria button formatting -->
<style type="text/css">
	#newCriteria{
		position:relative;
	    top: 3px;
	    left: 2px;
	    height: 50px;
	    width: 200px;
	    border-radius: 15px;

	    background-color: #4CAF50;
	    transition: 1.5s ease;
	    color: white;
	    padding: 16px;
	    font-size: 16px;
	    border: none;
	    cursor: pointer;

		box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
	}

	/* Dropdown button on hover & focus */
	#newCriteria:hover/*, #newCriteria:focus*/ {
	    background-color: #5e8eff;
	}


</style>

<body>

<div id=header>
<style type="text/css">
	#header{
		max_width:1000px;
	}
</style>
	<h1 style="text-align: center;"><span style="color: #ff9900;">Page 2</span></h1>
</div>
<!-- <div class="dropdown">
  <button onclick="myFunction()" class="dropbtn">Dropdown</button>
  <div id="myDropdown" class="dropdown-content">
    <a href="#">Link 1</a>
    <a href="#">Link 2</a>
    <a href="#">Link 3</a>
  </div>
</div> -->

<div id=newCriteriaDiv>
	<button id="newCriteria" onclick="addCriteriaLine('criteriaFieldsDiv')">New criteria</button>
</div>

<div id=fill>
<style type="text/css">
	#fill{
		height: 40px;
	}
</style>
</div>

<div id=criteriaFieldsDiv>
<style type="text/css">
	#criteriaFieldsDiv{
		background-color: #E3EBF7;
		max-width: 1000;
	}
</style>
</div>

<!-- <button id="newCriteria" onclick="adddiv()">Add Div</button>
<script type="text/javascript">
	
		function adddiv() {
	  
	   var divElement = document.createElement("div");  // private scope
	   divElement.id = "myDiv";  
	   divElement.style='width:100px;height:100px;border:1px solid black;'
	   divElement.className = "myDivClass";  
	   divElement.innerHTML = 'new div';  
	   document.body.appendChild(divElement);
	    var btn=document.getElementById('btn');
	   btn.addEventListener('click',function(){  // if this function is defined outside it won't work because divElement will be out of its scope
	         document.body.removeChild(divElement);
	   });
	   
	}
	window.addEventListener('load',adddiv);
</script> -->



<form id="form1" name="form1" method="post" action="<?php echo $PHP_SELF; ?>">
    <select Emp Name='NEW'>
    <option value="">--- Select ---</option>
    
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
    <input type="submit" name="Submit" value="Select" />
</form>

</body>
</html>