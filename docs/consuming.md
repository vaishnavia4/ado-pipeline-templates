# Consuming the templates

## 1. Allow access to the template repository

The consuming pipeline must be able to read the template repository.
In the template project, give the consuming project's build service identity `Read` on the repository
(Project Settings, Repositories, Security). If the repository lives in another project, also turn off
"Limit job authorization scope to referenced Azure DevOps repositories" or add the repository as a resource.

## 2. Declare the repository resource

```yaml
resources:
  repositories:
    - repository: templates          # alias used after the @ sign
      type: git
      name: contoso-platform/ado-pipeline-templates
      ref: refs/tags/v1.0.0          # always a tag
```

## 3. Use a template

Stage templates plug into `stages:` and take `dependsOn`, `condition` and `pool` like a normal stage:

```yaml
stages:
  - template: templates/stages/build-node.yml@templates
    parameters:
      nodeVersion: 20.x
  - template: templates/stages/security-scans.yml@templates
    parameters:
      dependsOn:
        - build
```

Paths inside the template repository are written as `templates/...@templates`. Templates reference each other with
relative paths, so you never need the alias inside the library.

## 4. Or enforce a shape with `extends`

`templates/pipelines/infra-bicep.yml` owns the whole stage graph. The consuming pipeline only supplies data:

```yaml
extends:
  template: templates/pipelines/infra-bicep.yml@templates
  parameters:
    environments:
      - name: dev
        # see examples/infra-pipeline.yml
```

Pair `extends` with environment checks of type "Required template" so that production environments only accept
pipelines that extend a trusted template.

## Parameters

All parameters, types and defaults are in [parameters.md](parameters.md). Parameters without a default are required.

## Validating locally

```bash
pip install -r requirements-dev.txt
yamllint --strict .
python -m pytest
```

To check a consuming pipeline against the Azure DevOps parser without running it, use the
"Validate" option in the pipeline editor or the pipelines preview REST endpoint.
