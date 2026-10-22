# Shopify Page Studio for DeepSeek Harness

Target: Windows + DSH 0.2.0-rc.2. This is a native bundle, not the old offline HTML distribution.

Install the built `.tgz` through DSH's plugin manager, or `dsh plugin --profile <your-profile> add <absolute-tgz-path>`. Reload/restart as requested by the host. A Page Studio launcher appears in the native overlay. Model requests use the host's selected DeepSeek route and credentials.

Fill requirements, preview the send payload, then generate or generate-and-export. The generated seven pages are validated and combined with the supplied Contact Us template. Pages and Menus export together as Matrixify XLSX; JSON and homepage/SEO text are also retained. Save edits before switching versions. Prompt templates support `{{variable}}`, defaults, tags, saving, preview and direct execution in DSH.

User state is under `~/.dsh/page-studio/<profile>/state.json`; never under the installed package. Schema 1 migration is idempotent and backward-compatible; unknown schemas stop without overwriting. Uninstalling the bundle retains state. To recover manually, install the rollback tarball saved under `updates/` and restore the corresponding `state-backup.json` only if needed.

Updates default to startup + six-hour checks and automatic installation when metadata declares a compatible, tested-recoverable version. Until a fixed GitHub `owner/repo` is configured, the UI says the source is missing; it does not claim up to date. Sources are not guessed. Downloads use stable Release assets, length/SHA-256 checks, package identity checks, safe archive inspection, an installation lock and idle gating. Unsaved edits/generation/export defer installation. New permissions or irreversible migrations require review.

Existing bundle updates on this DSH report restart-required. A scoped helper copied to the user update directory watches the old host exit and new-version health; it never terminates DSH. On missing health after restart it reinstalls this plugin's exact saved previous package through the DSH CLI, restores schema-1 state and blocks the failed version. SHA-256 detects corruption, not compromise of the publishing account. Do not enable unattended release eligibility before real install/recovery testing.

Supported content rules retain the original 1–3-day dispatch, estimated 6–12-day delivery, USD, 60-day returns and 5–10-day refund requirements. No fixed local-body generation fallback is shipped. Prompt optimization and separate AI trial are not part of this first build; core prompt execution is included. The existing Contact Us form redirects home and does not submit a message.

Actual validation status and blockers are recorded in `docs/dsh-migration.md` in the project repository. No GitHub release is claimed until a target and successful upload exist.
