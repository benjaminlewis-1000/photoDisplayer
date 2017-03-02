<html>

<input type="hidden" value="0" id="divNumID" />

	<title>
		Picture Perfect Pi Photo Phrame
	</title>

<head>

<!-- Style sheet from the javascript toolbox library demo page, http://www.mattkruse.com/javascript/calendarpopup/index.html -->
<link rel="stylesheet" type="text/css" href="css/cal_styles.css">

<script src="js/jquery.js" type="text/javascript"></script>
<script src="js/popupWindow.js"></script>

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
	    min-height: 70px;
	    max-width: 1000px;
	    /*border: 4px solid black;*/
		margin 20px auto;
		padding: 10px;
		border: solid blue 2px;
		--webkit-box-sizing: border-box;
		-moz-box-sizing: border-box;
		box-sizing: border-box;
		overflow: hidden
	}

	.fieldChild{
	    background-color: #FFFCE0;
	    color: #200954;
	    border: 20px;
	    cursor: pointer;

	    font-size: 16px;
	    text-align: center;

	    left: 20px;
	    flex: 1;
	    height: 50px;
	    border-radius: 15px;

	    margin-left: 10px;
	    margin-right: 10px;
	    /*margin-top: 10px;
	    margin-bottom: 10px;*/

	    transition: 1.5s ease;
	    float:left;
	}

	.fieldChildColorless{
	   /* padding: 16px;*/

	    border: 20px;
	    cursor: pointer;

	    font-size: 20px;
	    text-align: center;

	    left: 20px;
	    flex: 1;
	    height: 50px;
	    border-radius: 15px;

	    margin-left: 10px;
	    margin-right: 10px;
	  /*  margin-top: 10px;
	    margin-bottom: 10px;*/

	    transition: 1.5s ease;
	    float:left;
	}

	.calendarBox{
	   /* padding: 16px;*/

	    border: 20px;
	    cursor: pointer;

	    font-size: 20px;
	    text-align: center;
	    width:150px;

	    left: 20px;
	    flex: 1;
	    height: 50px;
	    border-radius: 15px;

	    margin-left: 10px;
	    margin-right: -10px;
	    /*margin-top: 10px;
	    margin-bottom: 10px;*/

	    transition: 1.5s ease;
	    float:left;
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

		var subdiv1 = document.createElement('div');
			lineDiv.appendChild(subdiv1);
			subdiv1.id = 'typeBox' + num

			var select = document.createElement("select");


			var list = ["Date Range", "Person", "Year", "Month"]

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
		subdiv3.id = 'selectionDiv' + num
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
			//console.log(value)

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

		criteriaTypeField = 'selectCriteriaMenu' + divNumber
		selectionValue = document.getElementById(criteriaTypeField).value

		var subdiv2 = document.getElementById('binarySelect' + divNumber)
		var subdiv3 = document.getElementById('selectionDiv' + divNumber)

		while (subdiv2.firstChild) {
		    subdiv2.removeChild(subdiv2.firstChild);
		}
		while (subdiv3.firstChild) {
		    subdiv3.removeChild(subdiv3.firstChild);
		}

		switch(selectionValue){
			case "Date Range":
				/* Replace the traditional binary select with two calendars.  */

				var startLabel = document.createElement('p')
				var startText = document.createTextNode("From: ")
				startLabel.appendChild(startText)

				/*Calendar #1*/
				var i1 = document.createElement("input"); //input element, text
				i1.setAttribute('type',"text");
				i1.id = "binarySelectValues" + divNumber
				i1.value = "<none>"
				i1.className = "calendarBox"
				//i1.setAttribute('size','25')

				var s1 = document.createElement('button'); //input element, Submit button
				s1.id = "anchor1_" + divNumber
				var linkText = document.createTextNode("select");
				s1.appendChild(linkText)
				s1.className = "fieldChild"
				s1.setAttribute('type', 'button')
				//s1.style.height="30px"

				//subdiv2.appendChild(startLabel)
				subdiv2.appendChild(i1);
				subdiv2.appendChild(s1);

				s1.onclick=function(){
					cal.select(i1,'anchor1_'+ divNumber,'MM/dd/yyyy')
				}

				var endLabel = document.createElement('p')
				var endText = document.createTextNode("To: ")
				endLabel.appendChild(endText)

				/* Calendar #2 */
				var i2 = document.createElement("input"); //input element, text
				i2.setAttribute('type',"text");
				i2.id = "selectionValue" + divNumber
				i2.value = "<none>"
				i2.className = "calendarBox"
				//i2.setAttribute('size','25')

				var s2 = document.createElement('button'); //input element, Submit button
				s2.id = "anchor2_" + divNumber
				var linkText = document.createTextNode("select");
				s2.appendChild(linkText)
				s2.className = "fieldChild"
				s2.setAttribute('type', 'button')
				//s2.style.height="30px"

				//subdiv3.appendChild(endLabel)
				subdiv3.appendChild(i2);
				subdiv3.appendChild(s2);

				s2.onclick=function(){
					cal.select(i2,'anchor2_'+ divNumber,'MM/dd/yyyy')
				}

				break

			case "Person":
				var binarySelect = document.createElement('select')
				binarySelect.id = 'binarySelectValues' + divNumber
				subdiv2.appendChild(binarySelect)
				binarySelect.className = "fieldChild"

				binarySelect.options.add(new Option("is", "is", true, true));
				binarySelect.options.add(new Option("is not", "is not", true, true));
				binarySelect.selectedIndex = 0

				var personSelect = document.createElement('select')
				personSelect.id = 'selectionValue' + divNumber
				subdiv3.appendChild(personSelect)
				personSelect.className = "fieldChild"

				for (var i = 0; i < personNames.length; i++){
					personSelect.options.add(new Option(personNames[i], personNames[i], true, true))
				}
				personSelect.selectedIndex = 0


				break;
			case "Year":

				var binarySelect = document.createElement('select')
				binarySelect.id = 'binarySelectValues' + divNumber
				subdiv2.appendChild(binarySelect)
				binarySelect.className = "fieldChild"

				binarySelect.options.add(new Option("is", "is", true, true));
				binarySelect.options.add(new Option("is not", "is not", true, true));
				binarySelect.options.add(new Option("is before", "is before", true, true));
				binarySelect.options.add(new Option("is after", "is after", true, true));

				binarySelect.selectedIndex = 0

				var yearSelect = document.createElement("INPUT")
				yearSelect.setAttribute("type", "text")
				yearSelect.id = 'selectionValue' + divNumber
				yearSelect.className = "fieldChildColorless"
				yearSelect.onkeypress=function(){validateNumbers(event)}

				subdiv3.appendChild(yearSelect)

				break;

			case "Month":

				var binarySelect = document.createElement('select')
				binarySelect.id = 'binarySelectValues' + divNumber
				subdiv2.appendChild(binarySelect)
				binarySelect.className = "fieldChild"

				binarySelect.options.add(new Option("is", "is", true, true));
				binarySelect.options.add(new Option("is not", "is not", true, true));
				binarySelect.selectedIndex = 0

				var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

				var monthSelect = document.createElement('select')
				monthSelect.id = 'selectionValue' + divNumber
				subdiv3.appendChild(monthSelect)
				monthSelect.className = "fieldChild"

				for (var i = 0; i < months.length; i++){
					monthSelect.options.add(new Option(months[i], months[i], true, true))
				}
				monthSelect.selectedIndex = 0


				break;
		}

	}

	function validateNumbers(evt){
		var theEvent = evt || window.event;
		var key = theEvent.keyCode || theEvent.which;
		key = String.fromCharCode( key );
		var regex = /[0-9]/;
		if( !regex.test(key) ) {
			theEvent.returnValue = false;
		if(theEvent.preventDefault) theEvent.preventDefault();
		}
	}

	function listenMetaCategory(subdivName){

		var re = /.?(\d+)/ // Match the number at the end of the ID. 
		var num1 = re.exec(subdivName)
		var value = num1[1]

		var newVal = document.getElementById("selectCriteriaMenu" + value).value

	}

	function removeElement(boxIDName){

		//console.log(boxIDName)
		var re = /.?(\d+)/ // Match the number at the end of the ID. 
		var num1 = re.exec(boxIDName)
		//console.log(num1)
		var value = num1[1]

		parentName = 'criteriaBox' + value
		//console.log(parentName)
		var parent = document.getElementById(parentName);
		parent.remove();
  
	}

</script>

<script type="text/javascript">
	function saveCriteria(){
		// Loop through and get all the data. 
		var numElements = document.getElementById('divNumID').value + 1; // +1 so we have typical for loop indexing
		for (var i = 0; i < numElements; i++){
			criteriaTypeField = 'selectCriteriaMenu' + i
			if ($("#" + criteriaTypeField).length > 0){
				criteriaType = document.getElementById(criteriaTypeField).value
				booleanValue = document.getElementById('binarySelectValues' + i).value
				criteriaValue = document.getElementById('selectionValue' + i).value

				console.log(criteriaType + " " + booleanValue + " " + criteriaValue)
			}
		}
	}
</script>
<!-- New criteria button formatting -->
<style type="text/css">
	.taskButton{
		position:relative;
	    top: 3px;
	    left: 20px;
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
	.taskButton:hover/*, #newCriteria:focus*/ {
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
	<button id="newCriteria" class="taskButton" onclick="addCriteriaLine('criteriaFieldsDiv')">New criteria</button>
	<button id="saveCriteria" class="taskButton" onclick="saveCriteria()">Save criteria</button>
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
	<script language="JavaScript" src="js/CalendarPopup.js"></script>
	<script type="text/javascript" src="js/date.js"></script>
	<script type="text/javascript" src="js/AnchorPosition.js"></script>


<div id="testdiv1" style="position:absolute;visibility:hidden;background-color:white;layer-background-color:white;"></div>
<!-- <form name="example">
<input type="text" name="date1" value="" size="25">
<a href="#">Select</a>
</form> -->
<!-- <script>
	var cal = new CalendarPopup("testdiv1");
		cal.showNavigationDropdowns();
		cal.setCssPrefix("Test");
		cal.setYearSelectStartOffset(10);
</script> -->
<!-- 
	<script>
	var f = document.createElement("form");

	var i = document.createElement("input"); //input element, text
	i.setAttribute('type',"text");
	i.id="date1"
	i.setAttribute('size','25')

	var s = document.createElement('button'); //input element, Submit button
	s.id="anchor3"
	var linkText = document.createTextNode("select");
	s.appendChild(linkText)

	f.appendChild(i);
	f.appendChild(s);
	f.id="example3"
	document.getElementsByTagName('body')[0].appendChild(f);

	s.onclick=function(){
		cal.select(document.forms['example3'].date1,'anchor3','MM/dd/yyyy')
	}

</script> -->

	<script type="text/javascript">
		var cal = new CalendarPopup("testdiv1");
		cal.showNavigationDropdowns();
		cal.setCssPrefix("Test");
		cal.setYearSelectStartOffset(10);
	</script>

<!-- <form name="example">
<input type="text" name="date1" value="" size="25">
<a href="#" onclick="cal.select(document.forms['example'].date1,'anchor1','MM/dd/yyyy'); return false;" name="anchor1" id="anchor1">select</a>
</form>
 -->
</body>
</html>