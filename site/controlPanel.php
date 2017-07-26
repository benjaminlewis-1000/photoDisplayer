<html>

<head>
	<link rel="stylesheet" type="text/css" href="controlPanel.css" media="all"/>
	<link rel="stylesheet" type="text/css" href="modal.css" media="all"/>
	<link rel="stylesheet" type="text/css" href="criteria.css" media="all"/>
	<link rel="stylesheet" type="text/css" href="css/cal_styles.css"/>
</head>

<script src="controlPanelAccordion.js"></script>
<!-- For using AJAX -->
<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js"></script>


<!-- Calendar JS files -->
<script language="JavaScript" src="js/CalendarPopup.js"></script>
<script type="text/javascript" src="js/date.js"></script>
<script type="text/javascript" src="js/AnchorPosition.js"></script>
<!-- End Calendar JS files -->

<!-- Calendar javascript configuration -->
<script type="text/javascript">
	var cal = new CalendarPopup("testdiv1");
	cal.showNavigationDropdowns();
	cal.setCssPrefix("Test");
	cal.setYearSelectStartOffset(10);
</script>
<!-- End calendar JS config -->


<script src='lineConstructor.php' type='text/javascript'></script>


<body>
	<!-- A variable for incrementing and decrementing -->
	<input type="hidden" value="0" id="divNumID" />
	<!-- Floating div for calendar -->
	<div id="testdiv1" style="position:absolute;visibility:hidden;background-color:white;layer-background-color:white;"></div>

	<script type="text/javascript" src="lineAdd.js"></script>

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
		<button id="launchSlideshow", class="taskButton", onclick="launchSlideshow()">
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
	<script type="text/javascript" src="modalScript.php"></script>


	<button class="accordion">Picture Criteria Selection
		<script type="text/javascript" src="controlPanelAccordion.js"></script>
	</button>

	<div class="panel" id="criteriaFieldsDiv">
	</div>


	<!-- https://www.w3schools.com/howto/howto_js_accordion.asp -->


	<button class="accordion">Slideshow Options
		<script type="text/javascript" src="controlPanelAccordion.js"></script>
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
					  	<input class="option_chk" type="checkbox" name="options" value="Fullscreen"> Fullscreen<br> <!-- -FxZ -->
					</li>
					<li>
					  	<input class="option_chk" type="checkbox" name="options" value="Randomize"> Randomize<br>  <!-- -z -->
					</li>
					<li>
					  	<input class="option_chk" type="checkbox" name="options" value="Date Order"> Sort by date, beginnng to end<br>  <!-- -z -->
					</li>
				</ul>
		    </div>
		    <div class="sub-entry">
		        <ul>
					<li>
					  	<input class="option_chk" type="checkbox" name="options" value="Hide"> Hide Menus and Pointer<br> <!-- -Y, -N -->
					</li>
					<li>
						<input class="option_chk" type="checkbox" name="options" value="Delay"> Delay between images: 
						<input id="delayForm" name="delayVal" style="width: 40px; height: 25px"></input>
						seconds
						<br>
					</li>
				</ul>
		    </div>
		</form>
	</div>





</body>


</html>