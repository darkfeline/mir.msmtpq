# Generic Makefile for installing a single script.

SCRIPT=pymsmtpq
INSTALL_DIR=~/bin
SCRIPT_PATH=$(realpath $(SCRIPT))

all:
	@echo "Usage:"
	@echo "make install - Install script in ~/bin"
	@echo "make develop - Install symlink to script in ~/bin"

install:
	cp $(SCRIPT) $(INSTALL_DIR)

develop:
	ln -s $(SCRIPT_PATH) $(INSTALL_DIR)/$(SCRIPT)
