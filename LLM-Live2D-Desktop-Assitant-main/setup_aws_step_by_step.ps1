# AWS Knowledge Base Setup - PowerShell Script
# Enhanced setup script for Windows PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AWS Knowledge Base Setup - Step by Step" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Step 1: Checking Prerequisites..." -ForegroundColor Yellow
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python..." -NoNewline
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅ Python is installed ($pythonVersion)" -ForegroundColor Green
    } else {
        throw "Python not found"
    }
} catch {
    Write-Host " ❌ Python is not installed" -ForegroundColor Red
    Write-Host "Please install Python 3.11+ from https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if AWS CLI is installed
Write-Host "Checking AWS CLI..." -NoNewline
try {
    $awsVersion = aws --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅ AWS CLI is installed" -ForegroundColor Green
    } else {
        throw "AWS CLI not found"
    }
} catch {
    Write-Host " ❌ AWS CLI is not installed" -ForegroundColor Red
    Write-Host "Installing AWS CLI..." -ForegroundColor Yellow
    try {
        winget install Amazon.AWSCLI
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ AWS CLI installed successfully" -ForegroundColor Green
        } else {
            throw "Installation failed"
        }
    } catch {
        Write-Host "Failed to install AWS CLI automatically" -ForegroundColor Red
        Write-Host "Please install manually from: https://aws.amazon.com/cli/" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Check if SAM CLI is installed
Write-Host "Checking SAM CLI..." -NoNewline
try {
    $samVersion = sam --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅ SAM CLI is installed" -ForegroundColor Green
    } else {
        throw "SAM CLI not found"
    }
} catch {
    Write-Host " ❌ SAM CLI is not installed" -ForegroundColor Red
    Write-Host "Installing SAM CLI..." -ForegroundColor Yellow
    try {
        pip install aws-sam-cli
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ SAM CLI installed successfully" -ForegroundColor Green
        } else {
            throw "Installation failed"
        }
    } catch {
        Write-Host "Failed to install SAM CLI" -ForegroundColor Red
        Write-Host "Please install manually: pip install aws-sam-cli" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "Step 2: Installing Python Dependencies..." -ForegroundColor Yellow
Write-Host "Installing boto3, pyyaml, aiohttp..."
try {
    pip install boto3 pyyaml aiohttp
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python dependencies installed" -ForegroundColor Green
    } else {
        throw "Installation failed"
    }
} catch {
    Write-Host "❌ Failed to install Python dependencies" -ForegroundColor Red
    Write-Host "Please check your internet connection and try again" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 3: AWS Configuration Check..." -ForegroundColor Yellow
Write-Host "Testing AWS credentials..."
try {
    $identity = aws sts get-caller-identity 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ AWS credentials are configured" -ForegroundColor Green
        Write-Host "Current AWS identity:" -ForegroundColor Cyan
        Write-Host $identity -ForegroundColor Gray
    } else {
        throw "AWS credentials not configured"
    }
} catch {
    Write-Host "❌ AWS credentials not configured" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please configure AWS credentials:" -ForegroundColor Yellow
    Write-Host "1. Run: aws configure" -ForegroundColor White
    Write-Host "2. Enter your AWS Access Key ID" -ForegroundColor White
    Write-Host "3. Enter your AWS Secret Access Key" -ForegroundColor White
    Write-Host "4. Enter region: us-west-2" -ForegroundColor White
    Write-Host "5. Enter output format: json" -ForegroundColor White
    Write-Host ""
    
    $configure = Read-Host "Would you like to run 'aws configure' now? (y/n)"
    if ($configure -eq "y" -or $configure -eq "Y") {
        Write-Host "Running AWS configure..." -ForegroundColor Yellow
        aws configure
        Write-Host ""
        Write-Host "Testing AWS connection..." -ForegroundColor Yellow
        try {
            $identity = aws sts get-caller-identity 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ AWS configuration successful" -ForegroundColor Green
                Write-Host $identity -ForegroundColor Gray
            } else {
                throw "Configuration test failed"
            }
        } catch {
            Write-Host "❌ AWS configuration failed" -ForegroundColor Red
            Read-Host "Press Enter to exit"
            exit 1
        }
    } else {
        Write-Host "Please configure AWS credentials manually and run this script again" -ForegroundColor Yellow
        Read-Host "Press Enter to exit"
        exit 1
    }
}

Write-Host ""
Write-Host "Step 4: Deployment Options" -ForegroundColor Yellow
Write-Host ""
Write-Host "Choose deployment method:" -ForegroundColor Cyan
Write-Host "1. Automated deployment (Recommended)" -ForegroundColor White
Write-Host "2. Manual step-by-step deployment" -ForegroundColor White
Write-Host "3. Skip deployment (just test current setup)" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter your choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Running automated deployment..." -ForegroundColor Yellow
        try {
            python deploy_aws_rag.py --region us-west-2 --stack-name live2d-aws-backend
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Automated deployment completed" -ForegroundColor Green
            } else {
                throw "Deployment failed"
            }
        } catch {
            Write-Host "❌ Automated deployment failed" -ForegroundColor Red
            Write-Host "Check the error messages above" -ForegroundColor Red
            Read-Host "Press Enter to continue with testing"
        }
    }
    "2" {
        Write-Host ""
        Write-Host "Manual deployment selected..." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Step 4a: Deploy infrastructure only" -ForegroundColor Cyan
        try {
            python deploy_aws_rag.py --skip-kb --skip-docs --region us-west-2
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Infrastructure deployed" -ForegroundColor Green
            } else {
                throw "Infrastructure deployment failed"
            }
        } catch {
            Write-Host "❌ Infrastructure deployment failed" -ForegroundColor Red
            Read-Host "Press Enter to continue"
        }
        Write-Host ""
        Write-Host "Step 4b: Manual Knowledge Base Setup Required" -ForegroundColor Cyan
        Write-Host "Please follow the manual setup instructions in AWS_SETUP_QUICKSTART.md" -ForegroundColor Yellow
        Write-Host "After creating the Knowledge Base manually, run:" -ForegroundColor Yellow
        Write-Host "python deploy_aws_rag.py --skip-deploy --skip-kb --region us-west-2" -ForegroundColor White
        Read-Host "Press Enter to continue"
    }
    "3" {
        Write-Host "Skipping deployment..." -ForegroundColor Yellow
    }
    default {
        Write-Host "Invalid choice, skipping deployment..." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Step 5: Testing the Setup..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Testing AWS Knowledge Base integration..." -ForegroundColor Cyan
try {
    python test_aws_kb_integration.py --test aws-kb
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ AWS Knowledge Base test passed" -ForegroundColor Green
    } else {
        Write-Host "⚠️ AWS Knowledge Base test failed (this is OK if not set up yet)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ AWS Knowledge Base test failed (this is OK if not set up yet)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Testing hybrid RAG system..." -ForegroundColor Cyan
try {
    python test_aws_kb_integration.py --test hybrid
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Hybrid RAG test passed" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Hybrid RAG test failed" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Hybrid RAG test failed" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 6: Server Setup Check..." -ForegroundColor Yellow
Write-Host ""

Write-Host "Testing enhanced server configuration..." -ForegroundColor Cyan
try {
    python run_enhanced_server.py --help | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Enhanced server script is ready" -ForegroundColor Green
    } else {
        Write-Host "❌ Enhanced server script has issues" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Enhanced server script has issues" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path ".env.aws-rag") {
    Write-Host "✅ AWS configuration file created: .env.aws-rag" -ForegroundColor Green
    Write-Host "To use it, run: Copy-Item .env.aws-rag .env" -ForegroundColor Yellow
} else {
    Write-Host "⚠️ AWS configuration file not found" -ForegroundColor Yellow
    Write-Host "You may need to complete the AWS deployment first" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. If deployment succeeded, copy .env.aws-rag to .env" -ForegroundColor White
Write-Host "2. Run the enhanced server: python run_enhanced_server.py" -ForegroundColor White
Write-Host "3. Test the RAG functionality with manufacturing questions" -ForegroundColor White
Write-Host "4. Upload your own documents to the S3 bucket" -ForegroundColor White
Write-Host ""

Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "- python run_enhanced_server.py          (Start enhanced server)" -ForegroundColor White
Write-Host "- python test_aws_kb_integration.py      (Test RAG integration)" -ForegroundColor White
Write-Host "- python deploy_aws_rag.py               (Deploy/update AWS resources)" -ForegroundColor White
Write-Host ""

Write-Host "For detailed troubleshooting, see:" -ForegroundColor Cyan
Write-Host "- AWS_SETUP_QUICKSTART.md" -ForegroundColor White
Write-Host "- SERVER_TROUBLESHOOTING.md" -ForegroundColor White
Write-Host "- AWS_KNOWLEDGE_BASE_SETUP.md" -ForegroundColor White
Write-Host ""

Write-Host "Setup script completed!" -ForegroundColor Green
Read-Host "Press Enter to exit"