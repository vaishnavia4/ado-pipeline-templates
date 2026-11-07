# Environments, approvals and service connections

Approvals and checks are attached to Azure DevOps environments, not to YAML. Every deployment template uses a
`deployment` job with `environment:`, which is what makes the checks apply.

## Environment layout

| Environment | Approvals | Checks | Branch control |
| --- | --- | --- | --- |
| `contoso-web-dev` | none | none | any |
| `contoso-web-uat` | one approver group | business hours optional | `main` |
| `contoso-web-prd` | two approvers, requester cannot approve | business hours, required template | `main` |

Create one environment per application and stage, for example `contoso-infra-dev`, `contoso-infra-uat`, `contoso-infra-prd`.

## Setting up an environment

1. Pipelines, Environments, New environment, resource type None.
2. Approvals and checks, add Approvals. Choose a group, tick "Requester cannot approve", set a timeout.
3. Add Branch control and allow only `refs/heads/main` for UAT and PRD.
4. For production add Business hours and Required template (point it at `templates/pipelines/...` in the template repository).
5. Add Exclusive lock when two runs must never deploy to the same environment at once.

## Release gates template

`stages/release-gates.yml` adds gates that run before a deployment stage:

- business hours window in a named time zone and a weekday list
- `ManualValidation@0` on the server pool, rejects on timeout
- optional environment gate, a no-op deployment job that triggers the environment approvals early

Use the environment checks as the authoritative control. The template adds visibility and earlier feedback.

## Service connections

Create Azure Resource Manager connections with **workload identity federation** (automatic or manual).
No secret is stored and nothing expires.

| Purpose | Role | Scope |
| --- | --- | --- |
| Bicep what-if (plan) | Reader plus `Microsoft.Resources/deployments/whatIf/action` | resource group or subscription |
| Bicep or Terraform deploy | Contributor, or a narrower custom role | the target resource group |
| App Service deploy | Website Contributor | the web app |
| Container push | AcrPush | the registry |

Rules that keep this safe:

- One connection per environment, never shared between DEV and PRD.
- Restrict each connection to the pipelines that need it (pipeline permissions) and add a branch control check for PRD.
- Do not grant Owner or User Access Administrator to a pipeline identity. Role assignments belong in a separate, reviewed pipeline.

## Variable groups and Key Vault

Link a variable group to Key Vault (Pipelines, Library, "Link secrets from an Azure key vault as variables").
Grant the connection used for the link `Get` and `List` on secrets only. Reference the group through the `variableGroup`
parameter of the deploy, test and notify templates. Secret values are masked in logs and are mapped to `env:` where used.
