<html>
<head>	
	<title>
		Picture Perfect Pi Photo Phrame
	</title>
</head>

<body>


<h1 style="text-align: center;"><span style="color: #33cccc;">Picture Perfect Pi</span></h1>
<p>&nbsp;</p>
<p><a href="page2.php"> <button> Select Filter Options </button> </a></p>
<p>&nbsp;</p>
<p>So, here's the earth. It's "cron"-ically cool. I have a display here, it's so great! Hello, today is <?php echo date('l, F jS, Y'); ?>.</p>

<p>&nbsp;</p>

<?php
    echo "<textarea name='mydata'>\n";
    echo htmlspecialchars($data)."\n";
    echo "</textarea>";
?>


        
</body>		
</html>

