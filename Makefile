
SHELL = /bin/bash
TOOLS="./tools"

.PHONY: help run kill status monitor errors

help:
	@ echo ""
	@ echo "Usage:"
	@ echo "  run: Launch the Bot"
	@ echo "  kill: Stop the Bot"
	@ echo "  status: Check if Bot is running"
	@ echo "  monitor: Check users captcha process"
	@ echo "  error: Check for errors in the Bot"
	@ echo ""

run:
	@ $(TOOLS)/run

kill:
	@ $(TOOLS)/kill

status:
	@ $(TOOLS)/status

monitor:
	@ $(TOOLS)/monitor

errors:
	@ $(TOOLS)/check_errors
