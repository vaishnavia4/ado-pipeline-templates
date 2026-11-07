# ado-pipeline-templates

Reusable Azure DevOps YAML templates and example pipelines for build, scan, infrastructure and release workflows.
Teams consume them through `resources.repositories` plus `template:` or `extends:`, pinned to a version tag.
Security defaults are built in: workload identity federation, no secrets in YAML, pinned versions, approvals on environments.

## Template catalog

| Template | Purpose |
| --- | --- |
| `stages/build-dotnet.yml` | Restore, build, test with coverage, publish a .NET app |
| `stages/build-node.yml` | npm cache, lint, test, build, publish a Node.js app |
| `stages/build-python.yml` | pip cache, lint, pytest with coverage, package a Python app |
| `stages/bicep-validate.yml` | Bicep build, linter, what-if (no approval needed), plan artifact |
| `stages/bicep-deploy.yml` | Deployment job per environment with approvals and checks |
| `stages/terraform-plan.yml` | Terraform init, validate, plan with OIDC (optional) |
| `stages/terraform-apply.yml` | Apply the saved plan behind an environment (optional) |
| `stages/container-build-push.yml` | Build and push to ACR using workload identity federation |
| `stages/app-service-deploy.yml` | Slot deploy, health check, swap, verify, roll back on failure |
| `stages/playwright-tests.yml` | Playwright run, JUnit results, HTML report artifact |
| `stages/security-scans.yml` | gitleaks, Snyk, SonarCloud or SonarQube, fail on high |
| `stages/release-gates.yml` | Business-hours check, manual validation, environment approvals |
| `stages/notify-teams.yml` | Teams message when a watched stage fails |
| `pipelines/infra-bicep.yml` | `extends` template: validate, what-if, deploy for each environment |
| `jobs/*`, `steps/*` | Shared building blocks (build jobs, caching, versioning, checkout, publish) |

Every parameter is listed in [docs/parameters.md](docs/parameters.md).

## Quickstart

Reference the repository from a pipeline in another repository and pin a tag:

```yaml
resources:
  repositories:
    - repository: templates
      type: git
      name: contoso-platform/ado-pipeline-templates
      ref: refs/tags/v1.0.0

stages:
  - template: templates/stages/build-dotnet.yml@templates
    parameters:
      solution: src/Contoso.Web.sln
      publishProjects: src/Contoso.Web/Contoso.Web.csproj
```

Full examples live in [examples/](examples/):

- `web-app-pipeline.yml`: build, test, scan, deploy DEV, UAT (approval), PRD (approval)
- `infra-pipeline.yml`: Bicep validate, what-if, deploy per environment through `extends`
- `nightly-playwright.yml`: scheduled regression run with a failure notification

More in [docs/](docs/): [consuming the templates](docs/consuming.md), [environments and approvals](docs/environments-and-approvals.md),
[versioning](docs/versioning.md), [promotion flow](docs/promotion-flow.md), [conventions](docs/conventions.md).

## Security notes

- Service connections use workload identity federation. No client secrets, no registry passwords.
- Plan and deploy use separate identities so what-if never needs write access.
- `checkout: self` runs with `persistCredentials: false`.
- Secrets reach pipelines only through variable groups linked to Key Vault and are mapped into `env:`, never into YAML or script text.
- Task versions are pinned to a major version, tools such as gitleaks are pinned and checksum verified.
- Approvals and checks belong to Azure DevOps environments, so a pipeline author cannot remove them from YAML.
- Snyk uses an API token service connection because it has no federation option. Treat that token as the one exception.
- Template parameters flow into scripts through environment variables to avoid command injection.

## Quality gates

```bash
pip install -r requirements-dev.txt
yamllint --strict .
python scripts/gen_param_docs.py --check
python -m pytest
```

The same checks run in GitHub Actions (`.github/workflows/validate.yml`). Tests verify that every parameter is documented,
every example references templates that exist with valid parameters, and the repository contains no em dashes or obvious secrets.

## Status

The templates were written against current Azure Pipelines syntax but have not been run in a live organization.
Places where a Marketplace task version should be confirmed are marked `TODO` in the YAML.

## License

MIT, see [LICENSE](LICENSE). Copyright (c) 2026 Vaishnavi Akki.

## Author

Vaishnavi Akki: [GitHub](https://github.com/vaishnavia4) | [Portfolio](https://vaishnavia4.github.io/Vaishnavi-Portfolio/)
