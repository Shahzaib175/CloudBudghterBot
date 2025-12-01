#!/bin/bash
set -e

echo "🚀 Starting Lambda build process..."

# Remove old build folders and zip
echo "🧹 Cleaning old build files..."
rm -rf build
rm -rf lambda_package
rm -f cloudbudgter.zip

# Create a fresh directory
mkdir -p lambda_package

echo "📦 Installing Python dependencies into lambda_package..."
pip install -r requirements.txt -t lambda_package/

echo "📁 Copying Python source files..."
cp *.py lambda_package/

echo "🗜️ Creating Lambda ZIP: cloudbudgter.zip"
cd lambda_package
zip -r ../cloudbudgter.zip .
cd ..

echo "✅ Build complete! Generated: cloudbudgter.zip"
