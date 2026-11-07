# Promotion flow

The web app example (`examples/web-app-pipeline.yml`) promotes one build artifact through every environment.
Nothing is rebuilt between environments.

```mermaid
flowchart LR
    PR[Pull request] --> B
    M[Merge to main] --> B
    B[Build and unit test] --> S[Security scans]
    S -->|main only| D[Deploy DEV]
    D --> T[Playwright smoke DEV]
    T --> U[Deploy UAT]
    U --> G[Release gate]
    G --> P[Deploy PRD]
    A1{{Approval: UAT environment}} -.-> U
    A2{{Business hours and manual validation}} -.-> G
    A3{{Approval: PRD environment}} -.-> P
    B -. failure .-> N[Notify Teams]
    S -. failure .-> N
    D -. failure .-> N
    U -. failure .-> N
    P -. failure .-> N
```

Pull requests stop after the scan stage. Deploy stages only run for non-PR builds.

Each App Service deployment runs this sequence inside its environment:

```mermaid
sequenceDiagram
    participant Pipe as Pipeline
    participant Slot as Staging slot
    participant Prod as Production slot
    Pipe->>Slot: Deploy package
    Pipe->>Slot: Health check
    Pipe->>Prod: Swap slots
    Pipe->>Prod: Health check
    alt health check fails
        Pipe->>Prod: Swap again (roll back)
    end
```

The infrastructure example follows the same pattern with Bicep. For each environment, `validate_<env>` runs build, lint and
what-if without any approval, then `deploy_<env>` waits for the environment approval.

```mermaid
flowchart LR
    V1[validate_dev] --> D1[deploy_dev] --> V2[validate_uat] --> D2[deploy_uat] --> V3[validate_prd] --> D3[deploy_prd]
```
