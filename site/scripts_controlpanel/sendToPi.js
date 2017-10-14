
function sendToPi(){

	criteriaJSON = criteriaToJSON();
	optionsJSON = readShowOptions(relaunchShow=false);

	var callback = $.ajax({
		type: 'POST',
		url: 'scripts_controlpanel/launchSlideshow.php',
		data: {'json': criteriaJSON, 'options': optionsJSON},
		success: function(data){
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

function turnOnTV(onState){
	console.log('hi')
	var callback = $.ajax({
		type: 'POST',
		url: 'scripts_controlpanel/turnOnTV.php',
		data: {'onState': onState},
		success: function(data){
			data = JSON.parse(data)
			console.log(data)
	        exceptions = data['exceptions']
	        for (i = 0; i < exceptions.length; i++){
	        	console.log("Error in relaunchWithOptions: " + exceptions[i]);
	        }
	        debugMsgs = data['debug']
	        for (i = 0; i < debugMsgs.length; i++){
	        	console.log("Debug message in relaunchWithOptions: " + debugMsgs[i]);
	        }
		}
	});
}

function relaunchWithOptions(){
	options = readShowOptions(relaunchShow=true);

	var callback = $.ajax({
		type: 'POST',
		url: 'scripts_controlpanel/sendOptions.php',
		data: {'options': options},
		success: function(data){
			data = JSON.parse(data)
	        exceptions = data['exceptions']
	        for (i = 0; i < exceptions.length; i++){
	        	console.log("Error in relaunchWithOptions: " + exceptions[i]);
	        }
	        debugMsgs = data['debug']
	        for (i = 0; i < debugMsgs.length; i++){
	        	console.log("Debug message in relaunchWithOptions: " + debugMsgs[i]);
	        }
		}
	});
}