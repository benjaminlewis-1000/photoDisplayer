<html>
	<title>
		Picture Perfect Pi Photo Phrame
	</title>

<head>
	<style>
		/* Dropdown Button */
		.dropbtn {
		    background-color: #4CAF50;
		    color: white;
		    padding: 16px;
		    font-size: 16px;
		    border: none;
		    cursor: pointer;
		}

		/* Dropdown button on hover & focus */
		.dropbtn:hover, .dropbtn:focus {
		    background-color: #3e8e41;
		}

		/* The container <div> - needed to position the dropdown content */
		.dropdown {
		    position: relative;
		    display: inline-block;
		}

		/* Dropdown Content (Hidden by Default) */
		.dropdown-content {
		    display: none;
		    position: absolute;
		    background-color: #f9f9f9;
		    min-width: 160px;
		    box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
		    z-index: 1;
		}

		/* Links inside the dropdown */
		.dropdown-content a {
		    color: black;
		    padding: 12px 16px;
		    text-decoration: none;
		    display: block;
		}

/*
		#test{
			max-width: 1000px;
			margin 20px auto;
			padding: 10px;
			border: solid blue 2px;
			--webkit-box-sizing: border-box;float: 
			-moz-box-sizing: border-box;
			box-sizing: border-box;
		}
*/
		/* Change color of dropdown links on hover */
		.dropdown-content a:hover {background-color: #f1f1f1}

		/* Show the dropdown menu (use JS to add this class to the .dropdown-content container when the user clicks on the dropdown button) */
		.show {display:block;}
	</style>
</head>

<style type="text/css">

	.fieldParent{
		position:relative;
	    height: 70px;
	    max-width: 1000px;
	    /*border: 4px solid black;*/
		margin 20px auto;
		padding: 10px;
		border: solid blue 2px;
		--webkit-box-sizing: border-box;float: 
		-moz-box-sizing: border-box;
		box-sizing: border-box;
	}

	.fieldChild{
	    background-color: #FFFCE0;
	    color: #200954;
	    padding: 16px;
	    font-size: 16px;
	    border: 20px;
	    cursor: pointer;

	    left: 20px;
	    flex: 1;
	    height: 50px;
	    max-width: 200px;
	    float: left;
	    border-radius: 15px;

	    margin-left: 10px;
	    margin-right: 10px;

	    transition: 1.5s ease;
	    padding: 16px;
	    font-size: 16px;
	    border: none;
	    cursor: pointer;
	}

	.fieldChild:hover {
	    background-color: #eeefba;
	}
</style>

<!-- New criteria line script -->
<script type="text/javascript">

	function addCriteriaLine(divOfFields){
		var div = document.createElement('div');
		div.id = 'test';
		div.className = "fieldParent";

		var subdiv1 = document.createElement('div');
			var select = document.createElement("select");

			var list = ["Date", "Person"];

			for (var i = 0; i < list.length; i++){
				select.options.add(new Option(list[i], list[i]));
			}

			select.className = "fieldChild";

			var t = document.createTextNode("Click me!");
			select.appendChild(t);

			subdiv1.appendChild(select);

		var subdiv2 = document.createElement('div');

			var select2 = document.createElement("select");
			select2.options.add(new Option("m23", "adfds", true, true));
			select2.options.add(new Option("m562", "sdAU", true, true));
			select2.options.add(new Option("m356", "A2U", true, true));

			select2.className = "fieldChild";

			var t = document.createTextNode("Click me!");
			select2.appendChild(t);

			subdiv2.appendChild(select2);

		var subdiv3 = document.createElement('div');
		subdiv3.id = 'subdiv3';
			var removeLineButton = document.createElement('BUTTON');
			removeLineButton.id = 'button';
			var t = document.createTextNode('Remove Criteria');
			removeLineButton.appendChild(t);


			removeLineButton.className = "fieldChild";
			subdiv3.appendChild(removeLineButton);



		div.appendChild(subdiv1);
		div.appendChild(subdiv2);
		div.appendChild(subdiv3);

		console.log(subdiv3.parentNode.id);
		console.log(subdiv3.id);
		console.log(removeLineButton.parentNode.parentNode.id);
/*		removeLineButton.onClick=removeElement(removeLineButton.parentNode.parentNode.id, removeLineButton.parentNode.id);
*/
/*
		subdiv3.parentNode.removeChild(subdiv3);*/
		criteriaFieldsDiv.appendChild(div);


	}

	function removeElement(parentDiv, childDiv){
     if (childDiv == parentDiv) {
          alert("The parent div cannot be removed.");
     }
     else if (document.getElementById(childDiv)) {     
          var child = document.getElementById(childDiv);
          var parent = document.getElementById(parentDiv);
          parent.removeChild(child);
     }
     else {
          alert("Child div has already been removed or does not exist.");
          return false;
     }



  
}

</script>
<!-- New criteria button formatting -->
<style type="text/css">
	#newCriteria{
		position:relative;
	    top: 3px;
	    left: 2px;
	    height: 50px;
	    width: 200px;
	    border-radius: 15px;

	    background-color: #4CAF50;
	    transition: 1.5s ease;
	    color: white;
	    padding: 16px;
	    font-size: 16px;
	    border: none;
	    cursor: pointer;

		box-shadow: 0px 8px 16px 0px rgba(0,0,0,0.2);
	}

	/* Dropdown button on hover & focus */
	#newCriteria:hover/*, #newCriteria:focus*/ {
	    background-color: #5e8eff;
	}


</style>

<!-- <script>
	function myFunction() {
    	document.getElementById("myDropdown").classList.toggle("show");
	}


	// Close the dropdown menu if the user clicks outside of it
	window.onclick = function(event) {
	  if (!event.target.matches('.dropbtn')) {

	    var dropdowns = document.getElementsByClassName("dropdown-content");
	    var i;
	    for (i = 0; i < dropdowns.length; i++) {
	      var openDropdown = dropdowns[i];
	      if (openDropdown.classList.contains('show')) {
	        openDropdown.classList.remove('show');
	      }
	    }
	  }
	}
</script> -->

<!-- <script type="text/javascript">
	text="test";

	function postData(input){
		var jqXHR = $.ajax({
			type: "POST",
			url: "C:\\Users\\Benjamin\\Desktop\\site\\dbAccess.py",
			data: {param: input},
			success: callbackFunc
		})
	}

	function callbackFunc(response){
		console.log(response);
	}

	$('#submitbutton').click(function(){
        datatosend = 'this is my matrix';
        result = runPyScript(datatosend);
        console.log('Got back ' + result);
    });
</script> -->


<body>

<div id=header>
<style type="text/css">
	#header{
		max_width:1000px;
	}
</style>
	<h1 style="text-align: center;"><span style="color: #ff9900;">Page 2</span></h1>
</div>
<!-- <div class="dropdown">
  <button onclick="myFunction()" class="dropbtn">Dropdown</button>
  <div id="myDropdown" class="dropdown-content">
    <a href="#">Link 1</a>
    <a href="#">Link 2</a>
    <a href="#">Link 3</a>
  </div>
</div> -->

<div id=newCriteriaDiv>
	<button id="newCriteria" onclick="addCriteriaLine('criteriaFieldsDiv')">New criteria</button>
</div>

<div id=fill>
<style type="text/css">
	#fill{
		height: 40px;
	}
</style>
</div>

<div id=criteriaFieldsDiv>
<style type="text/css">
	#criteriaFieldsDiv{
		background-color: #E3EBF7;
		max-width: 1000;
	}
</style>
</div>

<!-- <button id="newCriteria" onclick="adddiv()">Add Div</button>
<script type="text/javascript">
	
		function adddiv() {
	  
	   var divElement = document.createElement("div");  // private scope
	   divElement.id = "myDiv";  
	   divElement.style='width:100px;height:100px;border:1px solid black;'
	   divElement.className = "myDivClass";  
	   divElement.innerHTML = 'new div';  
	   document.body.appendChild(divElement);
	    var btn=document.getElementById('btn');
	   btn.addEventListener('click',function(){  // if this function is defined outside it won't work because divElement will be out of its scope
	         document.body.removeChild(divElement);
	   });
	   
	}
	window.addEventListener('load',adddiv);
</script> -->

<input type='button' value='remove' id='btn'>


<form id="form1" name="form1" method="post" action="<?php echo $PHP_SELF; ?>">
    <select Emp Name='NEW'>
    <option value="">--- Select ---</option>
    
    <?php 

	try{
		$db = new SQLite3('photos_master.db');

		$results = $db->query('SELECT person_name FROM people');
		while ($row = $results->fetchArray()) {
			if (!empty($row[0])){
		   		echo "<option value=\"" . $row[0] . ">" . $row[0] . "</option>";
			}
		}
	}catch(Exception $e){
		die('connection_unsuccessful: ' . $e->getMessage());
	}

     ?>
     
    </select>
    <input type="submit" name="Submit" value="Select" />
</form>
<!-- 
<div id="parent" style="border: 1px solid red; padding: 10px;">
     I am the parent div.
     <div id="child" style="border: 1px solid green; padding: 10px;">
           I am a child div within the parent div.
     </div>
</div>
<p>&nbsp;</p>
<input type="button" value="Remove Element" onClick="removeElement('parent','child');"> -->

</body>
</html>