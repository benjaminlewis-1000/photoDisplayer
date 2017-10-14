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
<script type="text/javascript" src="scripts_controlpanel/lineAdd.js"></script>
<script type="text/javascript" src="scripts_controlpanel/sendToPi.js"></script>

<!-- Calendar JS files -->
<script language="JavaScript" src="scripts_controlpanel/CalendarPopup.js"></script>
<script type="text/javascript" src="scripts_controlpanel/date.js"></script>
<script type="text/javascript" src="scripts_controlpanel/AnchorPosition.js"></script>
<!-- End Calendar JS files -->

<!-- Calendar javascript configuration -->
<script type="text/javascript">
	var cal = new CalendarPopup("testdiv1");
	cal.showNavigationDropdowns();
	cal.setCssPrefix("Test");
	cal.setYearSelectStartOffset(10);
</script>
<!-- End calendar JS config -->


<script src='scripts_controlpanel/lineConstructor.php' type='text/javascript'></script>


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
	<!-- Floating div for calendar -->
	<div id="testdiv1" style="position:absolute;visibility:hidden;background-color:white;layer-background-color:white;"></div>


	<div id=newCriteriaDiv class="head_div">
		<button id="newCriteria" class="taskButton" title="Toggle TV power - turn off TV if on, turn TV on if off" onclick="turnOnTV('Toggle')">
			Toggle TV Power
		</button>
		<button id="newCriteria" class="taskButton" title="Add a new filtering option to the slideshow" onclick="addCriteriaLine('criteriaFieldsDiv')">
			New Criteria
		</button>
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

	<div id="minPhotoDiv"  style="position: absolute; right:60%; width:30%; height:30px; font-size: 15px; z-index:999; margin-top: 10px; vertical-align: middle;">
		<span style="line-height: 30px; margin-right: 5px;">
			Min Pictures Per Person:  
		</span>
		<span>
			<input id="minPhotos" 
				style="position:absolute; font-family: 'Goudy Old Style'; height:30px; " 
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


	<button class="accordion">Slideshow Options
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
						<input id="delayForm" name="delayVal" style="width: 40px; height: 25px" value="2.0"></input>
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



</body>

<script type="text/javascript">
	$('#optionForm').submit(function () {
	 return false;
	});
</script>


</html>