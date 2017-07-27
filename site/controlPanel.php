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
		<button id="newCriteria" class="taskButton" onclick="addCriteriaLine('criteriaFieldsDiv')">
			New criteria
		</button>
		<button id="loadShow" class="taskButton">
			Load Slideshow
		</button>
		<button id="saveCriteria" class="taskButton">
			Save Slideshow
		</button>
		<button id="launchSlideshow", class="taskButton", onclick="sendToPi()">
			Launch Slideshow
		</button>
	</div>

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


	<button class="accordion" id="criteriaAccordion">Picture Criteria Selection
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
		<form class="form-validation" method="post" action="script.php">
		    <div class="sub-entry">
		        <ul>
					<li>
					  	<input class="option_chk" type="checkbox" name="options" value="Fullscreen" checked=True> Fullscreen<br> <!-- -FxZ -->
					</li>
					<li>
					  	<input class="option_chk" type="checkbox" name="options" value="Randomize" checked=True> Randomize<br>  <!-- -z -->
					</li>
					<li>
					  	<input class="option_chk" type="checkbox" name="options" value="Date Order"> Sort by date, beginnng to end<br>  <!-- -z -->
					</li>
				</ul>
		    </div>
		    <div class="sub-entry">
		        <ul>
					<li>
					  	<input class="option_chk" type="checkbox" name="options" value="Hide" checked=True> Hide Menus and Pointer<br> <!-- -Y, -N -->
					</li>
					<li>
						<input class="option_chk" type="checkbox" name="options" value="Delay" checked=True> Delay between images: 
						<input id="delayForm" name="delayVal" style="width: 40px; height: 25px" value="2.0"></input>
						seconds
						<br>
					</li>
				</ul>
		    </div>
		</form>
	</div>

	<button id='asd' onclick=readShowOptions()> Click me! </button>





</body>


</html>