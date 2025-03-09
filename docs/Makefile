# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= -j auto
SPHINXBUILD   ?= sphinx-build
SPHINXAPIDOC  ?= sphinx-apidoc
SPHINXAPIDOCDIR = generated
SOURCEDIR     = .
BUILDDIR      = _build
PACKAGEDIR    ?= ../src

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

linkcheck:
	$(SPHINXBUILD) -b linkcheck $(ALLSPHINXOPTS) "$(SOURCEDIR)" $(BUILDDIR)/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
	      "or in $(BUILDDIR)/linkcheck/output.txt."

# Generate API documentation
apidoc:
	@$(SPHINXAPIDOC) $(APIDOCFLAGS) -d 1 --force --separate --no-toc -o "$(SPHINXAPIDOCDIR)" "$(PACKAGEDIR)"

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
