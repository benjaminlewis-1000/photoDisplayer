#!/usr/bin/perl
use warnings;
use strict;
use Tk;
use Tk::Pane;

my $mw = MainWindow->new;
$mw->geometry('800x600+100+100');

$mw->fontCreate('big',
     -weight=>'bold',
     -size=> 18
    );


my $count = 0;

# hash to hold the text widgets
my %optionLabels;
my %selectionFields;
my %selectionVals;

my $abutton = $mw->Button( -text => 'Add New Text Widget',
              -bg => 'lightyellow',
              -command => \&add,
              -font => 'big'
)->pack(-fill=>'x');


# Scrolled Pane to be the overall container
my $sp = $mw->Scrolled('Pane',
    -scrollbars => 'osoe',
)->pack(-fill=>'both', -expand=>1 );

# a simple text inserter to all text widgets
# my $repeater = $mw->repeat(2000,\&insert );

MainLoop;

sub add{
  my $num = $count++;

  # make a frame to lock in the scrolled text to the scrolled pane
  my $frame = $sp->Frame()->pack(-fill=>'x', -expand=> 1);

  # $text{$num} = $frame->Scrolled('Text',
  #                -background=>'lightsteelblue',
  #        -foreground=>'black',
  #                -font => 'big',
  #                -height => 15, # how many lines are shown
  #                -width => 100, # how many characters per line
  #                )->pack(-fill=>'both', -expand=>1);

    # $buttons{$num} = $frame->Button(-text => "It's a new button")->pack();
    $optionLabels{$num} = $frame->Label(-text=>"Option #$num:");
    $optionLabels{$num}->grid(-row=>$num, -column=>1);

    $selectionFields{$num} = $frame->Optionmenu(
		-command => \&enableField,
		-options => [[Name=>1], [Date=>2], [Month=>3]],
		# -variable => \$var,
		# -textvariable => \$tvar,
		-width=> 50
	);
	$selectionFields{$num}->grid(-row=>$num, -column=>2);

	# TODO: Get the variable, enable or gray out the next one accordingly

    $selectionVals{$num} = $frame->Optionmenu(
		# -command => \&enableField,
		-options => [[a=>1], [b=>2], [c=>3]],
		# -variable => \$var,
		# -textvariable => \$tvar,
		-width=> 60,
		-state=>"disabled"
	);
	$selectionVals{$num}->grid(-row=>$num, -column=>3);

	$selectionVals{$num}->configure(-state=>"active");

 

 }


sub enableField{
	print "got: ", shift, "\n";
	# TODO: Get the row number... 
}

# sub insert {
#    my $data = rand 100000;

#    foreach my $num (keys %text){
#      $text{$num}->insert('end',"text number $num-> ". $data);
#      $text{$num}->insert('end',"\n");
#      $text{$num}->see('end');
#   }

# }
