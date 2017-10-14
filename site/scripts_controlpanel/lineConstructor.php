<?php
header("Content-type: application/javascript");
?>  /*<!-- Do this because of https://stackoverflow.com/questions/23574306/executing-php-code-inside-a-js-file -->*/

function getNamesThenMakeLine(divNumber, lineDiv, jsonTemplate){

	numPhotosField = document.getElementById("minPhotos")
	minNumPhotos = numPhotosField.value

/*	 Load the database using PHP */

	$.ajax({
		type: 'POST',
		url: 'scripts_controlpanel/listPeople.php',
		data: {'minPhotos': minNumPhotos},
		success: function(data){
			console.log(data)
			decodedData = JSON.parse(data);
			people = decodedData['personNames']
			makeLineWithNames(divNumber, lineDiv, jsonTemplate, people)

	        exceptions = decodedData['exceptions']
	        for (i = 0; i < exceptions.length; i++){
	        	console.log("Error in deleting slideshow (modalScript.php): " + exceptions[i]);
	        }
	    }
	});
}

function makeLineWithNames(divNumber, lineDiv, jsonTemplate, personNames){

	/* jsonTemplate is a JSON of the form: {'selectType': <selection type>, 'binarySwitch': <switch value> , 'selection': <field val>} */

	console.log("no diff here")
	critMenuName = 'selectCriteriaMenu';
	binaryFieldName = 'binarySelect';
	firstSelectionFieldName = 'selectionDiv';


	/* Parse the json template */
	selectionValue = jsonTemplate['selectType']
	if (jsonTemplate.hasOwnProperty('binarySwitch')){
		binarySwitch = jsonTemplate['binarySwitch']
	}else{
		binarySwitch = null
	}
	if (jsonTemplate.hasOwnProperty('selection')){
		selection = jsonTemplate['selection']
	}else{
		selection = null
	}

	/* Set the first field type menu according to the JSON. */
	criteriaTypeField = critMenuName + divNumber
	document.getElementById(criteriaTypeField).value = selectionValue

	var subdiv2 = document.getElementById(binaryFieldName + divNumber)
	var subdiv3 = document.getElementById(firstSelectionFieldName + divNumber)

	/* Clear anything that was previously on the line */
	while (subdiv2.firstChild) {
	    subdiv2.removeChild(subdiv2.firstChild);
	}
	while (subdiv3.firstChild) {
	    subdiv3.removeChild(subdiv3.firstChild);
	}

	switch(selectionValue){
		case "Date Range":
			/* Replace the traditional binary select with two calendars.  */

			var startLabel = document.createElement('span')
			startLabel.id = "spacing"
			var startText = document.createTextNode("From: ")
			startLabel.className = "labelText"
			startLabel.appendChild(startText) 

			/*Calendar #1*/
			var i1 = document.createElement("input"); //input element, text
			i1.setAttribute('type',"text");
			i1.id = "binarySelectValues" + divNumber
			if (binarySwitch == null){
				i1.value = "<none>"
			}else{
				i1.value = binarySwitch
			}
			i1.className = "calendarBox"
			//i1.setAttribute('size','25')

			var s1 = document.createElement('button'); //input element, Submit button
			s1.id = "anchor1_" + divNumber
			var linkText = document.createTextNode("Select");
			s1.appendChild(linkText)
			s1.className = "calSelect"
			s1.setAttribute('type', 'button')
			//s1.style.height="30px"

			subdiv2.appendChild(startLabel)
			subdiv2.appendChild(i1);
			subdiv2.appendChild(s1);

			s1.onclick=function(){
				cal.select(i1,'anchor1_'+ divNumber,'MM/dd/yyyy')
			}

			var endLabel = document.createElement('span')
			var endText = document.createTextNode("To: ")
			endLabel.className = "labelText"
			endLabel.appendChild(endText)

			/* Calendar #2 */
			var i2 = document.createElement("input"); //input element, text
			i2.setAttribute('type',"text");
			i2.id = "selectionValue" + divNumber
			if (selection == null){
				i2.value = "<none>"
			}else{
				i2.value = selection
			}
			i2.className = "calendarBox"
			//i2.setAttribute('size','25')

			var s2 = document.createElement('button'); //input element, Submit button
			s2.id = "anchor2_" + divNumber
			var linkText = document.createTextNode("Select");
			s2.appendChild(linkText)
			s2.className = "calSelect"
			s2.setAttribute('type', 'button')
			//s2.style.height="30px"

			subdiv3.appendChild(endLabel)
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
			binarySelect.className = "binaryField"

			binarySelect.options.add(new Option("is", "is", true, true));
			binarySelect.options.add(new Option("is not", "is not", true, true));
			if (binarySwitch == null) {
				binarySelect.selectedIndex = 0
			}else{
				possVals = ['is', 'is not']
				if (possVals.indexOf(binarySwitch) < 0){
					console.log("Error in function constructSelectionLine: Unknown binary switch value for Person. ")
					binarySelect.selectedIndex = 0
				}else{
					binarySelect.value = binarySwitch
				}
			}

			var personSelect = document.createElement('select')
			personSelect.id = 'selectionValue' + divNumber
			subdiv3.appendChild(personSelect)
			personSelect.className = "dropdownOptions"

			for (var i = 0; i < personNames.length; i++){
				personSelect.options.add(new Option(personNames[i], personNames[i], true, true))
			}

			if (selection == null) {
				personSelect.selectedIndex = 0
			}else{
				if (personNames.indexOf(selection) < 0){
					console.log("Error in function constructSelectionLine: Unknown person selected for Person field. ")
					personSelect.selectedIndex = 0
				}else{
					personSelect.value = selection
				}
			}


			break;
		case "Year":

			var binarySelect = document.createElement('select')
			binarySelect.id = 'binarySelectValues' + divNumber
			subdiv2.appendChild(binarySelect)
			binarySelect.className = "binaryField"

			binarySelect.options.add(new Option("is", "is", true, true));
			binarySelect.options.add(new Option("is not", "is not", true, true));
			binarySelect.options.add(new Option("is before", "is before", true, true));
			binarySelect.options.add(new Option("is after", "is after", true, true));

			binarySelect.selectedIndex = 0
			if (binarySwitch == null) {
				binarySelect.selectedIndex = 0
			}else{
				possVals = ['is', 'is not', 'is before', 'is after']
				if (possVals.indexOf(binarySwitch) < 0){
					console.log("Error in function constructSelectionLine: Unknown binary switch value for Person. ")
					binarySelect.selectedIndex = 0
				}else{
					binarySelect.value = binarySwitch
				}
			}

			var yearSelect = document.createElement("INPUT")
			yearSelect.setAttribute("type", "text")
			yearSelect.id = 'selectionValue' + divNumber
			yearSelect.className = "dropdownOptions"
			yearSelect.onkeypress=function(){validateNumbers(event)}

			var regex = /^[0-9]+$/;
			if (selection != null && regex.test(selection) ){
				yearSelect.value = selection
			}

			subdiv3.appendChild(yearSelect)

			break;

		case "Month":

			var binarySelect = document.createElement('select')
			binarySelect.id = 'binarySelectValues' + divNumber
			subdiv2.appendChild(binarySelect)
			binarySelect.className = "binaryField"

			binarySelect.options.add(new Option("is", "is", true, true));
			binarySelect.options.add(new Option("is not", "is not", true, true));
			if (binarySwitch == null) {
				binarySelect.selectedIndex = 0
			}else{
				possVals = ['is', 'is not']
				if (possVals.indexOf(binarySwitch) < 0){
					console.log("Error in function constructSelectionLine: Unknown binary switch value for Person. ")
					binarySelect.selectedIndex = 0
				}else{
					binarySelect.value = binarySwitch
				}
			}

			var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

			var monthSelect = document.createElement('select')
			monthSelect.id = 'selectionValue' + divNumber
			subdiv3.appendChild(monthSelect)
			monthSelect.className = "dropdownOptions"

			for (var i = 0; i < months.length; i++){
				monthSelect.options.add(new Option(months[i], i + 1, true, true))
			}

			if (selection == null) {
				monthSelect.selectedIndex = 0
			}else{
				if (months.indexOf(selection) < 0){
					console.log("Error in function constructSelectionLine: Unknown person selected for Person field. ")
					monthSelect.selectedIndex = 0
				}else{
					/* VValues are numerical, so we need to choose the selected index rather than the month name. */
					monthSelect.selectedIndex = months.indexOf(selection)
				}
			}

			break;

		default:
			break;
	}
	//document.getElementsByClassName("accordion").style.height = "200px"

}

function validateNumbers(evt){
	var theEvent = evt || window.event;
	var key = theEvent.keyCode || theEvent.which;
	key = String.fromCharCode( key );
	var regex = /^[0-9]+$/;
	if( !regex.test(key) ) {
		theEvent.returnValue = false;
	if(theEvent.preventDefault) theEvent.preventDefault();
	}
}
