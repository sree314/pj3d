all: purgex.stl purgey.stl test1.stl test2.stl test3.stl test4.stl purge_stlinfo.json

purgex.stl: purge.scad
	openscad $< -D dirx=1 -o $@

purgey.stl: purge.scad
	openscad $< -D dirx=0 -o $@

test%.stl: purgetest.scad
	openscad $< -D ty=$* -o $@

purge_stlinfo.json: purgex.stl purgey.stl
	stlinfo $^ -o $@
