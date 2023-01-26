module purge_line() {
   cube([90,2,0.2]);
}
dirx = 0;
rotate([0,0,dirx == 1 ? 0 : 90])
purge_line();

