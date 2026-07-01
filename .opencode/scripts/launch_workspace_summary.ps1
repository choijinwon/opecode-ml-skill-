$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Target = Join-Path $ScriptDir "01-project-analyze\launch_workspace_summary.py"

python $Target @args
exit $LASTEXITCODE
