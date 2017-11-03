

function addScheduleLine(divOfFields, daySelected, timeStart, timeStop, showName){

	// Get the appropriate variable and increment it.
	var num = (document.getElementById('scheduleNumID').value - 1)+ 2;
	document.getElementById('scheduleNumID').value = num;

	console.debug('Div number is ' + num)

	var mainDiv = document.getElementById(divOfFields);
	var lineDiv = document.createElement('div');

	mainDiv.appendChild(lineDiv);

	// Day of week drop-down button
	var span_day_of_week = document.createElement('span');
	var select_day_of_week = document.createElement('select');
	lineDiv.appendChild(span_day_of_week);
	span_day_of_week.appendChild(select_day_of_week);

	days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "On Given Day"];
	for (var i = 0; i < days.length; i++){
		select_day_of_week.options.add(new Option(days[i], days[i]));
	}

	if (daySelected != null && days.indexOf(daySelected) >= 0){
		select_day_of_week.value = daySelected
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

	console.debug('Start time is ' + timeStart)
	console.debug(timeStart)
	if (timeStart != null){
		input_start_time.value = timeStart;
	}

	input_start_time.onchange = function(){checkTime(input_start_time.id) };

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

	if (timeStop != null){
		input_stop_time.value = timeStop;
	}

	input_stop_time.onchange = function(){checkTime(input_stop_time.id) };
	
	// Show name field 
	var span_show_name = document.createElement('span');
	var select_show_name = document.createElement('select');
	lineDiv.appendChild(span_show_name);
	span_show_name.appendChild(select_show_name);

	select_show_name.id = "showNameSelect" + num;
	select_show_name.className = "dropdownOptions";
	select_show_name.style.width=31 + "%"


	// The value of 'definedSlideshows' is managed over in modalScript.php and updates dynamically
	// every time we have a new or deleted slideshow. The theory is to have few calls to the database
	// and then rebuild the list when necessary.
	var i;
    for(i = select_show_name.options.length - 1 ; i >= 0 ; i--)
    {
        select_show_name.remove(i);
    }

	for (var i = 0; i < definedSlideshows.length; i++){	
		select_show_name.options.add(new Option(definedSlideshows[i], definedSlideshows[i]));
	}

	select_show_name.onclick = function(){
		// The value of 'definedSlideshows' is managed over in modalScript.php and updates dynamically
		// every time we have a new or deleted slideshow. The theory is to have few calls to the database
		// and then rebuild the list when necessary.

		console.error('TODO: This should only update if the slideshow array has changed...')
		var i;
	    for(i = select_show_name.options.length - 1 ; i >= 0 ; i--)
	    {
	        select_show_name.remove(i);
	    }

		for (var i = 0; i < definedSlideshows.length; i++){	
			select_show_name.options.add(new Option(definedSlideshows[i], definedSlideshows[i]));
		}
	}

	// Remove button

	var removeSpan = document.createElement('span');
	lineDiv.appendChild(removeSpan);
	removeSpan.id = 'removeSubdivSlideshow' + num;

	var removeLineButton = document.createElement('button');
	removeLineButton.id = 'button';
	removeLineButton.innerText = "Remove";

	removeLineButton.className = "fieldChild";
	removeSpan.appendChild(removeLineButton);

	removeLineButton.onclick = function() { 
		removeElement(lineDiv.id);
	};

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

function removeElement(parentName){

	//console.log(parentName)
	var parent = document.getElementById(parentName);
	parent.remove();

}

function checkTime(elementId){


	element = document.getElementById(elementId);
	time = element.value;

	var timePat = /^((\d{1,2})[:]?(\d{2})?)(\s?(AM|am|PM|pm)?)$/;

	//([0-2]?[0-9]):?([0-5][0-9])(\s?(AM|am|PM|pm)?)

	var milTimePat = /^([01]?\d|2[0-3]):?([0-5]\d)$/;
	var twelveHTimPat = /^([0]?[0-9]|1[0-2]):?([0-5][0-9])?\s?(AM|am|PM|pm)?$/;
//([0-9]|0[0-9]|1[0-9]|2[0-3]):([0-5][0-9])?(AM|am|PM|pm)

	var milTimeMatch = time.match(milTimePat);
	var twelveTimeMatch = time.match(twelveHTimPat);

	if (milTimeMatch == null && twelveTimeMatch == null) {
		//alert("Time is not in a valid format.");
		console.log('time not valid')
		element.value = '';
		return false;
	}

	if (milTimeMatch != null){
		hours = parseInt(milTimeMatch[1]);
		minutes = parseInt(milTimeMatch[2]);

		if (hours < 12){
			ampm = 'AM'
		}else{
			ampm = 'PM'
		}
		hours = (hours + 11) % 12 + 1

	}else if (twelveTimeMatch != null){
		hours = parseInt(twelveTimeMatch[1]);
		if (twelveTimeMatch[2] != null){
			minutes = parseInt(twelveTimeMatch[2]);
		}else{
			minutes = 0;
		}
		if (twelveTimeMatch.length > 3){
			ampm = twelveTimeMatch[3].toUpperCase();
		}else{
			ampm = 'AM'
		}
	}

	minutes = minutes.toString();
	while (minutes.length < 2){
		minutes = '0' + minutes
	}

	element.value = hours + ':' + minutes + ' ' + ampm;
}