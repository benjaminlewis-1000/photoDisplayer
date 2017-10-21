var acc = document.getElementsByClassName("accordion");
var slideshowButton = document.getElementsByClassName("newShowClass");
var i;

for (i = 0; i < acc.length; i++) {
    acc[i].onclick = function() {
	    this.classList.toggle("active");

	    var thisId = this.id;
	    // If we have activated the accordion for slideshow scheduling, toggle the "new schedule" button to active or not as well.
	    if (thisId == "slideshowSchedulingAccordion"){
	    	slideshowButton[0].classList.toggle("active");
	    }
	    var panel = this.nextElementSibling;
	    if (panel.style.maxHeight){
	      panel.style.maxHeight = null;
	    } else {
	      panel.style.maxHeight = panel.scrollHeight + "px";
	    } 
    }

}


for (i = 0; i < slideshowButton.length; i++){
	slideshowButton[i].onclick = function(){
		this.classList.toggle("active");
		addScheduleLine('slideshowScheduleFieldsDiv');
	}
}