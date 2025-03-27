
SHELL = /bin/bash
TOOLS="./tools"

.PHONY: help run kill status monitor errors

help:
	@ echo ""
	@ echo "Usage:"
	@ echo "  setup: Setup Project"
	@ echo "  run: Launch the Bot"
	@ echo "  stop: Stop the Bot"
	@ echo "  status: Check if Bot is running"
	@ echo "  monitor: Check users captcha process"
	@ echo "  error: Check for errors in the Bot"
	@ echo ""

setup:
	@ chmod +x $(TOOLS)/setup
	@ $(TOOLS)/setup

run:
	@ chmod +x $(TOOLS)/run
	@ $(TOOLS)/run

stop:
	@ chmod +x $(TOOLS)/stop
	@ $(TOOLS)/stop

status:
	@ chmod +x $(TOOLS)/status
	@ $(TOOLS)/status

monitor:
	@ chmod +x $(TOOLS)/monitor
	@ $(TOOLS)/monitor

errors:
	@ chmod +x $(TOOLS)/check_errors
	@ $(TOOLS)/check_errors

catcfgchat:
	@ chmod +x $(TOOLS)/catcfgchat
	@ $(TOOLS)/catcfgchat

stats:
	@ chmod +x $(TOOLS)/stats
	@ $(TOOLS)/stats
