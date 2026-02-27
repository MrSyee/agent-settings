.PHONY: install uninstall install-claude uninstall-claude install-agent-deck uninstall-agent-deck

install: install-claude install-agent-deck

uninstall: uninstall-claude uninstall-agent-deck

install-claude:
	@./claude-user-setting/symlink_install.sh

uninstall-claude:
	@./claude-user-setting/symlink_uninstall.sh

install-agent-deck:
	@./agent-deck/symlink_install.sh

uninstall-agent-deck:
	@./agent-deck/symlink_uninstall.sh
