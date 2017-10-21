

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



		var removeSubdiv = document.createElement('span');
		lineDiv.appendChild(removeSubdiv);
		removeSubdiv.id = 'removeSubdiv' + num;

		var removeLineButton = document.createElement('button');
		removeLineButton.id = 'button';
		removeLineButton.innerText = "Remove";

		removeLineButton.className = "fieldChild";
		removeSubdiv.appendChild(removeLineButton);

		removeLineButton.onclick = function() { 
			removeElement(removeSubdiv.id);
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

	function addScheduleLine(){

		// Get the appropriate variable and increment it.
  		var num = (document.getElementById('scheduleNumID').value - 1)+ 2;
  		document.getElementById('scheduleNumID').value = num;

  		console.log(num);

		divOfFields = arguments[0];
		var mainDiv = document.getElementById(divOfFields);
		var lineDiv = document.createElement('div');

		mainDiv.appendChild(lineDiv);

		// Day of week drop-down button
		var span_day_of_week = document.createElement('span');
		var select_day_of_week = document.createElement('select');
		lineDiv.appendChild(span_day_of_week);
		span_day_of_week.appendChild(select_day_of_week);

		days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
		for (var i = 0; i < days.length; i++){
			select_day_of_week.options.add(new Option(days[i], days[i]));
		}

		lineDiv.className = "fieldParent";
		select_day_of_week.className = "criteriaType";
		lineDiv.id = 'scheduleBox' + num;
		select_day_of_week.id = 'dayOfWeekBox' + num;

		// Put the "From" label on the time 
		var startLabel = document.createElement('span')
		startLabel.innerHTML="From:"
		startLabel.className = "labelText"
		lineDiv.appendChild(startLabel)

		// Start time input field
		var span_start_time = document.createElement('span');
		var input_start_time = document.createElement('input');
		lineDiv.appendChild(span_start_time);
		span_start_time.appendChild(input_start_time);

		input_start_time.className = "timeInputBox";
		input_start_time.id = "showStartTime" + num;
		input_start_time.setAttribute('type',"text");

		// Put the "to" label in
		var stopLabel = document.createElement('span')
		stopLabel.innerHTML="To:"
		stopLabel.className = "labelText"
		lineDiv.appendChild(stopLabel)

		// Stop time input field
		var span_stop_time = document.createElement('span');
		var input_stop_time = document.createElement('input');
		lineDiv.appendChild(span_stop_time);
		span_stop_time.appendChild(input_stop_time);

		input_stop_time.className = "timeInputBox";
		input_stop_time.id = "showStopTime" + num;
		input_stop_time.setAttribute('type',"text");
		
		// Show name field 
		var span_show_name = document.createElement('span');
		var select_show_name = document.createElement('select');
		lineDiv.appendChild(span_show_name);
		span_show_name.appendChild(select_show_name);

		shows = ['a', 'b', 'c']
		for (var i = 0; i < shows.length; i++){
			select_show_name.options.add(new Option(shows[i], shows[i]));
		}
		select_show_name.id = "showNameSelect" + num;
		select_show_name.className = "dropdownOptions";
		select_show_name.style.width=31 + "%"


		// Grow the accordion if it is in display mode. Take the name of the accordion div (which
		// holds the actual options of this type), get the next sibling, and set it to active.
		var acc = document.getElementById("slideshowSchedulingAccordion");
	    var panel = acc.nextElementSibling;

	    if (acc.className == "accordion"){  
	    // Toggle the criteria div on; it's clearly advantageous to see what you're adding.
	    	acc.classList.toggle("active");
	    }
	    if (acc.className == "accordion active"){
		    panel.style.maxHeight = panel.scrollHeight + "px";
		}
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