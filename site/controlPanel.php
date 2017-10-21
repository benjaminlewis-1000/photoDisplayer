<html>

<head>
	<link rel="stylesheet" type="text/css" href="css_controlpanel/controlPanel.css" media="all"/>
	<link rel="stylesheet" type="text/css" href="css_controlpanel/modal.css" media="all"/>
	<link rel="stylesheet" type="text/css" href="css_controlpanel/criteria.css" media="all"/>
	<link rel="stylesheet" type="text/css" href="css_controlpanel/cal_styles.css"/>
</head>

<!-- For using AJAX -->
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>

<!-- Functionality js files -->
<script src="scripts_controlpanel/controlPanelAccordion.js"></script>
<script src="scripts_controlpanel/readState.js"></script>
<script type="text/javascript" src="scripts_controlpanel/constructCriteriaLine.js"></script>
<script type="text/javascript" src="scripts_controlpanel/schedulingLines.js"></script>
<script type="text/javascript" src="scripts_controlpanel/sendToPi.js"></script>

<!-- Calendar JS files -->
<script language="JavaScript" src="scripts_controlpanel/CalendarPopup.js"></script>
<script type="text/javascript" src="scripts_controlpanel/date.js"></script>
<script type="text/javascript" src="scripts_controlpanel/AnchorPosition.js"></script>
<!-- End Calendar JS files -->

<!-- Link for the "Orbitron" font -->
<link rel="stylesheet" type="text/css" href="//fonts.googleapis.com/css?family=Orbitron" />

<!-- Calendar javascript configuration -->
<script type="text/javascript">
	var cal = new CalendarPopup("testdiv1");
	cal.showNavigationDropdowns();
	cal.setCssPrefix("Test");
	cal.setYearSelectStartOffset(10);
</script>
<!-- End calendar JS config -->




<body>

	<style type="text/css">
		
		/*Implement the nice grayscale background*/
		body {
			background-color: #9e9e9e;
			background-image: -webkit-gradient(linear, left top, left bottom, from(#9e9e9e), to(#454545));
			background-image: -webkit-linear-gradient(top, #9e9e9e, #454545);
			background-image:    -moz-linear-gradient(top, #9e9e9e, #454545);
			background-image:      -o-linear-gradient(top, #9e9e9e, #454545);
			background-image:         linear-gradient(to bottom, #9e9e9e, #454545);
			height: 100%;
			margin: 0;
			background-repeat: no-repeat;
			background-attachment: fixed;
		}
		html {
		    height: 100%;
		}
	</style>

	<!-- A global variable for incrementing and decrementing -->
	<input type="hidden" value="0" id="divNumID" />
	<input type="hidden" value="0" id="scheduleNumID" />
	<!-- Floating div for calendar -->
	<div id="testdiv1" style="position:absolute;visibility:hidden;background-color:white;layer-background-color:white;z-index: 3;"></div>


	<div id=newCriteriaDiv class="head_div">
		<button id="loadShow" title="Load a saved slideshow by name; the &#013criteria fields will automatically populate &#013according to the defined show and any &#013existing criteria will be deleted." class="taskButton">
			Load Slideshow
		</button>
		<button id="saveCriteria" title="Save criteria as currently set to a named&#013 slideshow. If a show name is selected that &#013 already exists, it will be overwritten.&#013The name of a loaded slideshow will be pre-populated" class="taskButton">
			Save Slideshow
		</button>
		<button id="launchSlideshow" title="Launch the slideshow with images filtered&#013 by the current criteria. The TV will turn &#013on if it is not already (although the HDMI&#013 input will not automatically change)" class="taskButton", onclick="sendToPi()">
			Launch Slideshow
		</button>
	</div>

	<div id=onOffDiv class="head_div"><!-- 
		<button id="newCriteria" class="taskButton" title="Add a new filtering option to the slideshow" onclick="addCriteriaLine('criteriaFieldsDiv')"> -->
		<button id="newCriteria" class="taskButton" title="Add a new filtering option to the slideshow" onclick="constructOrUpdateCriteriaLine('criteriaFieldsDiv', 'true', null, 'Person', null, null)">
			New Criteria
		</button>
		<button id="tvToggle" class="taskButton" title="Toggle TV power - turn off TV if on, turn TV on if off" onclick="turnOnTV('Toggle')">
			Toggle TV Power
		</button>
		<button id="showOff" class="taskButton" title="Turn off the TV and end the slideshow" onclick="turnOnTV('End Slideshow')">
			End Slideshow
		</button>
	</div>

	<div id="clockDiv">
		<span id="time" class="digitalClock"></span>
	</div>

	<script type="text/javascript">
		function pad(num, size) {
		    var s = num+"";
		    while (s.length < size) s = "0" + s;
		    return s;
		}
		function Timer() {
		   var dt=new Date()
		   document.getElementById('time').innerHTML=(dt.getHours() + 11) % 12 + 1+":"
		   		+pad(dt.getMinutes(), 2)+":"
		   		+pad(dt.getSeconds(),2)+ " " 
		   		+(dt.getHours() > 11? 'PM': 'AM');
		   setTimeout("Timer()",1000);
		}
		Timer();
	</script>

	<!-- Actions for the modal boxes are defined in scripts_controlpanel/modalScript.php -->
	<!-- Defines the modal overlay that appears when the "Save Slideshow" button is pressed. -->
	<div id="saveModal" class="modal">
	  <div class="modal-content">
	    <span class="modalContent">
	    	<button id="cButtonSave" class="closeButton">&times;</button>
	    	<input id="nameForm" name="saveName" class="loadSelectOptions">
	    	</input>
	   	 	<button id="saveNameSubmit" class="modalSubmit">Save Slideshow</button>
	   	 </span>	
	  </div>
	</div>

	<!-- Defines the modal overlay that appears when the "Load Slideshow" button is pressed. -->
	<div id="loadModal" class="modal">
	  <div class="modal-content">
	    <span class="modalContent">
	    	<button id="cButtonLoad" class="closeButton">&times;</button>
	    	<select id="savedSlideshowSelect" class = "loadSelectOptions"></select>

		   	 	<button id="loadShowSubmit" class="modalSubmit">Load Slideshow</button>
		   	 	<button id="deleteShowSubmit" class="modalSubmit" >Delete Selected Slideshow
	   	 	</button>
	   	 </span>	
	  </div>
	</div>
	<script type="text/javascript" src="scripts_controlpanel/modalScript.php"></script>

	<div id="minPhotoDiv"  style="position: absolute; right:60%; width:30%; height:30px; font-size: 15px; z-index:10; margin-top: 10px; vertical-align: middle;">
		<span style="line-height: 30px; margin-right: 5px;">
			Min Pictures Per Person:  
		</span>
		<span>
			<input id="minPhotos" 
				value="1"
				title="Establish a lower limit for number of photos a person&#013must be in to show in a 'Person' dropdown list. This only &#013applies for criteria that are created or refreshed after the &#013value is changed, because you may theoretically want to &#013include someone that's only been in 2 photos, then change &#013this box to make finding someone with a ton of photos easier &#013afterward.">
			</input>
	    </span>
	</div>

	<button class="accordion" id="criteriaAccordion">
		Picture Criteria Selection
		<script type="text/javascript" src="scripts_controlpanel/controlPanelAccordion.js"></script>
	</button>

	<div class="panel" id="criteriaFieldsDiv">
	</div>


	<!-- https://www.w3schools.com/howto/howto_js_accordion.asp -->


	<button class="accordion" id="slideshowOptions">Slideshow Options
		<script type="text/javascript" src="scripts_controlpanel/controlPanelAccordion.js"></script>
	</button>
	<!-- 
	<script>
	window.onload = function() {
	  $("active").unhide();
	};
	</script> -->



	<div class="panel" id="active" onload="toggleOnLoad(); toggleFunction();">
		<form class="form-validation" id="optionForm" action="#">
		    <div class="sub-entry">
		        <ul>
					<li>
					  	<input class="option_chk" type="checkbox" name="options" value="Fullscreen" checked=True title="Show pictures fullscreen"> Fullscreen<br> <!-- -FxZ -->
					</li>
					<li>
					  	<input class="option_chk" type="checkbox" name="options" value="Randomize" checked=True title="Randomize the list of photos that comprise the slideshow"> Randomize<br>  <!-- -z -->
					</li>
					<li>
					  	<input class="option_chk" type="checkbox" name="options" value="Date Order" title="Sort the photos for a chronological slideshow"> Sort by date, beginnng to end<br>  <!-- -z -->
					</li>
				</ul>
		    </div>
		    <div class="sub-entry">
		        <ul>
					<li>
					  	<input class="option_chk" type="checkbox" name="options" value="Hide" checked=True title="Don't show any menus from the display program and hide the pointer."> Hide Menus and Pointer<br> <!-- -Y, -N -->
					</li>
					<li>
						<input class="option_chk" type="checkbox" name="options" value="Delay" checked=True title="Seconds between each image, minimum."> Delay between images: 
						<input id="delayForm" name="delayVal" style="width: 40px; height: 25px" value="5.0"></input>
						seconds
						<br>
					</li>
				</ul>
		    </div>
			<button id="optionRelaunch"  onclick="relaunchWithOptions()">
				Relaunch with these options
			</button>
		</form>
	</div>


	<div id="newScheduleDiv"  style="position: absolute; right:60%; width:30%; height:30px; font-size: 15px; z-index:10; vertical-align: middle;">
		<button id="newShowButton" class="newShowClass" onclick="
			/* Gets the button that this button is on (i.e. 'Slideshow Scheduling') and 
			determines whether it is expanded or not. If it is not expanded, its state 
			will toggle, and that of the button should as well. Otherwise, it's already 
			toggled and we can leave it alone.*/
			counterpart = document.getElementById('slideshowSchedulingAccordion');
	    	panel = counterpart.nextElementSibling;
	    	if (! panel.style.maxHeight){
				this.classList.toggle('active'); 
		    } 
			addScheduleLine('slideshowScheduleFieldsDiv');
		" >New schedule</button>
	</div>
	<button class="accordion" id="slideshowSchedulingAccordion">Slideshow Scheduling
		<script type="text/javascript" src="scripts_controlpanel/controlPanelAccordion.js"></script>
	</button>

	<div class="panel" id="slideshowScheduleFieldsDiv">
	</div>


</body>

<script type="text/javascript">
	$('#optionForm').submit(function () {
	 return false;
	});
</script>


</html>