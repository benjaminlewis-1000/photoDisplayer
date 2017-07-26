

var critMenuName = 'selectCriteriaMenu';
var emptyCal = '<none>'


	function addCriteriaLine(){


		divOfFields = arguments[0];
		construct = {'selectType': 'Date Range'}
		if (arguments.length > 1){
			criteria = arguments[1];
			construct = {'selectType': criteria['criteriaType'], 'binarySwitch': criteria['booleanVal'], 'selection': criteria['criteriaVal']}
		}

		var mainDiv = document.getElementById(divOfFields);

  		var num = (document.getElementById('divNumID').value -1)+ 2;
  		document.getElementById('divNumID').value = num;

		var lineDiv = document.createElement('div');
		mainDiv.appendChild(lineDiv);

		lineDiv.id = 'criteriaBox' + num;
		lineDiv.className = "fieldParent";

		var subdiv1 = document.createElement('span');
			lineDiv.appendChild(subdiv1);
			subdiv1.id = 'typeBox' + num

			var select = document.createElement("select");


			var list = ["Date Range", "Person", "Year", "Month"]

			for (var i = 0; i < list.length; i++){
				select.options.add(new Option(list[i], list[i]));
			}

			select.className = "criteriaType";
			select.id = critMenuName + num

			subdiv1.appendChild(select);

			select.addEventListener("change", function(){
				// Get the new field, create a construct for it, and construct the selection line again. 
				classType = select.value;
				construct = {'selectType': classType}
				constructSelectionLine(num, lineDiv, construct)
			})


		var subdiv2 = document.createElement('span')
		subdiv2.id = 'binarySelect' + num
		lineDiv.appendChild(subdiv2)

		var subdiv3 = document.createElement('span')
		subdiv3.id = 'selectionDiv' + num
		lineDiv.appendChild(subdiv3)

		constructSelectionLine(num, lineDiv, construct)


		var removeSubdiv = document.createElement('span');
		lineDiv.appendChild(removeSubdiv);
		removeSubdiv.id = 'removeSubdiv' + num;

			var removeLineButton = document.createElement('BUTTON');
			removeLineButton.id = 'button';
			var t = document.createTextNode('Remove ');
			removeLineButton.appendChild(t);

			removeLineButton.className = "fieldChild";
			removeSubdiv.appendChild(removeLineButton);

			var name = 'removeButton' + num
			var re = /.?(\d+)$/

			var num1 = re.exec(name)
			var value = num1[1]
			//console.log(value)

			removeLineButton.onclick = function() { removeElement(removeSubdiv.id);};//removeElement//(subdiv3.id)

	}
/*
	function listenMetaCategory(subdivName){

		var re = /.?(\d+)/ // Match the number at the end of the ID. 
		var num1 = re.exec(subdivName)
		var value = num1[1]

		var newVal = document.getElementById(critMenuName + value).value

	}*/

	function removeElement(boxIDName){

		//console.log(boxIDName)
		var re = /.?(\d+)/ // Match the number at the end of the ID. 
		var num1 = re.exec(boxIDName)
		//console.log(num1)
		var value = num1[1]

		parentName = 'criteriaBox' + value
		//console.log(parentName)
		var parent = document.getElementById(parentName);
		parent.remove();
  
	}