
#!/usr/local/bin/perl
use Tk;

# Main Window
my $mw = new MainWindow;

#GUI Building Area
my $playlist;

my $frm_name = $mw -> Frame();

my $row = 2;

# my $options = $mw->OptionMenu(
# 	-options=> [[]]
# )

my @entries;

my @list = ('a','b');
my @two = (1, 2);
my @rowVals = (1, 3);

my %hash;
$hash{'a'} = 1;
$hash{'b'} = 2;

my $opt = $mw->Optionmenu(
-command => sub { print "got: ", shift, "\n" },
-variable => \$var,
-textvariable => \$tvar,
-width=> 50
);

push (@entries, $opt);

while ( (my $key, my $value) = each %hash) {
	$entries[0]->addOptions([$key => $value]);
}

$entries[0]->grid(-row=>2,-column=>2);

my $label = $mw -> Label(-text=>"TBD:");
$label->grid(-row=>2, -column=>1);

my $button = $mw->Button(-text=>"Push me!", -command=>\&push_button)->grid(-row=>1, -column=>1);
# my $playlistName = $frm_name -> Entry(-textvariable=>\$playlist)->grid(-row=>3, -column=>1);
#Age

# my $c = $mw->Canvas(-width => 600, -height => 600)->pack();
MainLoop;

## Functions
#This function will be executed when the button is pushed
sub push_button {
	
	push(@rowVals, 1);
my $ent2 = $frm_name -> Entry();
	my $newOpt = $mw->Optionmenu(
	-command => sub { print "got: ", shift, "\n" },
	-variable => \$rowVals,
	-textvariable => \$tvar,
	-width=> 50
	);
	push(@entries, $ent2);
	$entries[end]->grid(-row=>$row, -column=>2);
while ( (my $key, my $value) = each %hash) {
	print "My val is : " . $val  . "\n";
	$entries[$row - 1]->addOptions([$key => $value]);
}
	$row += 1;
}