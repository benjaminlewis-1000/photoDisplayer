

	function addCriteriaLine(divOfFields){


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
			select.id = "selectCriteriaMenu" + num

			subdiv1.appendChild(select);

			select.addEventListener("change", function(){
				constructSelectionLine(num, lineDiv)
			})


		var subdiv2 = document.createElement('span')
		subdiv2.id = 'binarySelect' + num
		lineDiv.appendChild(subdiv2)

		var subdiv3 = document.createElement('span')
		subdiv3.id = 'selectionDiv' + num
		lineDiv.appendChild(subdiv3)

		constructSelectionLine(num, lineDiv)


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
