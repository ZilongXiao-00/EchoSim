# Grammar Check Forum with AWS Bedrock

## Overview

This demo showcases how to integrate **AWS Bedrock** with OpenAgents by creating a grammar-checking forum powered by Claude 3.5 Haiku. This is a variant of Demo 4 that demonstrates using AWS-hosted models instead of direct API access.

**Key Features:**
- AWS Bedrock integration with Claude 3.5 Haiku
- Enterprise-grade infrastructure via AWS
- Automated grammar checking in a forum setting
- Cost-effective with Haiku's fast, affordable responses
- Latest Claude 3.5 model with improved performance

## Why AWS Bedrock?

AWS Bedrock provides several advantages:
- **Enterprise Security**: AWS infrastructure with VPC, encryption, compliance
- **Unified Billing**: Consolidate AI costs with existing AWS spend
- **Regional Deployment**: Keep data within specific AWS regions
- **IAM Integration**: Fine-grained access control via AWS IAM
- **No Direct API Keys**: Use AWS credentials instead of Anthropic API keys

## Prerequisites

### 1. AWS Account Setup

You need an AWS account with:
- Active AWS Bedrock service enabled
- Claude models enabled in your region
- Appropriate IAM permissions

### 2. Enable AWS Bedrock

1. Sign in to AWS Console
2. Navigate to **Amazon Bedrock** service
3. Click **Model access** in the left sidebar
4. Click **Manage model access**
5. Enable **Anthropic Claude** models:
   - ✅ Claude 3.5 Haiku
   - ✅ Claude 3.5 Sonnet (optional)
   - ✅ Claude 3 Opus (optional)
6. Click **Request model access**
7. Wait for approval (usually instant for Claude models)

### 3. IAM Permissions

Your AWS user/role needs these permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-5-haiku-20241022-v1:0",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
      ]
    }
  ]
}
```

### 4. AWS Credentials Configuration

Choose one of the following methods:

#### Method A: AWS CLI (Recommended for Local Development)

```bash
# Install AWS CLI if not already installed
pip install awscli

# Configure credentials
aws configure
# AWS Access Key ID [None]: YOUR_ACCESS_KEY
# AWS Secret Access Key [None]: YOUR_SECRET_KEY
# Default region name [None]: us-east-1
# Default output format [None]: json
```

#### Method B: Environment Variables

```bash
export AWS_ACCESS_KEY_ID="AKIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
export AWS_DEFAULT_REGION="us-east-1"
```

#### Method C: IAM Role (For EC2/ECS/Lambda)

If running on AWS infrastructure, attach an IAM role with Bedrock permissions. No credential configuration needed.

```bash
# Verify role has correct permissions
aws sts get-caller-identity
```

#### Method D: AWS Credentials File

Create `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

Create `~/.aws/config`:

```ini
[default]
region = us-east-1
output = json
```

### 5. Verify Bedrock Access

Test your Bedrock access:

```bash
# List available foundation models
aws bedrock list-foundation-models --region us-east-1

# Check if Claude 3.5 Haiku is available
aws bedrock list-foundation-models \
  --region us-east-1 \
  --query 'modelSummaries[?contains(modelId, `claude-3-5-haiku`)]'
```

Expected output should include:
```json
{
  "modelId": "anthropic.claude-3-5-haiku-20241022-v1:0",
  "modelName": "Claude 3.5 Haiku",
  "providerName": "Anthropic"
}
```

### 6. OpenAgents Installation

```bash
pip install openagents
```

## Architecture

```
┌─────────────────────────────────────────────────┐
│                    Forum                        │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  User Post: "I wants to learning..."    │   │
│  └─────────────────────────────────────────┘   │
│                      │                          │
│                      ▼ forum.topic.created      │
│            ┌─────────────────┐                  │
│            │ grammar-checker │                  │
│            │   AWS Bedrock   │                  │
│            │ Claude 3.5 Haiku│                  │
│            │                 │                  │
│            │ - Find errors   │                  │
│            │ - Explain fixes │                  │
│            │ - Provide tips  │                  │
│            └─────────────────┘                  │
│                      │                          │
│                      ▼ AWS API Call             │
│         ┌────────────────────────────┐          │
│         │   Amazon Bedrock Service   │          │
│         │  Claude 3 Haiku Model      │          │
│         └────────────────────────────┘          │
│                      │                          │
│                      ▼ reply                    │
│  ┌─────────────────────────────────────────┐   │
│  │  Grammar Check Results:                 │   │
│  │  1. "wants" → "want"                    │   │
│  │  2. "to learning" → "to learn"          │   │
│  │  Corrected: "I want to learn..."        │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

## Quick Start

### Step 1: Configure AWS Credentials

```bash
# Verify AWS credentials are configured
aws sts get-caller-identity

# Should output your AWS account info
```

### Step 2: Start the Network

```bash
cd demos/07_grammar_check_forum_bedrock
openagents network start network.yaml
```

Expected output:
```
INFO: Starting network GrammarCheckForumBedrock
INFO: HTTP transport listening on 0.0.0.0:8700
INFO: gRPC transport listening on 0.0.0.0:8600
INFO: Forum mod loaded
INFO: Network ready
```

### Step 3: Launch the Agent

Open a new terminal:

```bash
cd demos/07_grammar_check_forum_bedrock
openagents launch-agent agents/grammar_checker.yaml
```

Expected output:
```
INFO: Agent grammar-checker starting
INFO: Model: anthropic.claude-3-5-haiku-20241022-v1:0
INFO: Provider: bedrock
INFO: Region: us-east-1
INFO: Connected to network at localhost:8700
INFO: Listening for forum events
```

### Step 4: Connect via Studio

Open a third terminal:

```bash
cd studio
npm start
```

Navigate to `http://localhost:8050` and connect to the network at `localhost:8700`.

### Step 5: Test the Grammar Checker

Create a new forum topic with intentionally incorrect grammar:

**Title:** "Please review my email"

**Content:**
```
Dear Sir,

I am writing to informed you that I will not be able to attending
the meeting tomorrow becuase I have a doctors appointment. I apologize
for any inconvenience this may caused.

Best regards
```

The grammar-checker agent will automatically reply with:
- Identified errors
- Corrections with explanations
- Fully corrected version
- Writing tips

## Configuration Details

### Agent Configuration

The key differences from the standard demo:

```yaml
type: "openagents.agents.collaborator_agent.CollaboratorAgent"
agent_id: "grammar-checker"

config:
  # Bedrock-specific configuration
  model_name: "anthropic.claude-3-5-haiku-20241022-v1:0"
  provider: "bedrock"
  region: "us-east-1"

  # Standard agent configuration
  instruction: |
    You are the GRAMMAR CHECKER...
```

### Available Bedrock Models

You can use different Claude models by changing `model_name`:

| Model | Model ID | Use Case | Cost |
|-------|----------|----------|------|
| Claude 3.5 Haiku | `anthropic.claude-3-5-haiku-20241022-v1:0` | Fast, cost-effective, latest | $ |
| Claude 3.5 Sonnet | `anthropic.claude-3-5-sonnet-20241022-v1:0` | Balanced performance, improved | $$ |
| Claude 3 Opus | `anthropic.claude-3-opus-20240229-v1:0` | Maximum capability | $$$ |

### Network Configuration

```yaml
network:
  name: "GrammarCheckForumBedrock"
  transports:
    - type: "http"
      config:
        port: 8700
    - type: "grpc"
      config:
        port: 8600

  mods:
    - name: "openagents.mods.workspace.forum"
      enabled: true
```

## Example Interactions

### Example 1: Email Writing

**User Post:**
> "I wanted to follow up on our converstion from last week. Their are a few points I think we should discussed further."

**Agent Response:**
```
✍️ Grammar Check Results

Issues Found:
1. ❌ "converstion" → ✅ "conversation"
   - Spelling correction

2. ❌ "Their are" → ✅ "There are"
   - Use "There" for existence, "Their" for possession

3. ❌ "should discussed" → ✅ "should discuss"
   - Use base form after modal verb "should"

Corrected Version:
> I wanted to follow up on our conversation from last week. There are
> a few points I think we should discuss further.

Tips:
- "Their" = belonging to them | "There" = location or existence
- After modal verbs (should, could, would), use the base form
```

### Example 2: ESL Practice

**User Post:**
> "I have been living in this city since five years. The peoples here is very friendly."

**Agent Response:**
```
✍️ Grammar Check Results

Issues Found:
1. ❌ "since five years" → ✅ "for five years"
   - Use "for" with duration, "since" with starting point

2. ❌ "peoples" → ✅ "people"
   - "People" is already plural

3. ❌ "is very friendly" → ✅ "are very friendly"
   - Subject-verb agreement: "people" takes plural verb

Corrected Version:
> I have been living in this city for five years. The people here are
> very friendly.

Tips:
- "since 2020" (point in time) vs "for 5 years" (duration)
- "people" is the plural of "person" - no 's' needed
```

## Regional Availability

Claude models on Bedrock are available in these regions:

| Region | Region Code | Claude 3.5 Haiku | Claude 3.5 Sonnet |
|--------|-------------|------------------|-------------------|
| US East (N. Virginia) | us-east-1 | ✅ | ✅ |
| US West (Oregon) | us-west-2 | ✅ | ✅ |
| Asia Pacific (Singapore) | ap-southeast-1 | ✅ | ✅ |
| Asia Pacific (Tokyo) | ap-northeast-1 | ✅ | ✅ |
| Europe (Frankfurt) | eu-central-1 | ✅ | ✅ |

To use a different region, update the agent config:

```yaml
config:
  model_name: "anthropic.claude-3-5-haiku-20241022-v1:0"
  provider: "bedrock"
  region: "ap-southeast-1"  # Singapore
```

## Cost Estimation

AWS Bedrock pricing for Claude 3.5 Haiku (as of Dec 2024):

| Action | Price |
|--------|-------|
| Input tokens | $0.25 per 1M tokens |
| Output tokens | $1.25 per 1M tokens |

**Example cost for this demo:**
- Average grammar check: ~500 input + 300 output tokens
- Cost per check: ~$0.0005 (0.05 cents)
- 1,000 grammar checks: ~$0.50

Compare to Claude API direct:
- Similar pricing
- But billed through AWS (consolidated billing)
- Volume discounts may apply

## Troubleshooting

### Error: "Could not connect to Bedrock"

**Check 1: Verify AWS credentials**
```bash
aws sts get-caller-identity
```

**Check 2: Verify region**
```bash
# List models in your configured region
aws bedrock list-foundation-models --region us-east-1
```

**Check 3: Check IAM permissions**
```bash
# Test invoke permission
aws bedrock invoke-model \
  --model-id anthropic.claude-3-5-haiku-20241022-v1:0 \
  --region us-east-1 \
  --body '{"prompt": "test", "max_tokens": 10}' \
  /tmp/output.json
```

### Error: "Model access denied"

You need to enable Claude models in Bedrock:
1. Go to AWS Console → Bedrock → Model access
2. Click "Manage model access"
3. Enable Anthropic Claude models
4. Save changes and wait for approval

### Error: "Invalid region"

Claude on Bedrock is not available in all regions. Use one of:
- `us-east-1` (N. Virginia)
- `us-west-2` (Oregon)
- `ap-southeast-1` (Singapore)
- `eu-central-1` (Frankfurt)

### Agent Not Responding

**Check agent logs:**
```bash
# Look for Bedrock-specific errors
tail -f demos/07_grammar_check_forum_bedrock/logs/grammar-checker.log
```

**Common issues:**
- AWS credentials expired → Run `aws configure` again
- Network timeout → Check AWS service health
- Rate limiting → Bedrock has default quotas (requests per minute)

### Verify Network is Running

```bash
curl http://localhost:8700/health
```

Expected response:
```json
{"status": "healthy", "network": "GrammarCheckForumBedrock"}
```

## Advanced Configuration

### Using AssumeRole for Cross-Account Access

If your Bedrock access is in a different AWS account:

```yaml
config:
  model_name: "anthropic.claude-3-5-haiku-20241022-v1:0"
  provider: "bedrock"
  region: "us-east-1"

  # Additional AWS config
  aws_profile: "bedrock-account"  # Use specific AWS profile
  # or
  role_arn: "arn:aws:iam::123456789012:role/BedrockAccessRole"
```

### Custom Retry Configuration

```yaml
config:
  model_name: "anthropic.claude-3-5-haiku-20241022-v1:0"
  provider: "bedrock"
  region: "us-east-1"

  # Retry settings for Bedrock API
  max_retries: 3
  retry_delay: 1.0
  timeout: 30
```

### VPC Endpoint Configuration

For enhanced security, use VPC endpoints:

1. Create Bedrock VPC endpoint in AWS Console
2. Configure security groups
3. No agent config changes needed - boto3 auto-detects VPC endpoints

## Migration from Direct Claude API

If you have an existing agent using Anthropic API directly:

**Before (Direct API):**
```yaml
config:
  model_name: "claude-3-haiku-20240307"
  provider: "claude"
  # Uses ANTHROPIC_API_KEY environment variable
```

**After (Bedrock):**
```yaml
config:
  model_name: "anthropic.claude-3-5-haiku-20241022-v1:0"
  provider: "bedrock"
  region: "us-east-1"
  # Uses AWS credentials
```

**Benefits of migration:**
- Enterprise security and compliance
- Consolidated AWS billing
- VPC/PrivateLink support
- AWS CloudWatch integration
- AWS Config compliance tracking

## Monitoring and Logging

### CloudWatch Logs

Bedrock automatically logs to CloudWatch. View logs:

```bash
aws logs tail /aws/bedrock/modelinvocations --follow
```

### Cost Monitoring

Track Bedrock costs in AWS Cost Explorer:
1. AWS Console → Cost Management → Cost Explorer
2. Filter by Service: "Amazon Bedrock"
3. Group by: "API Operation" or "Model ID"

### Agent Logs

Local agent logs are in:
```
demos/07_grammar_check_forum_bedrock/logs/
```

## Security Best Practices

1. **Use IAM roles** instead of access keys when possible
2. **Enable CloudTrail** to audit Bedrock API calls
3. **Use VPC endpoints** to keep traffic within AWS network
4. **Rotate credentials** regularly if using access keys
5. **Apply least privilege** IAM policies
6. **Enable AWS Config** to track compliance
7. **Use AWS KMS** for encryption at rest

## Related Documentation

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Anthropic Claude on Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-claude.html)
- [OpenAgents Forum Mod Guide](https://openagents.org/docs/mods/forum)
- [OpenAgents LLM Provider Configuration](https://openagents.org/docs/llm-providers)

## Next Steps

- Try different Claude models (Sonnet, Opus)
- Deploy to AWS ECS/Fargate for production
- Add CloudWatch monitoring and alerts
- Integrate with AWS Lambda for serverless deployment
- Use AWS Secrets Manager for credential management
- Set up VPC endpoints for enhanced security
