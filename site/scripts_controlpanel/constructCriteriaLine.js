function constructOrUpdateCriteriaLine(divOfFields, isNew, divNumber, criteriaType, binaryValue, selectionValue){

	var mainDiv = document.getElementById(divOfFields);
	var criteriaTypes = ["Date Range", "Person", "Year", "Month", "Special"]

	if (isNew){
  		var divNumber = (document.getElementById('divNumID').value - 1)+ 2;
  		document.getElementById('divNumID').value = divNumber;

		var lineDiv = document.createElement('div');
		lineDiv.id = 'criteriaBox' + divNumber;
		lineDiv.className = "fieldParent";
		mainDiv.appendChild(lineDiv);

		// Create and classify the span for the criteria box
		var span_criteria_type = document.createElement('span');
		span_criteria_type.id = 'typeBox' + divNumber
		lineDiv.appendChild(span_criteria_type);

		// Create and classify the select box
		var select_criteria_type = document.createElement("select");
		span_criteria_type.appendChild(select_criteria_type);
		select_criteria_type.className = "criteriaType";
		select_criteria_type.id = 'selectCriteriaMenu' + divNumber

		// Populate the list with the various types of criteria
		for (var i = 0; i < criteriaTypes.length; i++){
			select_criteria_type.options.add(new Option(criteriaTypes[i], criteriaTypes[i]));
		}


		if (criteriaTypes.indexOf(criteriaType) < 0){
			console.log("Error in choosing criteria type; selecting default. ")
			select_criteria_type.selectedIndex = 0
		}else{
			select_criteria_type.value = criteriaType
		}

		//select_criteria_type.value = criteriaType

		// Add a listener - if the first field (type box) changes, then change the rest of the line accordingly.
		select_criteria_type.addEventListener("change", function(){
			// Get the new field, create a construct for it, and construct the selection line again. 
			classType = select_criteria_type.value;
			constructOrUpdateCriteriaLine(divOfFields, 0, divNumber, classType, null, null);
		})

		// Make the binary selection field
		var span_qualifier = document.createElement('span')
		span_qualifier.id = 'binarySelect' + divNumber
		lineDiv.appendChild(span_qualifier)

		// Make the criteria choice field
		var span_filter_criteria = document.createElement('span')
		span_filter_criteria.id = 'selectionDiv' + divNumber
		lineDiv.appendChild(span_filter_criteria)

		// Create the remove button
		var removeSpan = document.createElement('span');
		lineDiv.appendChild(removeSpan);
		removeSpan.id = 'removeSubdiv' + divNumber;

		var removeLineButton = document.createElement('button');
		removeLineButton.id = 'button';
		removeLineButton.innerText = "Remove";

		removeLineButton.className = "fieldChild";
		removeSpan.appendChild(removeLineButton);

		removeLineButton.onclick = function() { 
			removeElement(lineDiv.id);
		};

		// Grow the accordion if it is in display mode.
		var acc = document.getElementById("criteriaAccordion");
	    var panel = acc.nextElementSibling;
	    if (acc.className == "accordion"){  
	    // Toggle the criteria div on; it's clearly advantageous to see what you're adding.
	    	acc.classList.toggle("active");
	    }
	    if (acc.className == "accordion active"){
		    panel.style.maxHeight = panel.scrollHeight + "px";
		}

	}else{
		lineDiv = document.getElementById('criteriaBox' + divNumber)

		select_criteria_type = document.getElementById('selectCriteriaMenu' + divNumber)
		var span_qualifier = document.getElementById('binarySelect' + divNumber)
		var span_filter_criteria = document.getElementById('selectionDiv' + divNumber)


		if (criteriaTypes.indexOf(criteriaType) < 0){
			console.log("Error in choosing criteria type; selecting default. ")
			select_criteria_type.selectedIndex = 0
		}else{
			select_criteria_type.value = criteriaType
		}

		while (span_qualifier.firstChild) {
		    span_qualifier.removeChild(span_qualifier.firstChild);
		}
			while (span_filter_criteria.firstChild) {
		    span_filter_criteria.removeChild(span_filter_criteria.firstChild);
		}
	}


	switch(select_criteria_type.value){
		case "Date Range":
			/* Replace the traditional binary select with two calendars.  */

			var startLabel = document.createElement('span')
			startLabel.id = "spacing"
			startLabel.innerHTML = "From:"
			startLabel.className = "labelText"

			/*Calendar #1*/
			var i1 = document.createElement("input"); //input element, text
			i1.setAttribute('type',"text");
			i1.id = "binarySelectValues" + divNumber
			if (binaryValue == null){
				i1.value = "<none>"
			}else{
				i1.value = binaryValue
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

			span_qualifier.appendChild(startLabel)
			span_qualifier.appendChild(i1);
			span_qualifier.appendChild(s1);

			s1.onclick=function(){
				cal.select(i1,'anchor1_'+ divNumber,'MM/dd/yyyy')
			}

			var endLabel = document.createElement('span')
			endLabel.innerHTML = "To:"
			endLabel.className = "labelText"

			/* Calendar #2 */
			var i2 = document.createElement("input"); //input element, text
			i2.setAttribute('type',"text");
			i2.id = "selectionValue" + divNumber
			if (selectionValue == null){
				i2.value = "<none>"
			}else{
				i2.value = selectionValue
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

			span_filter_criteria.appendChild(endLabel)
			span_filter_criteria.appendChild(i2);
			span_filter_criteria.appendChild(s2);

			s2.onclick=function(){
				cal.select(i2,'anchor2_'+ divNumber,'MM/dd/yyyy')
			}

			break

		case "Person":
			var binarySelect = document.createElement('select')
			binarySelect.id = 'binarySelectValues' + divNumber
			span_qualifier.appendChild(binarySelect)
			binarySelect.className = "binaryField"

			binarySelect.options.add(new Option("is", "is", true, true));
			binarySelect.options.add(new Option("is not", "is not", true, true));
			if (binaryValue == null) {
				binarySelect.selectedIndex = 0
			}else{
				possVals = ['is', 'is not']
				if (possVals.indexOf(binaryValue) < 0){
					console.log("Error in function constructOrUpdateCriteriaLine: Unknown binary switch value for Person. ")
					binarySelect.selectedIndex = 0
				}else{
					binarySelect.value = binaryValue
				}
			}

			var personSelect = document.createElement('select')
			personSelect.id = 'selectionValue' + divNumber
			span_filter_criteria.appendChild(personSelect)
			personSelect.className = "dropdownOptions"


			numPhotosField = document.getElementById("minPhotos")
			minNumPhotos = numPhotosField.value
			console.debug(personNames)

/*
			for (var i = 0; i < personNames.length; i++){
				personSelect.options.add(new Option(personNames[i], personNames[i], true, true))
			}

			if (selectionValue == null) {
				personSelect.selectedIndex = 0
			}else{
				if (personNames.indexOf(selectionValue) < 0){
					console.log("Error in function constructOrUpdateCriteriaLine: Unknown person selected for Person field. ")
					personSelect.selectedIndex = 0
				}else{
					personSelect.value = selectionValue
				}
			}
*/


			break;
		case "Year":

			var binarySelect = document.createElement('select')
			binarySelect.id = 'binarySelectValues' + divNumber
			span_qualifier.appendChild(binarySelect)
			binarySelect.className = "binaryField"

			binarySelect.options.add(new Option("is", "is", true, true));
			binarySelect.options.add(new Option("is not", "is not", true, true));
			binarySelect.options.add(new Option("is before", "is before", true, true));
			binarySelect.options.add(new Option("is after", "is after", true, true));

			binarySelect.selectedIndex = 0
			if (binaryValue == null) {
				binarySelect.selectedIndex = 0
			}else{
				possVals = ["is", "is not", "is before", "is after"]
				if (possVals.indexOf(binaryValue) < 0){
					console.log("Error in function constructOrUpdateCriteriaLine: Unknown binary switch value for Person. ")
					binarySelect.selectedIndex = 0
				}else{
					binarySelect.value = binaryValue
				}
			}

			var yearSelect = document.createElement("INPUT")
			yearSelect.setAttribute("type", "text")
			yearSelect.id = 'selectionValue' + divNumber
			yearSelect.className = "dropdownOptions"
			yearSelect.onchange=function(){
				var regex = /^[0-9]+$/;
				if( !regex.test(yearSelect.value) ) {
					yearSelect.value= ""
				}
			}

			var regex = /^[0-9]+$/;
			if (selectionValue != null && regex.test(selectionValue) ){
				yearSelect.value = selectionValue
			}

			span_filter_criteria.appendChild(yearSelect)

			break;

		case "Month":

			var binarySelect = document.createElement('select')
			binarySelect.id = 'binarySelectValues' + divNumber
			span_qualifier.appendChild(binarySelect)
			binarySelect.className = "binaryField"

			binarySelect.options.add(new Option("is", "is", true, true));
			binarySelect.options.add(new Option("is not", "is not", true, true));
			if (binaryValue == null) {
				binarySelect.selectedIndex = 0
			}else{
				possVals = ['is', 'is not']
				if (possVals.indexOf(binaryValue) < 0){
					console.log("Error in function constructOrUpdateCriteriaLine: Unknown binary switch value for Person. ")
					binarySelect.selectedIndex = 0
				}else{
					binarySelect.value = binaryValue
				}
			}

			var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

			var monthSelect = document.createElement('select')
			monthSelect.id = 'selectionValue' + divNumber
			span_filter_criteria.appendChild(monthSelect)
			monthSelect.className = "dropdownOptions"

			for (var i = 0; i < months.length; i++){
				monthSelect.options.add(new Option(months[i], i + 1, true, true))
			}

			if (selectionValue == null) {
				monthSelect.selectedIndex = 0
			}else{
				if (months.indexOf(selectionValue) < 0){
					console.log("Error in function constructOrUpdateCriteriaLine: Unknown person selected for Person field. ")
					monthSelect.selectedIndex = 0
				}else{
					/* VValues are numerical, so we need to choose the selected index rather than the month name. */
					monthSelect.selectedIndex = months.indexOf(selectionValue)
				}
			}

			break;

		default:
			break;
	}

}
