<?php
header("Content-type: application/javascript");
?>  <!-- Do this because of https://stackoverflow.com/questions/23574306/executing-php-code-inside-a-js-file -->

	// Get the modal
	var modal = document.getElementById('saveModal');

	// Get the button that opens the modal
	var btn = document.getElementById("saveCriteria");

	// Get the <button> element that closes the modal
	var closeButton = document.getElementById("cButton");

	var formField = document.getElementById("nameForm");
	// Get the button that saves the field 
	var saveField = document.getElementById("saveNameSubmit");

	console.log(formField)
	console.log(saveField)
	// When the user clicks the button, open the modal 
	btn.onclick = function() {
	    modal.style.display = "block";
	}

	// When the user clicks on <span> (x), close the modal
	closeButton.onclick = function() {
	    modal.style.display = "none";
	}

	// When the user clicks anywhere outside of the modal, close it
	window.onclick = function(event) {
	    if ( event.target == modal ) {
	        modal.style.display = "none";
	    }
	}

	saveField.onclick = function(){
		console.log('This button should run a script to save the current state of the model.');
		saveName = formField.value;
		console.log('Should save ' + saveName)
		formField.value = '';
		modal.style.display = "none";
	}