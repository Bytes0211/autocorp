# AWS Amplify Deployment Guide - AutoCorp AI Chatbox

**Status**: Frontend Code Ready | AWS Console Setup Required  
**Date**: January 1, 2026

---

## Overview

The AutoCorp AI Chatbox frontend is built with Next.js and ready for deployment to AWS Amplify. The code is committed to GitHub and includes all necessary configuration files.

**GitHub Repository**: `git@github.com:Bytes0211/autocorp.git`  
**Frontend Path**: `frontend/autocorp-chatbox/`  
**Branch**: `main`

---

## Prerequisites Completed ✅

- [x] Next.js application built and tested (builds in 1.5s)
- [x] React components implemented (ChatBox, MessageList, InputBar, ChatHeader)
- [x] API client configured for Lambda integration
- [x] Environment variables defined (`NEXT_PUBLIC_API_ENDPOINT`, `NEXT_PUBLIC_API_KEY`)
- [x] Build specification file (`amplify.yml`) created
- [x] Code committed and pushed to GitHub
- [x] API Gateway tested and operational

---

## Deployment Steps (AWS Console)

### Step 1: Navigate to AWS Amplify Console

1. Log in to AWS Console: https://console.aws.amazon.com
2. Navigate to **AWS Amplify** service
3. Click **"New app"** → **"Host web app"**

### Step 2: Connect GitHub Repository

1. Select **"GitHub"** as the repository service
2. Click **"Authorize AWS Amplify"** (one-time OAuth setup)
3. Select repository: **Bytes0211/autocorp**
4. Select branch: **main**
5. Click **"Next"**

### Step 3: Configure Build Settings

Amplify will auto-detect the Next.js app. Verify the following:

**App name**: `autocorp-chatbox-dev`

**Build spec file location**: `frontend/autocorp-chatbox/amplify.yml`

**Root directory**: `frontend/autocorp-chatbox`

**Environment variables** (click "Advanced settings"):
```
NEXT_PUBLIC_API_ENDPOINT=https://1fml3yigqh.execute-api.us-east-1.amazonaws.com/dev
NEXT_PUBLIC_API_KEY=nWU3TtU4G88fmNm0VDLyBONFlvx6gwE6WZGRTEY7
```

Click **"Next"**

### Step 4: Review and Deploy

1. Review all settings
2. Click **"Save and deploy"**
3. Wait for build to complete (typically 3-5 minutes)

### Step 5: Access Application

Once deployment completes:

1. Note the Amplify URL: `https://main.XXXXXXXX.amplifyapp.com`
2. Click the URL to open the chatbox
3. Test with a sample query: "What is an oil change?"

---

## Build Specification (amplify.yml)

The build spec is already configured in the repository:

```yaml
version: 1
frontend:
  phases:
    preBuild:
      commands:
        - npm ci
    build:
      commands:
        - npm run build
  artifacts:
    baseDirectory: .next
    files:
      - '**/*'
  cache:
    paths:
      - node_modules/**/*
```

---

## Expected Build Output

**Duration**: 3-5 minutes  
**Build steps**:
1. ✅ Provision (30s)
2. ✅ Build (2-3 min) - npm install + Next.js build
3. ✅ Deploy (30s)
4. ✅ Verify (10s)

**Artifacts**: `.next/` directory containing compiled Next.js app

---

## Testing the Deployed Application

### Manual Testing

1. Open the Amplify URL in a browser
2. Verify the chatbox interface loads
3. Test chat functionality:
   - Enter: "What parts are needed for an oil change?"
   - Expected: Response from Bedrock Nova Pro with part details
4. Check response time (~3 seconds)
5. Test error handling (disconnect network, verify error message)

### API Integration Test

The deployed app connects to:
- **API Gateway**: `https://1fml3yigqh.execute-api.us-east-1.amazonaws.com/dev`
- **Lambda Functions**: `autocorp-chat-handler-dev`, `autocorp-analytics-query-dev`
- **Bedrock Knowledge Base**: `UQSLM6QEVT`

### CORS Verification

API Gateway is configured with CORS enabled for all origins. If you encounter CORS errors:

1. Check API Gateway CORS settings
2. Verify `x-api-key` header is included
3. Check browser console for specific error messages

---

## Alternative Deployment (Manual via CLI)

If AWS Console access is unavailable, use the Amplify CLI:

### Install Amplify CLI
```bash
npm install -g @aws-amplify/cli
amplify configure
```

### Initialize Amplify in Project
```bash
cd /home/scotton/dev/projects/autocorp/frontend/autocorp-chatbox
amplify init
```

Follow prompts:
- Environment name: `dev`
- Default editor: (your choice)
- App type: `javascript`
- Framework: `react`
- Source directory: `.`
- Distribution directory: `.next`
- Build command: `npm run build`
- Start command: `npm run start`

### Deploy
```bash
amplify publish
```

---

## Troubleshooting

### Build Fails with "npm ci" Error

**Cause**: package-lock.json mismatch  
**Solution**: Regenerate lock file locally and commit:
```bash
cd frontend/autocorp-chatbox
rm package-lock.json
npm install
git add package-lock.json
git commit -m "Update package-lock.json"
git push
```

### 404 Error After Deployment

**Cause**: Next.js routing not configured  
**Solution**: Verify `amplify.yml` artifact configuration:
```yaml
artifacts:
  baseDirectory: .next
  files:
    - '**/*'
```

### API Calls Fail with CORS Error

**Cause**: API Gateway CORS not properly configured  
**Solution**: Update API Gateway CORS settings:
```bash
cd /home/scotton/dev/projects/autocorp/terraform
terraform apply -target=module.lambda_chat
```

### Environment Variables Not Applied

**Cause**: Variables not set in Amplify  
**Solution**: Add via AWS Console:
1. Amplify Console → App Settings → Environment variables
2. Add both `NEXT_PUBLIC_API_ENDPOINT` and `NEXT_PUBLIC_API_KEY`
3. Redeploy the app

---

## Cost Estimation

**AWS Amplify Hosting (Development)**:
- Build time: ~5 min/deploy
- Storage: ~100 MB
- Bandwidth: ~5 GB/month (estimated)

**Estimated Monthly Cost**: $0-15/month
- Free tier: 1,000 build minutes, 15 GB storage, 15 GB bandwidth
- Overages: $0.01/build minute, $0.023/GB storage, $0.15/GB bandwidth

---

## Post-Deployment Configuration

### Enable Custom Domain (Optional)

1. Purchase domain in Route 53
2. Amplify Console → App Settings → Domain management
3. Add custom domain
4. Configure DNS records (automatic)
5. Wait for SSL certificate provisioning (~15 minutes)

### Enable CI/CD (Automatic)

Amplify automatically deploys on every push to `main` branch:
- Commit code changes
- Push to GitHub
- Amplify detects changes and rebuilds
- New version deployed in 3-5 minutes

### Configure Branch Deployments (Multi-Environment)

Create dev/staging/prod environments:

```bash
# Create staging branch
git checkout -b staging
git push origin staging

# In Amplify Console, add branch
# App Settings → General → Add branch → staging
```

Each branch gets its own URL:
- `https://main.XXXXXXXX.amplifyapp.com` (production)
- `https://staging.XXXXXXXX.amplifyapp.com` (staging)

---

## Monitoring

### CloudWatch Logs

Amplify build logs are available in CloudWatch:
```bash
aws logs tail /aws/amplify/autocorp-chatbox-dev/main --follow
```

### Amplify Console Metrics

View in AWS Console:
- Build history
- Traffic analytics
- Error rates
- Response times

---

## Security Considerations

### API Key Management

**Current**: API key in environment variable (development)  
**Recommended for Production**:
1. Migrate to Amazon Cognito User Pools
2. Use JWT tokens for authentication
3. Remove API key from frontend environment

### HTTPS/SSL

Amplify provides automatic HTTPS with AWS-managed certificates:
- Certificate auto-renewed
- TLS 1.2+ enforced
- HSTS enabled

---

## Next Steps

After successful deployment:

1. ✅ **Test end-to-end functionality**
2. ✅ **Update project documentation** with Amplify URL
3. ✅ **Share URL with stakeholders** for review
4. ⏭️ **Optional**: Configure custom domain
5. ⏭️ **Optional**: Add authentication (Cognito)
6. ⏭️ **Optional**: Enable DMS CDC for real-time data replication

---

## References

- **Amplify Documentation**: https://docs.amplify.aws/
- **Next.js on Amplify**: https://docs.amplify.aws/guides/hosting/nextjs
- **API Gateway**: `/home/scotton/dev/projects/autocorp/terraform/modules/lambda-chat/`
- **Frontend Code**: `/home/scotton/dev/projects/autocorp/frontend/autocorp-chatbox/`

---

## Status Summary

✅ **Ready for Deployment**

| Component | Status | Details |
|-----------|--------|---------|
| Frontend Code | ✅ Complete | Next.js app built and tested |
| API Integration | ✅ Complete | Lambda + API Gateway operational |
| GitHub Repository | ✅ Complete | Code committed and pushed |
| Build Configuration | ✅ Complete | amplify.yml configured |
| Environment Variables | ✅ Complete | API endpoint + key defined |
| AWS Infrastructure | ⏸️ Pending | Requires AWS Console setup |

**Next Action**: Complete GitHub OAuth connection in AWS Amplify Console
