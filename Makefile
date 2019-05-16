build: bin/maze_creator

bin/maze_creator: src/maze_creator.cpp
	g++ src/may3.cpp -O2 -o bin/maze_creator

clear: 
	-rm bin/maze_creator

run: build
	flask run


