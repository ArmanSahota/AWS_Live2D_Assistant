param(
  [string]$Region="us-west-2",
  [string]$Stack="live2d-aws-backend",
  [string]$Profile=""
)

if ($Profile) { $env:AWS_PROFILE = $Profile }
$env:AWS_DEFAULT_REGION = $Region

aws sts get-caller-identity | Out-Host

$WS_URL = (aws cloudformation describe-stacks --stack-name $Stack --query "Stacks[0].Outputs[?OutputKey=='WSUrl'].OutputValue" --output text)
$HTTP_BASE = (aws cloudformation describe-stacks --stack-name $Stack --query "Stacks[0].Outputs[?OutputKey=='HttpBase'].OutputValue" --output text)

"WS_URL=$WS_URL`nHTTP_BASE=$HTTP_BASE"
Invoke-WebRequest "$HTTP_BASE/health" | Select-Object -ExpandProperty Content
