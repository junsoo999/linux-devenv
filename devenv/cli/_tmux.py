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

    # TPM resolves the plugin directory via ``tmux show-environment -g
    # TMUX_PLUGIN_MANAGER_PATH`` — that is, from the tmux *server's*
    # global environment, not the calling shell. The variable is only
    # auto-populated from inside a running tmux session (by ``run
    # '~/.tmux/plugins/tpm/tpm'`` in tmux.conf), so when we invoke
    # ``install_plugins`` standalone we must seed it ourselves. Without
    # this TPM aborts with "FATAL: Tmux Plugin Manager not configured
    # in tmux.conf".
    plugin_path = str(ctx.home / ".tmux" / "plugins") + "/"
    run(
        ["tmux", "set-environment", "-g", "TMUX_PLUGIN_MANAGER_PATH", plugin_path],
        ctx,
    )

    install_plugins = tpm_dir / "bin" / "install_plugins"
    run([str(install_plugins)], ctx, check=False)
