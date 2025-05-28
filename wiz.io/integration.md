Here are some examples of Wiz.io GitLab integration:

**1. Integrating Wiz CLI with GitLab CI/CD**

To integrate Wiz CLI with GitLab CI/CD, you can use the `wizcli` command in your `.gitlab-ci.yml` file. For example:
```yaml
stages:
  - security

security:
  stage: security
  script:
    - wizcli auth --id $CI_PROJECT_ID --secret $CI_PROJECT_TOKEN
    - wizcli scan --config-path ./wiz-config.yaml
```
**2. Using Wiz CLI as a GitLab hook**

You can also use Wiz CLI as a GitLab hook to run scans on your codebase before pushing changes. To do this, you'll need to create a `.gitlab/hooks/post-receive` file in your repository with the following contents:
```bash
#!/bin/bash

wizcli auth --id $CI_PROJECT_ID --secret $CI_PROJECT_TOKEN
wizcli scan --config-path ./wiz-config.yaml
```
**3. Integrating Wiz CLI with GitLab's CI/CD pipeline**

You can also integrate Wiz CLI with GitLab's CI/CD pipeline using the `wizcli` command in your `.gitlab-ci.yml` file. For example:
```yaml
stages:
  - security

security:
  stage: security
  script:
    - wizcli auth --id $CI_PROJECT_ID --secret $CI_PROJECT_TOKEN
    - wizcli scan --config-path ./wiz-config.yaml
```
**4. Using Wiz CLI with GitLab's Adaptive Shield**

You can also use Wiz CLI with GitLab's Adaptive Shield to manage users, roles, and risks. To do this, you'll need to create a `wizcli` command in your `.gitlab-ci.yml` file with the following contents:
```yaml
stages:
  - security

security:
  stage: security
  script:
    - wizcli auth --id $CI_PROJECT_ID --secret $CI_PROJECT_TOKEN
    - wizcli adaptive-shield --config-path ./wiz-config.yaml
```
These are just a few examples of how you can integrate Wiz.io with GitLab. You can customize the `wizcli` commands to fit your specific use case.