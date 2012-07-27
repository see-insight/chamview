all: show 

show: docs/epydocs
	open ./docs/epydocs/index.html

docs/epydocs: 
	epydoc --html chamview.py -o ./docs/epydocs

clean:
	rm -r ./docs/epydocs 
