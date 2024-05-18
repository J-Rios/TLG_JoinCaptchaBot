
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
	@ chmod +x $(TOOLS)/run
	@ $(TOOLS)/run

kill:
	@ chmod +x $(TOOLS)/kill
	@ $(TOOLS)/kill

status:
	@ chmod +x $(TOOLS)/status
	@ $(TOOLS)/status

monitor:
	@ chmod +x $(TOOLS)/monitor
	@ $(TOOLS)/monitor

errors:
	@ chmod +x $(TOOLS)/check_errors
	@ $(TOOLS)/check_errors
