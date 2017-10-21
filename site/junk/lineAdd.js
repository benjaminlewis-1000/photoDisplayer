

var critMenuName = 'selectCriteriaMenu';
var emptyCal = '<none>'


	function addCriteriaLine(){

		divOfFields = arguments[0];
		construct = {'selectType': 'Date Range'}
		if (arguments.length > 1){
			criteria = arguments[1];
			construct = {'selectType': criteria['criteriaType'], 'binarySwitch': criteria['booleanValue'], 'selection': criteria['criteriaVal']}
		}

		// Get the value of a variable for counting off divs and increment it. 
  		var num = (document.getElementById('divNumID').value - 1)+ 2;
  		document.getElementById('divNumID').value = num;

  		// Select the root div for the criteria selection, then append another div with name 'criteriaBox<n>'.
  		// Inside the criteriaBox, put in a criteria type box, a select box 
		var mainDiv = document.getElementById(divOfFields);
		var lineDiv = document.createElement('div');
		var span_criteria_type = document.createElement('span');
		var select_criteria_type = document.createElement("select");
		// Tack on the div of the line, then append the subdiv 
		mainDiv.appendChild(lineDiv);
		lineDiv.appendChild(span_criteria_type);
		span_criteria_type.appendChild(select_criteria_type);

		lineDiv.id = 'criteriaBox' + num;
		lineDiv.className = "fieldParent";
		span_criteria_type.id = 'typeBox' + num

		var list = ["Date Range", "Person", "Year", "Month"]

		for (var i = 0; i < list.length; i++){
			select_criteria_type.options.add(new Option(list[i], list[i]));
		}

		select_criteria_type.className = "criteriaType";
		select_criteria_type.id = critMenuName + num

		// Add a listener - if the first field (type box) changes, then change the rest of the line accordingly.
		select_criteria_type.addEventListener("change", function(){
			// Get the new field, create a construct for it, and construct the selection line again. 
			classType = select_criteria_type.value;
			construct = {'selectType': classType}
			getNamesThenMakeLine(num, lineDiv, construct)
		})

		var subdiv_qualifier = document.createElement('span')
		subdiv_qualifier.id = 'binarySelect' + num
		lineDiv.appendChild(subdiv_qualifier)

		var subdiv_filter_criteria = document.createElement('span')
		subdiv_filter_criteria.id = 'selectionDiv' + num
		lineDiv.appendChild(subdiv_filter_criteria)

		getNamesThenMakeLine(num, lineDiv, construct)



		var removeSpan = document.createElement('span');
		lineDiv.appendChild(removeSpan);
		removeSpan.id = 'removeSubdiv' + num;

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
	}
/*
	function listenMetaCategory(subdivName){

		var re = /.?(\d+)/ // Match the number at the end of the ID. 
		var num1 = re.exec(subdivName)
		var value = num1[1]

		var newVal = document.getElementById(critMenuName + value).value

	}*/
