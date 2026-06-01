"""Tmux installer — mirrors the legacy ``install_tmux.sh``."""

from __future__ import annotations

from devenv.cli._installer import (
    InstallContext,
    deploy_dotfile,
    ensure_command,
    ensure_dir,
    git_clone_idempotent,
    package_file,
    run,
)

TPM_REPO = "https://github.com/tmux-plugins/tpm"


def install(ctx: InstallContext) -> None:
    """Install TPM, deploy ``tmux.conf``, and fetch declared plugins."""
    ensure_command("tmux")
    ensure_command("git")

    deploy_dotfile(package_file("tmux", "tmux.conf"), ctx.home / ".tmux.conf", ctx)

    tpm_dir = ctx.home / ".tmux" / "plugins" / "tpm"
    ensure_dir(tpm_dir.parent, ctx)
    git_clone_idempotent(TPM_REPO, tpm_dir, ctx)

    # TPM's ``install_plugins`` reads ``$TMUX_PLUGIN_MANAGER_PATH`` to
    # decide where to clone plugins. The variable is normally exported
    # by ``set-environment`` in ``tmux.conf``, but that only fires from
    # inside a tmux session — when we invoke the script standalone we
    # must pass it explicitly or TPM aborts with "FATAL: Tmux Plugin
    # Manager not configured in tmux.conf".
    install_plugins = tpm_dir / "bin" / "install_plugins"
    plugin_path = str(ctx.home / ".tmux" / "plugins") + "/"
    run(
        [str(install_plugins)],
        ctx,
        check=False,
        env={"TMUX_PLUGIN_MANAGER_PATH": plugin_path},
    )
