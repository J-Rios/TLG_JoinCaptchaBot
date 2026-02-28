
SHELL = /bin/bash
TOOLS="./tools"

.PHONY: help start kill status monitor errors

help:
	@ echo ""
	@ echo "Usage:"
	@ echo "  setup: Setup Project"
	@ echo "  start: Launch the Bot"
	@ echo "  stop: Stop the Bot"
	@ echo "  status: Check if Bot is running"
	@ echo "  monitor: Check users captcha process"
	@ echo "  error: Check for errors in the Bot"
	@ echo "  stats: Show statistics"
	@ echo ""

setup:
	@ chmod +x $(TOOLS)/setup
	@ $(TOOLS)/setup

start:
	@ chmod +x $(TOOLS)/start
	@ chmod +x $(TOOLS)/status
	@ $(TOOLS)/start

stop:
	@ chmod +x $(TOOLS)/stop
	@ $(TOOLS)/stop

status:
	@ chmod +x $(TOOLS)/status
	@ $(TOOLS)/status

monitor:
	@ chmod +x $(TOOLS)/monitor
	@ $(TOOLS)/monitor

error:
	@ chmod +x $(TOOLS)/check_errors
	@ $(TOOLS)/check_errors

stats:
	@ chmod +x $(TOOLS)/stats
	@ $(TOOLS)/stats
