pyfigures = $(wildcard figures/*.py)
drawiofigures = $(wildcard figures/*.drawio)

drawiosvg = $(patsubst %.drawio,%.svg,$(drawiofigures))
drawiopdf = $(patsubst %.drawio,%.pdf,$(drawiofigures))
pysvg = $(patsubst %.py,%.svg,$(pyfigures))
pypdf = $(patsubst %.py,%.pdf,$(pyfigures))

.PHONY: html allcode pysvg allsvg drawiosvg

html: allcode allsvg
	(cd site; hugo --minify --cleanDestinationDir)

site/static/images/manual:
	mkdir -p $@

site/static/images/auto:
	mkdir -p $@

allsvg: pysvg drawiosvg

pysvg: site/static/images/auto $(pysvg)
	rsync --delete -rupm $(pysvg) site/static/images/auto/

drawiosvg: site/static/images/manual $(drawiosvg)
	rsync --delete -rupm $(drawiosvg) site/static/images/manual/

figures/%.svg: figures/%.drawio
	drawio -s 2 -t -f svg -x --crop -o $@ $<

figures/%.svg: figures/%.py
	python $< $@

allcode:
	rsync --delete -rupm code/ site/static/code/ --filter '+ */'  --filter '+ Makefile' --filter '+ *.ipynb' --filter '+ *.c' --filter '+ *.py' --filter '+ *.slurm' --filter '- *'
