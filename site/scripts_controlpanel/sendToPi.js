
function sendToPi(){

	criteriaJSON = criteriaToJSON();

	var callback = $.ajax({
	  type: 'POST',
	  url: 'scripts_controlpanel/launchSlideshow.php',
	  data: {'json': criteriaJSON},
	  complete: function(r){
         console.log(r.responseText);
      }
	});

	console.log(callback);
}
