# Branching and versioning the template repository

Consumers pin a tag, so template changes roll out on the consumer's schedule.

## Branching

- `main` is always releasable. Protect it: pull request required, build validation runs the quality gates, no direct pushes.
- Short-lived topic branches (`feat/...`, `fix/...`) merge by pull request.
- To try a change in a real pipeline, point a test pipeline at the topic branch with `ref: refs/heads/feat/my-change`.
  Never leave a branch reference in a production pipeline.

## Tags

Semantic versioning with a leading `v`.

| Change | Bump | Example |
| --- | --- | --- |
| Breaking: removed or renamed parameter, changed default behavior, new required parameter | major | `v2.0.0` |
| New template, new optional parameter | minor | `v1.3.0` |
| Bug fix, documentation | patch | `v1.3.1` |

Create annotated tags from `main` after the quality gates pass:

```bash
git tag -a v1.3.0 -m "Add terraform-plan stage"
git push origin v1.3.0
```

Optionally keep a moving major tag (`v1`) for teams that want fixes automatically. Move it only for patch and minor releases:

```bash
git tag -fa v1 -m "v1 -> v1.3.0"
git push origin v1 --force
```

Protect `v*` tags with a tag security policy so only the platform team can create or move them.

## Deprecation policy

1. Add the new parameter or template alongside the old one in a minor release and mark the old one deprecated in its comment.
2. Keep the old behavior for at least one minor release cycle.
3. Remove it in the next major release and list it in `CHANGELOG.md` under "Breaking".

## Upgrading a consumer

1. Read `CHANGELOG.md` between the current and target tag.
2. Change `ref: refs/tags/vX.Y.Z` in a branch and open a pull request.
3. Run the pipeline with the stages that deploy turned off, or against DEV only, before merging.

## Application versioning

`steps/set-version.yml` supports two strategies:

- `buildNumber`: `<majorMinor>.<BuildId>`, the default, no extra tooling.
- `gitversion`: semantic version from git history, needs the GitVersion extension and a full clone (the templates set `fetchDepth: 0`).

Both set the `appVersion` variable and update the build number so stages, artifacts and image tags agree.
