all: show 

show: docs/epydocs
	open ./docs/epydocs/index.html

test:
	python -m doctest -v chamview.py grammar 

docs/epydocs: 
	epydoc --html . -o ./docs/epydocs

clean:
	rm -r ./docs/epydocs 
