CLANGXX?=clang-15
PYTHON?=python3
CXXFLAGS?=-g -O3

DESTDIR=templates
OBJS=src/m_axi.o src/trace.o
OUTPUTS=$(DESTDIR)/liblightningsimrt.a $(DESTDIR)/fifo.ll.jinja $(DESTDIR)/fifo_float.ll.jinja $(DESTDIR)/m_axi.ll.jinja
#DESTDIR_TEST=/home/eric/Projects/hbm-sim/extern/lightning_sim

.PHONY: all clean

all: $(OUTPUTS)

clean:
	rm -f $(OBJS) $(OUTPUTS)

#test: $(DESTDIR_TEST)/fifo.ll.jinja $(DESTDIR_TEST)/fifo_float.ll.jinja

$(DESTDIR)/liblightningsimrt.a: $(OBJS)
	$(AR) rcs $@ $^

$(DESTDIR)/fifo.ll.jinja: src/fifo.cpp
	$(PYTHON) scripts/generate_fifo_template.py --cxx=$(CLANGXX) $< $@

$(DESTDIR)/fifo_float.ll.jinja: src/fifo_float.cpp
	$(PYTHON) scripts/generate_fifo_float_template.py --cxx=$(CLANGXX) $< $@

$(DESTDIR)/m_axi.ll.jinja: src/m_axi.ll.jinja
	cp $< $@
