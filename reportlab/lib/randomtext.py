#!/bin/env python
#copyright ReportLab Inc. 2000
#see license.txt for license details
#history http://cvs.sourceforge.net/cgi-bin/cvsweb.cgi/reportlab/lib/randomtext.py?cvsroot=reportlab
#$Header: /tmp/reportlab/reportlab/lib/randomtext.py,v 1.6 2001/02/07 15:16:11 johnprecedo Exp $

__version__=''' $Id: randomtext.py,v 1.6 2001/02/07 15:16:11 johnprecedo Exp $ '''

import string

###############################################################################
#	generates so-called 'Greek Text' for use in filling documents.
###############################################################################
"""
This module exposes a function randomText() which generates paragraphs.
These can be used when testing out document templates and stylesheets.
A number of 'themes' are provided - please contribute more!
We need some real Greek text too.

There are currently six themes provided:
	STARTUP (words suitable for a business plan - or not as the case may be),
	COMPUTERS (names of programming languages and operating systems etc),
	BLAH (variations on the word 'blah'),
	BUZZWORD (buzzword bingo),
	STARTREK (Star Trek),
	PRINTING (print-related terms)
	PYTHON (snippets and quotes from Monty Python)
"""

#theme one :-)
STARTUP = ['strategic', 'direction', 'proactive', 'venture capital',
    'reengineering', 'forecast', 'resources', 'SWOT analysis',
    'forward-thinking', 'profit', 'growth', 'doubletalk', 'B2B', 'B2C',
    'venture capital', 'IPO', "NASDAQ meltdown - we're all doomed!"]

#theme two - computery things.
COMPUTERS = ['Python', 'Perl', 'Pascal', 'Java', 'Javascript',
    'VB', 'Basic', 'LISP', 'Fortran', 'ADA', 'APL', 'C', 'C++',
    'assembler', 'Larry Wall', 'Guido van Rossum', 'XML', 'HTML',
    'cgi', 'cgi-bin', 'Amiga', 'Macintosh', 'Dell', 'Microsoft',
    'firewall', 'server', 'Linux', 'Unix', 'MacOS', 'BeOS', 'AS/400',
    'sendmail', 'TCP/IP', 'SMTP', 'RFC822-compliant', 'dynamic',
    'Internet', 'A/UX', 'Amiga OS', 'BIOS', 'boot managers', 'CP/M',
    'DOS', 'file system', 'FreeBSD', 'Freeware', 'GEOS', 'GNU',
    'Hurd', 'Linux', 'Mach', 'Macintosh OS', 'mailing lists', 'Minix',
    'Multics', 'NetWare', 'NextStep', 'OS/2', 'Plan 9', 'Realtime',
    'UNIX', 'VMS', 'Windows', 'X Windows', 'Xinu', 'security', 'Intel', 
    'encryption', 'PGP' , 'software', 'ActiveX', 'AppleScript', 'awk',
    'BETA', 'COBOL', 'Delphi', 'Dylan', 'Eiffel', 'extreme programming',
    'Forth', 'Fortran', 'functional languages', 'Guile', 'format your hard drive',
    'Icon', 'IDL', 'Infer', 'Intercal', 'J', 'Java', 'JavaScript', 'CD-ROM',
    'JCL', 'Lisp', '"literate programming"', 'Logo', 'MUMPS', 'C: drive',
    'Modula-2', 'Modula-3', 'Oberon', 'Occam', 'OpenGL', 'parallel languages',
    'Pascal', 'Perl', 'PL/I', 'PostScript', 'Prolog', 'hardware', 'Blue Screen of Death',
    'Rexx', 'RPG', 'Scheme', 'scripting languages', 'Smalltalk', 'crash!', 'disc crash',
    'Spanner', 'SQL', 'Tcl/Tk', 'TeX', 'TOM', 'Visual', 'Visual Basic', '4GL',
    'VRML', 'Virtual Reality Modeling Language', 'difference engine', '...went into "yo-yo mode"', 
    'Sun', 'Sun Microsystems', 'Hewlett Packard', 'output device',
    'CPU', 'memory', 'registers', 'monitor', 'TFT display', 'plasma screen', 
    'bug report', '"mis-feature"', '...millions of bugs!', 'pizza',
    '"illiterate programming"','...lots of pizza!', 'pepperoni pizza',
    'coffee', 'Jolt Cola[TM]', 'beer', 'BEER!']

#theme three - 'blah' - for when you want to be subtle. :-)
BLAH = ['Blah', 'BLAH', 'blahblah', 'blahblahblah', 'blah-blah',
    'blah!', '"Blah Blah Blah"', 'blah-de-blah', 'blah?', 'blah!!!',
    'blah...', 'Blah.', 'blah;', 'blah, Blah, BLAH!', 'Blah!!!']

#theme four - 'buzzword bingo' time!
BUZZWORD = ['intellectual capital', 'market segment', 'flattening',
		'regroup', 'platform', 'client-based', 'long-term', 'proactive',
		'quality vector', 'out of the loop', 'implement',
		'streamline', 'cost-centered', 'phase', 'synergy',
		'synergize', 'interactive', 'facilitate',
		'appropriate', 'goal-setting', 'empowering', 'low-risk high-yield',
		'peel the onion', 'goal', 'downsize', 'result-driven',
		'conceptualize', 'multidisciplinary', 'gap analysis', 'dysfunctional',
		'networking', 'knowledge management', 'goal-setting',
		'mastery learning', 'communication', 'real-estate', 'quarterly',
		'scalable', 'Total Quality Management', 'best of breed',
		'nimble', 'monetize', 'benchmark', 'hardball',
		'client-centered', 'vision statement', 'empowerment',
		'lean & mean', 'credibility', 'synergistic',
		'backward-compatible', 'hardball', 'stretch the envelope',
		'bleeding edge', 'networking', 'motivation', 'best practice',
		'best of breed', 'implementation', 'Total Quality Management',
		'undefined', 'disintermediate', 'mindset', 'architect',
		'gap analysis', 'morale', 'objective', 'projection',
		'contribution', 'proactive', 'go the extra mile', 'dynamic',
		'world class', 'real estate', 'quality vector', 'credibility',
		'appropriate', 'platform', 'projection', 'mastery learning',
		'recognition', 'quality', 'scenario', 'performance based',
		'solutioning', 'go the extra mile', 'downsize', 'phase',
		'networking', 'experiencing slippage', 'knowledge management',
		'high priority', 'process', 'ethical', 'value-added', 'implement',
		're-factoring', 're-branding', 'embracing change']

#theme five - Star Trek
STARTREK = ['Starfleet', 'Klingon', 'Romulan', 'Cardassian', 'Vulcan',
    'Benzite', 'IKV Pagh', 'emergency transponder', 'United Federation of Planets',
    'Bolian', "K'Vort Class Bird-of-Prey", 'USS Enterprise', 'USS Intrepid',
    'USS Reliant', 'USS Voyager', 'Starfleet Academy', 'Captain Picard',
    'Captain Janeway', 'Tom Paris', 'Harry Kim', 'Counsellor Troi',
    'Lieutenant Worf', 'Lieutenant Commander Data', 'Dr. Beverly Crusher',
    'Admiral Nakamura', 'Irumodic Syndrome', 'Devron system', 'Admiral Pressman',
    'asteroid field', 'sensor readings', 'Binars', 'distress signal', 'shuttlecraft',
    'cloaking device', 'shuttle bay 2', 'Dr. Pulaski', 'Lwaxana Troi', 'Pacifica',
    'William Riker', "Chief O'Brian", 'Soyuz class science vessel', 'Wolf-359',
    'Galaxy class vessel', 'Utopia Planitia yards', 'photon torpedo', 'Archer IV',
    'quantum flux', 'spacedock', 'Risa', 'Deep Space Nine', 'blood wine',
    'quantum torpedoes', 'holodeck', 'Romulan Warbird', 'Betazoid', 'turbolift', 'battle bridge',
    'Memory Alpha', '...with a phaser!', 'Romulan ale', 'Ferrengi', 'Klingon opera',
    'Quark', 'wormhole', 'Bajoran', 'cruiser', 'warship', 'battlecruiser', '"Intruder alert!"',
    'scout ship', 'science vessel', '"Borg Invasion imminent!" ', '"Abandon ship!"',
    'Red Alert!', 'warp-core breech', '"All hands abandon ship! This is not a drill!"']

#theme six - print-related terms
PRINTING = ['points', 'picas', 'leading', 'kerning', 'CMYK', 'offset litho', 
    'type', 'font family', 'typography', 'type designer',
    'baseline', 'white-out type', 'WOB', 'bicameral', 'bitmap',
    'blockletter', 'bleed', 'margin', 'body', 'widow', 'orphan',
    'cicero', 'cursive', 'letterform', 'sidehead', 'dingbat', 'leader',
    'DPI', 'drop-cap', 'paragraph', 'En', 'Em', 'flush left', 'left justified',
    'right justified', 'centered', 'italic', 'Latin letterform', 'ligature',
    'uppercase', 'lowercase', 'serif', 'sans-serif', 'weight', 'type foundry',
    'fleuron', 'folio', 'gutter', 'whitespace', 'humanist letterform', 'caption',
    'page', 'frame', 'ragged setting', 'flush-right', 'rule', 'drop shadows',
    'prepress', 'spot-colour', 'duotones', 'colour separations', 'four-colour printing',
    'Pantone[TM]', 'service bureau', 'imagesetter']

#it had to be done!...
#theme seven - the "full Monty"!
PYTHON = ['Good evening ladies and Bruces','I want to buy some cheese', 'You do have some cheese, do you?',
		  "Of course sir, it's a cheese shop sir, we've got...",'discipline?... naked? ... With a melon!?',
		  'The Church Police!!' , "There's a dead bishop on the landing", 'Would you like a twist of lemming sir?',
		  '"Conquistador Coffee brings a new meaning to the word vomit"','Your lupins please',
		  'Crelm Toothpaste, with the miracle ingredient Fraudulin',
		  "Well there's the first result and the Silly Party has held Leicester.",
		  'Hello, I would like to buy a fish license please', "Look, it's people like you what cause unrest!",
		  "When we got home, our Dad would thrash us to sleep with his belt!", 'Luxury', "Gumby Brain Specialist",
		  "My brain hurts!!!", "My brain hurts too.", "How not to be seen",
		  "In this picture there are 47 people. None of them can be seen",
		  "Mrs Smegma, will you stand up please?",
		  "Mr. Nesbitt has learned the first lesson of 'Not Being Seen', not to stand up.",
		  "My hovercraft is full of eels", "Ah. You have beautiful thighs.", "My nipples explode with delight",
		  "Drop your panties Sir William, I cannot wait 'til lunchtime",
		  "I'm a completely self-taught idiot.", "I always wanted to be a lumberjack!!!",
		  "Told you so!! Oh, coitus!!", "",
		  "Nudge nudge?", "Know what I mean!", "Nudge nudge, nudge nudge?", "Say no more!!",
		  "Hello, well it's just after 8 o'clock, and time for the penguin on top of your television set to explode",
		  "Oh, intercourse the penguin!!", "Funny that penguin being there, isn't it?",
		  "I wish to register a complaint.", "Now that's what I call a dead parrot", "Pining for the fjords???",
		  "No, that's not dead, it's ,uhhhh, resting", "This is an ex-parrot!!",
		  "That parrot is definitely deceased.", "No, no, no - it's spelt Raymond Luxury Yach-t, but it's pronounced 'Throatwobbler Mangrove'.",
		  "You're a very silly man and I'm not going to interview you.", "No Mungo... never kill a customer."
		  "And I'd like to conclude by putting my finger up my nose",
		  "egg and Spam", "egg bacon and Spam", "egg bacon sausage and Spam", "Spam bacon sausage and Spam",
		  "Spam egg Spam Spam bacon and Spam", "Spam sausage Spam Spam Spam bacon Spam tomato and Spam", 
		  "Spam Spam Spam egg and Spam", "Spam Spam Spam Spam Spam Spam baked beans Spam Spam Spam",
		  "Spam!!", "I don't like Spam!!!", "You can't have egg, bacon, Spam and sausage without the Spam!",
		  "I'll have your Spam. I Love it!",
		  "I'm having Spam Spam Spam Spam Spam Spam Spam baked beans Spam Spam Spam and Spam",
		  "Have you got anything without Spam?", "There's Spam egg sausage and Spam, that's not got much Spam in it.",
		  "No one expects the Spanish Inquisition!!", "Our weapon is surprise, surprise and fear!",
		  "Get the comfy chair!", "Amongst our weaponry are such diverse elements as: fear, surprise, ruthless efficiency, an almost fanatical devotion to the Pope, and nice red uniforms - Oh damn!",
		  "Nobody expects the... Oh bugger!", "What swims in the sea and gets caught in nets? Henri Bergson?",
		  "Goats. Underwater goats with snorkels and flippers?", "A buffalo with an aqualung?",
		  "Dinsdale was a looney, but he was a happy looney.", "Dinsdale!!",
		  "The 127th Upper-Class Twit of the Year Show", "What a great Twit!",
		  "thought by many to be this year's outstanding twit",
		  "...and there's a big crowd here today to see these prize idiots in action.",
		  "And now for something completely different.", "Stop that, it's silly",
		  "We interrupt this program to annoy you and make things generally irritating",
		  "This depraved and degrading spectacle is going to stop right now, do you hear me?",
		  "Stop right there!", "This is absolutely disgusting and I'm not going to stand for it",
		  "I object to all this sex on the television. I mean, I keep falling off",
		  "Right! Stop that, it's silly. Very silly indeed", "Very silly indeed", "Lemon curry?",
		  "And now for something completely different, a man with 3 buttocks",
		  "I've heard of unisex, but I've never had it", "That's the end, stop the program! Stop it!"]



def randomText(theme=STARTUP):
	#this may or may not be appropriate in your company
	from random import randint, choice

	RANDOMWORDS = theme

	sentences = 5
	output = ""
	for sentenceno in range(randint(1,5)):
		output = output + 'Blah'
		for wordno in range(randint(10,25)):
			if randint(0,4)==0:
				word = choice(RANDOMWORDS)
			else:
				word = 'blah'
			output = output + ' ' +word
		output = output+'. '
	return output

