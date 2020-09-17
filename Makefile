pyfigures = $(wildcard figures/*.py)
drawiofigures = $(wildcard figures/*.drawio)

drawiopng = $(patsubst %.drawio,%.png,$(drawiofigures))
drawiopdf = $(patsubst %.drawio,%.pdf,$(drawiofigures))
pypng = $(patsubst %.py,%.png,$(pyfigures))
pypdf = $(patsubst %.py,%.pdf,$(pyfigures))

.PHONY: html pypng allcode alltgz

html: allcode pypng
	(cd site; hugo --minify --cleanDestinationDir)

allslides: allfigures

site/static/images:
	mkdir -p $@

pypng: site/static/images $(pypng)
	rsync --delete -rupm figures/ site/static/images/auto/ --filter '+ */' --filter '+ *.png' --filter '- *'

drawiopng: site/static/images $(drawiopng)
	rsync --delete -rupm figures/ site/static/images/manual/ --filter '+ */' --filter '+ *.png' --filter '- *'

allpdf: $(drawiopdf) $(pypdf)

figures/%.png: figures/%.drawio
	drawio -s 2 -t -f png -x --crop -o $@ $<

figures/%.pdf: figures/%.drawio
	drawio -f pdf -x --crop -o $@ $<

figures/%.png: figures/%.py
	python $< $@

figures/%.pdf: figures/%.py
	python $< $@
