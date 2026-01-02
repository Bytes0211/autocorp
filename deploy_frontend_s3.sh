#!/bin/bash

# AutoCorp Frontend Deployment to S3 + CloudFront
# Date: January 1, 2026

set -e

BUCKET_NAME="autocorp-frontend-dev"
REGION="us-east-1"
FRONTEND_DIR="/home/scotton/dev/projects/autocorp/frontend/autocorp-chatbox"

echo "🚀 Deploying AutoCorp AI Chatbox to S3..."

# Step 1: Create S3 bucket if it doesn't exist
echo "📦 Creating S3 bucket: $BUCKET_NAME"
if aws s3 ls "s3://$BUCKET_NAME" 2>&1 | grep -q 'NoSuchBucket'; then
    aws s3 mb "s3://$BUCKET_NAME" --region "$REGION"
    echo "✅ Bucket created"
else
    echo "✅ Bucket already exists"
fi

# Step 2: Configure bucket for static website hosting
echo "🌐 Configuring static website hosting..."
aws s3 website "s3://$BUCKET_NAME" \
    --index-document index.html \
    --error-document 404.html

# Step 3: Set bucket policy for public read access
echo "🔓 Setting bucket policy..."
cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
    --bucket "$BUCKET_NAME" \
    --policy file:///tmp/bucket-policy.json

# Step 4: Build the Next.js app with static export
echo "🔨 Building Next.js app..."
cd "$FRONTEND_DIR"

# Check if .env.local exists, if not create it
if [ ! -f .env.local ]; then
    echo "📝 Creating .env.local with API configuration..."
    cat > .env.local <<EOF
NEXT_PUBLIC_API_ENDPOINT=https://1fml3yigqh.execute-api.us-east-1.amazonaws.com/dev
NEXT_PUBLIC_API_KEY=nWU3TtU4G88fmNm0VDLyBONFlvx6gwE6WZGRTEY7
EOF
fi

# Run build
npm run build

# Step 5: Sync files to S3
echo "📤 Uploading files to S3..."
aws s3 sync .next/static "s3://$BUCKET_NAME/_next/static" \
    --delete \
    --cache-control "public, max-age=31536000, immutable"

aws s3 sync public "s3://$BUCKET_NAME" \
    --delete \
    --cache-control "public, max-age=3600"

# Upload HTML files
aws s3 cp .next/server/app/index.html "s3://$BUCKET_NAME/index.html" \
    --content-type "text/html" \
    --cache-control "public, max-age=0, must-revalidate"

# Step 6: Get the website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Website URL: $WEBSITE_URL"
echo ""
echo "📝 Next steps:"
echo "   1. Test the deployment: $WEBSITE_URL"
echo "   2. (Optional) Set up CloudFront distribution for HTTPS and CDN"
echo "   3. (Optional) Configure custom domain in Route 53"
echo ""
