
function sendToPi(){

	criteriaJSON = criteriaToJSON();

	var callback = $.ajax({
		type: 'POST',
		url: 'scripts_controlpanel/launchSlideshow.php',
		data: {'json': criteriaJSON},
		success: function(data){
			console.log(data)
			data = JSON.parse(data)
	        exceptions = data['exceptions']
	        for (i = 0; i < exceptions.length; i++){
	        	console.log("Error in sendToPi: " + exceptions[i]);
	        }
	        debugMsgs = data['debug']
	        for (i = 0; i < debugMsgs.length; i++){
	        	console.log("Debug message in sendToPi: " + debugMsgs[i]);
	        }
		}
	});

}
