# End-to-End DevOps & Deployment Guide: SmallApp

This guide walks through every step to connect **GitHub**, **Azure DevOps**, and **AWS EC2**, execute **Git PR & Merge workflows**, publish **Azure Artifacts**, and deploy with **Docker**.

---

## 1. Git Operations: Branching, PRs & Merges

### Branching Architecture
```
main (Master Gateway: Home Page + Orchestration)
  │
  ├── feature/feature-1 ──── PR #1 ───> Merged to main (Feature 1 Single Page)
  │
  └── feature/feature-2 ──── PR #2 ───> Merged to main (Feature 2 Diagnostics)
```

### Local Branches Status in this Repository
All branches are already initialized and tested:
```bash
git branch -a
# * main
#   feature/feature-1
#   feature/feature-2
```

### Step-by-Step GitHub PR & Merge Workflow

1. **Push all branches to your GitHub repository:**
   ```bash
   git remote add origin https://github.com/<your-username>/SmallApp.git
   git push -u origin --all
   ```

2. **Open Pull Requests on GitHub:**
   * Go to **GitHub > Pull Requests > New Pull Request**.
   * **PR #1**: Base: `main` &larr; Compare: `feature/feature-1`
     - Title: `feat(feature1): Add single page analytics calculator and standalone server`
     - Description: Includes Feature 1 blueprint, template, standalone runner, and unit tests.
   * **PR #2**: Base: `main` &larr; Compare: `feature/feature-2`
     - Title: `feat(feature2): Add system diagnostics telemetry and standalone server`
     - Description: Includes Feature 2 blueprint, template, standalone runner, and unit tests.

3. **Branch Protection & PR Policy:**
   * In GitHub: **Settings > Branches > Add branch protection rule**.
   * Branch pattern: `main`.
   * Enable:
     - *Require a pull request before merging*.
     - *Require status checks to pass before merging* (select Azure DevOps PR build).
     - *Require branches to be up to date before merging*.

4. **Merge Pull Requests:**
   * Merge via GitHub web interface using **Create a merge commit** (or Squash and Merge).
   * Notice that in this repository, both PRs have also been pre-merged locally into `main` using `--no-ff` merge commits so the combined app can be tested immediately!

---

## 2. Connecting GitHub with Azure DevOps

### Step 1: Create Azure DevOps Project
1. Log in to [Azure DevOps](https://dev.azure.com/).
2. Click **+ New Project** &rarr; Name it `SmallApp-CI-CD` &rarr; Visibility: Public or Private.

### Step 2: Create GitHub Service Connection
1. In your Azure DevOps project, navigate to **Project Settings** (bottom left gear icon).
2. Under **Pipelines**, click **Service connections**.
3. Click **New service connection** &rarr; select **GitHub**.
4. Choose **OAuth**, **Personal Access Token (PAT)**, or **GitHub App**:
   * If using PAT: Generate a PAT in GitHub (**Settings > Developer settings > Personal access tokens**) with scopes `repo`, `admin:repo_hook`.
5. Name the connection `github-connection` and grant access permission to all pipelines.

### Step 3: Create Azure Pipeline from GitHub
1. In Azure DevOps, go to **Pipelines > Pipelines** &rarr; click **Create Pipeline**.
2. **Where is your code?** &rarr; Select **GitHub (YAML)**.
3. Select your repository `SmallApp`.
4. Select **Existing Azure Pipelines YAML file** &rarr; Path: `/azure-pipelines.yml`.
5. Review the pipeline configuration and click **Run**.

### Step 4: Configure PR Validation Trigger
1. In Azure DevOps, go to **Pipelines > Pipelines** &rarr; click your pipeline &rarr; **Edit** &rarr; **Triggers**.
2. Under **Pull request validation**, enable PR validation for branch `main`.
3. Every time a PR is opened from `feature/feature-1` or `feature/feature-2`, Azure DevOps will automatically run Stage 1 (Tests, JUnit, Code Coverage) and block merging if tests fail!

---

## 3. Azure Artifacts & Build Drop

### Pipeline Drop Artifact
In `azure-pipelines.yml`, Stage 2 packages the deployable application bundle:
```yaml
- task: ArchiveFiles@2
  inputs:
    rootFolderOrFile: '$(System.DefaultWorkingDirectory)'
    archiveFile: '$(Build.ArtifactStagingDirectory)/smallapp-$(Build.BuildId).zip'

- task: PublishPipelineArtifact@1
  inputs:
    targetPath: '$(Build.ArtifactStagingDirectory)'
    artifact: 'drop'
    publishLocation: 'pipeline'
```
* The artifact `drop` is available directly under **Pipeline Runs > Artifacts > drop**.
* You can download `smallapp-<build_id>.zip` for direct server deployments.

### Publishing to an Azure Artifacts Feed (Universal Package / PyPI)
If you want to publish to an Azure Artifacts Feed:
1. Go to **Azure DevOps > Artifacts** &rarr; Click **+ Create Feed** (e.g. `smallapp-feed`).
2. Add this snippet to `azure-pipelines.yml` under Stage 2:
```yaml
- task: UniversalPackages@0
  displayName: 'Publish to Azure Artifacts Feed'
  inputs:
    command: 'publish'
    publishDirectory: '$(Build.ArtifactStagingDirectory)'
    feedsToUsePublish: 'internal'
    vstsFeedPublish: 'SmallApp-CI-CD/smallapp-feed'
    vstsFeedPackagePublish: 'smallapp-server'
    packagePublishDescription: 'SmallApp Production Build Package'
```

---

## 4. Deploying to AWS EC2

### Step 1: Launch an AWS EC2 Instance
1. In the **AWS Management Console**, navigate to **EC2 > Launch Instance**.
2. **Name**: `SmallApp-Server`
3. **AMI**: Amazon Linux 2023 or Ubuntu 22.04 LTS.
4. **Instance Type**: `t3.micro` or `t3.medium`.
5. **Key Pair**: Select or create an SSH key pair (`smallapp-key.pem`).
6. **Network & Security Group**:
   * Allow **SSH (Port 22)** from your IP / Azure DevOps agent IP.
   * Allow **HTTP (Port 80)** from Anywhere (`0.0.0.0/0`).
   * Allow **Custom TCP (Port 5000)** from Anywhere (Main App).
   * Allow **Custom TCP (Port 5001)** (Feature 1 Standalone).
   * Allow **Custom TCP (Port 5002)** (Feature 2 Standalone).
7. **Advanced Details > User Data**:
   * Paste the contents of `deploy/ec2-userdata.sh`.
   * Click **Launch Instance**.

### Step 2: Configure Azure DevOps SSH Service Connection
1. In Azure DevOps **Project Settings > Service connections** &rarr; **New service connection** &rarr; **SSH**.
2. Fill in:
   * **Connection Name**: `MyAwsEc2SshConnection`
   * **Host name**: Your EC2 Public IPv4 address or DNS.
   * **Port number**: `22`
   * **User name**: `ubuntu` (for Ubuntu) or `ec2-user` (for Amazon Linux).
   * **Private key**: Paste the private key text from `smallapp-key.pem`.
3. Save and authorize for all pipelines.

### Step 3: Run Continuous Deployment
When code is merged to `main`:
1. Azure DevOps runs tests & generates code coverage.
2. Builds the deployable artifact zip & pushes Docker image.
3. The `Deploy_to_AWS_EC2` stage invokes `deploy/deploy-ec2.sh` on your EC2 instance over SSH, replacing the old container with the new version with zero downtime.

---

## 5. Fitting Features Easily into a New Server

A key requirement is: **"second page should be in feature 2 so that can easily fit in new server"**.

Here are 3 ways to deploy features across separate servers:

### Option A: Standalone Python Microservice Mode
To run Feature 1 on **Server A (Port 5001)**:
```bash
python -m app.features.feature1.standalone --host 0.0.0.0 --port 5001
```

To run Feature 2 on **Server B (Port 5002)**:
```bash
python -m app.features.feature2.standalone --host 0.0.0.0 --port 5002
```

### Option B: Dockerized Standalone Microservices
Using the included `docker-compose.yml`:
```bash
# Starts Feature 1 standalone on port 5001 and Feature 2 standalone on port 5002
docker compose up -d feature1-microservice feature2-microservice
```

### Option C: Environment Feature Toggling on Separate EC2 Instances
You can deploy the exact same codebase on multiple EC2 instances with different feature toggles:
* **Server 1 (Home + Feature 1 only):**
  ```bash
  export ENABLE_FEATURE_1=true
  export ENABLE_FEATURE_2=false
  gunicorn --bind 0.0.0.0:5000 run:app
  ```
* **Server 2 (Feature 2 only on new server):**
  ```bash
  export ENABLE_FEATURE_1=false
  export ENABLE_FEATURE_2=true
  gunicorn --bind 0.0.0.0:5000 run:app
  ```
