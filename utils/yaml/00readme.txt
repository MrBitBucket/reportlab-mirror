The idea is a little documentation tool for ourselves.
This should replace/extend Aaron's markup used on the
web site; if needed we can change whitepaper.txt
and devfaq.txt to the new format, but hopefully
few changes will be needed.

We can then use it to write our own User Guide.
The parser should be really easy to extend
with new commands to do almost anything - 
go grab Python code, get drawings defined
elsewhere etc. etc.


Currently:

-yaml.py parses the file into a list of tuples like
this

[('PARAGRAPH', 'Heading1', 'My Document Title),
('IMAGE', filename)]

- yaml2pdf creates a doc template, defines a style
sheet, turns the above list into a story, and
prints it.  

- yaml2html not written.

Note that intra-paragraph XML tags are passed
straight through, which is exactly the intention.
The HTML output filter is not done yet.

I have no strong views on one module versus three.

- Andy

