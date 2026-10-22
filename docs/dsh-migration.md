> 历史记录更正：0.1.4 正向升级的短时激活不能证明恢复助手已退出。0.1.7 UI 验收发现健康路径不一致，已修正并补充长期恢复与实际助手退出检查；以 docs/release-0.1.7.md 的最终结果为准。

# DSH migration — evidence and acceptance

## Stage 0 / 2026-10-22

The supplied `DSH_插件迁移与自动更新_完整提示词.txt` was read in full (A–E).
Project: Shopify Page Studio, plain browser JS/HTML; no existing package.json or version. Existing git main HEAD 16b2e2b7460e31b92b2df85321f4b8543cf02bfc, no configured remote. Pre-existing modified/untracked files are retained.

Original chain: form → generator.js fixed prose → app.js data/pages → sanitized preview / saved HTML edits → xlsx.js Pages + Menus → ZIP/OOXML download. Separate prompt.js builds 12 selectable prompt requests and copies them. User JSON restore exists; no persistent history.

Preserve: eight page handles, Matrixify Pages 11 columns / Menus 18 columns, About/Information ordering, default Published true, HTML editor, downloads of XLSX/JSON and homepage/SEO text, prompt selection/variables, size-table pure HTML constraints. Replace plugin generation only; legacy offline edition remains intact for existing users. Do not ship fixed prose generator as plugin fallback.

Actual host: Windows Desktop **0.2.0-rc.2**. Confirmed using installed `resources/runtime/cli/bin/dsh.cmd --version`, not web master. Desktop exe is running; profile `~/.dsh/profiles/desktop` has base/web bundles and dsh-pet 0.3.7. Configured selection (no credentials read): deepseek-official / deepseek-flash / high. No API keys printed/copied.

Evidence paths below are relative to installed app.asar `dsh/node_modules/@deepseek-ai/`. The audit script extracts public runtime code into ignored `.dsh-audit` for local comparison. Installed source is authoritative; online docs are reference only.

| Capability | Verified symbol / evidence | Boundary |
|---|---|---|
| Package/install | package `dsh.bundle.patch`, `dsh plugin --profile … add …`; CLI help + official publish tutorial | use native profile manager, no package-store writes |
| Native UI | `window.__ModuleLoader__.load`, `ctx.slots.inject/register('shell.overlay', …)`; installed client-ui-slots and existing dsh-pet/src/client/app.ts | plugin-native launcher and embedded controlled editor |
| Host routes | `ctx.webServer.register({kind:'prefix',path,handler})`; dsh-host-webserver/lib/index.js | inherits host route authorization; origin/CSRF checked for writes |
| Models | `ctx.agentDefaultModel.currentSelection()`, `ctx.llm.listProviders/listModels`; installed modules | frontend never receives credentials |
| Session | `ctx.agents.create({sessionId,meta,agentOptions,setup})` returns `{agent,dispose}`; dsh-agent and agent-loop | unique request/session per initial generation; explicit existing-session continuation |
| Send | `agent.followup(createUserMessage({content,source}))`; agent-loop lines 800–814 | send returns no generation handle; plugin assigns requestId/message.id and observes exact session |
| Streaming | `ctx.on('agent/assistant-stream', ({agent,frame})=>…)`; frame start/chunk/end revision/index | keep reasoning/tools distinct, de-duplicate by attempt + index |
| Completion | `ctx.on('session/event',(session,event)=>…)`; `user/message`, `assistant/message` and `turn/end` | require matching user id, turn, final assistant body, completed reason; idle alone never succeeds |
| Cancellation | `agent.cancel({kind:'user'})`, `whenIdle()` drains | genuine loop signal cancellation; cancelled tasks cannot export |
| Storage | `resolveDshHome()` from dsh-home-paths; namespace + profile under user home | versioned atomic JSON, no runtime data in package |
| Update | plugin-manager `install` reports `restart-required` for existing bundle (lib/index.js ~1801) | no claim of hot update; health + recovery must survive plugin replacement |

Official references: https://deepseek-harness.github.io/deepseek-harness/en/develop/basic/publish ; https://github.com/deepseek-ai/deepseek-harness ; https://deepseek-harness.github.io/deepseek-harness/en/reference/subsystems/core

## Scope and phase checklist

0. Evidence audit above complete; source-specific signatures checked before implementation.
1. Native bundle / controlled editor / user-data storage.
2. Agent-backed tasks, turn association, stream and real cancel.
3. Saved editable prompts, variable expansion/preview/direct run; optimization/trial separately identified.
4. Immutable result revisions and deterministic XLSX + menu export; generate-and-export once per exact task.
5. Release filtering, checksum/staging, idle gating and restart/recovery. No unattended eligibility without a usable recovery archive.
6. Local tarball, checksums, release workflow. GitHub target absent: no guessed repository or fabricated release.
7. Actual host/model/export/install checks recorded separately from simulated/unit checks below.

Only Windows + exact DSH 0.2.0-rc.2 is the initial target. No other platform/version is claimed tested.

## Final local acceptance, 2026-10-22

Phases 1–4: installed native bundle into isolated `page-studio-test` profile. Actual DeepSeek provider `deepseek-official`, model `deepseek-flash`, reasoning `high` generated all seven content pages. Same-session revision changed the requested marketing CTA while retaining the seven page bodies. Actual assistant body and reasoning streams were observed independently. Real cancellation reached host idle with no export; an invalid provider failed truthfully. Duplicate active submission was rejected. Saved variable prompts ran through the actual model; explicit retry used a new request ID. Prompt optimization and isolated comparison trials are deferred enhancements, not claimed implemented.

Actual generated and edited XLSX files were reopened with openpyxl: Pages and Menus each contain the header plus eight records; all eight page handles are linked, Published defaults to TRUE, and saved Chinese edits survive export. The eighth Contact Us page uses the supplied fixed template. Repeated export of the same snapshot returns the same file. Model content is never executed as code.

Phase 5: actual native plugin manager upgraded 0.1.1 to 0.1.2 and reported restart-required; restart loaded 0.1.2 with saved prompts/history intact. Multi-window dirty state and an active real generation delayed installation. A corrupted staged archive was rejected. Release catalog/staging used local fixtures, not a live GitHub Release.

Recovery was exercised by installing a deliberately broken, local-only 0.1.3 fixture. The detached recovery guard survived termination of only the dedicated test host, waited for the failed health check, and used the native DSH CLI to restore 0.1.2 (exit code 0). Restart confirmed 0.1.2, three saved prompt sentinels including post-backup additions, the saved edited revision, failed-version blocking and cleared pending state. The initial test harness killed the whole process tree and was invalid; the independent hidden-host rerun is the successful evidence. No daily desktop profile was restarted or modified.

Phases 6–7: final archive is `dsh-shopify-page-studio-0.1.2.tgz`, SHA-256 `ba092a58791c3f953a7e7defaa04bc2b655d15c0d0067be326141f43162b914f`. Recovery eligibility is enabled only if the freshly packed archive exactly matches this recorded evidence. Nine unit tests pass; frontend JavaScript syntax checks pass. Package whitelist excludes credentials, runtime user state, generated test results and node_modules. Windows installation ZIP includes the archive, checksums, update metadata, installer and documentation.

## Remaining acceptance boundaries

- Native GUI visual acceptance remains manual: the computer-use tool stopped because it could not reliably identify the browser URL. No further GUI control was attempted. User should confirm the Page Studio launcher and editor after installation.
- GitHub repository has not been supplied. No push, tag, Release, remote CI run or live cross-network upgrade is claimed. The included workflow has not run remotely. Empty update repository correctly reports source-unconfigured.
- Current update transport supports public anonymous GitHub Releases; private repository authentication is not implemented.
- The production 0.1.2 archive excludes the intentionally broken fixture and the local verification overlay. Local integration artifacts and audit extraction remain ignored.
