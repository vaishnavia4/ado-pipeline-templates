# Conventions

## Layout

| Folder | Contents |
| --- | --- |
| `templates/stages` | A `stages:` fragment. The unit consumers use most. |
| `templates/jobs` | A `jobs:` fragment, reused by stage templates. |
| `templates/steps` | A `steps:` fragment for small shared pieces. |
| `templates/pipelines` | Full pipeline bodies meant for `extends:`. |
| `examples` | Complete pipelines that consume the library. Tested against the templates. |

## Parameters

- Every parameter has a comment on the line directly above `- name:`. The comment becomes the description in
  [parameters.md](parameters.md), and a test fails if it is missing.
- Regenerate the reference with `python scripts/gen_param_docs.py` after changing any parameter.
- Stage templates always accept `stageName`, `dependsOn`, `condition` and `pool` where they make sense.
- Use `type:` on every parameter. Use `values:` for enumerations.
- A parameter without a default is required. Keep required parameters to the minimum that cannot be guessed.
- Never add a parameter that carries a secret. Pass a variable group name or a service connection name instead.

## Naming

- Stage names use `snake_case` and are unique per pipeline: `build`, `scan`, `deploy_dev`.
- Artifact names are unique per run. Templates that publish take an `artifactName` parameter.
- Environments are `<app>-<env>`: `contoso-web-uat`.
- Service connections are `sc-<app>-<purpose>-<env>`.

## Security defaults

- Workload identity federation for every Azure service connection.
- `checkout: self` with `persistCredentials: false` through `steps/checkout-secure.yml`.
- Tasks pinned to a major version (`AzureCLI@2`). Downloaded tools are pinned to an exact version and checksum verified.
- Hosted images are pinned (`ubuntu-24.04`) instead of `ubuntu-latest`, so image changes are deliberate.
- Parameters reach scripts through `env:`, not through `${{ }}` inside script text.
- Secrets come from Key Vault linked variable groups and are mapped to `env:` per step.
- Deployment jobs use `environment:` so approvals and checks apply.
- Least privilege: separate plan and deploy identities, one identity per environment.

## Marketplace tasks

Tasks such as `SnykSecurityScan@1`, `SonarCloudPrepare@3`, `gitversion/execute@3` and `TerraformInstaller@1` come from
extensions that must be installed in the organization. Each use has a `TODO` comment to confirm the major version your
installed extension provides. Replace the comment once you have verified it.

## Quality gates

Pull requests must pass `yamllint --strict .`, `python scripts/gen_param_docs.py --check` and `python -m pytest`.
The tests check that parameters are documented, that examples reference real templates with valid parameters,
and that the repository has no em dashes or obvious secrets.
