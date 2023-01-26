/* tests using a 120x120x120 bed */

bedx = 120;
bedy = 120;
purgew = 2;
purgel = 90;
border = 1;

if(ty == 1)
  /* cube that is smaller than purge */
  cube([purgel - 5, purgel - 5, 10]);
else if(ty == 2)
  /* cube that is larger than purge */
  cube([purgel + 5, purgel + 5, 10]);
else if(ty == 3)
  /* cube that can barely accommodate purge with a minimal border
     and requires moving it when centered */
  cube([bedx - purgew - border , bedy - purgew - border, 10]);
else
  /* cube that cannot accommodate purge */
  cube([bedx - purgew, bedy - purgew, 10]);


