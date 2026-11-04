param(
    [Parameter(Mandatory=$true)][string]$RequestDirectory,
    [Parameter(Mandatory=$true)][string]$ExecutablePath
)
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath($RequestDirectory).TrimEnd('\')
$utf8 = New-Object System.Text.UTF8Encoding($false)
$resultPath = Join-Path $root 'reference_result.json'
if (Test-Path $resultPath) { throw 'Result already exists; use a new request directory' }
$watch = [Diagnostics.Stopwatch]::StartNew()
$owned = $null
$request = $null
$completion = 'failed'
$nativeExit = $null
$started = $null
$files = @()
$result = $null
function Local-Path([string]$relative) {
    if ([IO.Path]::IsPathRooted($relative)) { throw 'Expected a relative input path' }
    $full = [IO.Path]::GetFullPath((Join-Path $root $relative))
    if (-not $full.StartsWith($root+'\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Path escapes request root' }
    return $full
}
function Hash-File([string]$path) { return (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() }
try {
    $requestPath = Join-Path $root 'request.json'
    $requestHash = Hash-File $requestPath
    $request = [IO.File]::ReadAllText($requestPath, $utf8) | ConvertFrom-Json
    if ($request.schema_version -ne 1) { throw 'Unsupported request version' }
    if ($request.analysis_kind -notin @('dc','ac','transient')) { throw 'Invalid analysis' }
    $exe = Get-Item -LiteralPath $ExecutablePath
    if ($exe.VersionInfo.ProductVersion -ne '26.1.1.0') { throw 'LTspice 26.1.1 required' }
    $exeHash = Hash-File $ExecutablePath
    foreach ($entry in $request.inputs) {
        $path = Local-Path $entry.path
        if ((Get-Item -LiteralPath $path).Length -ne $entry.size_bytes) { throw 'Input size mismatch' }
        if ((Hash-File $path) -ne $entry.sha256) { throw 'Input hash mismatch' }
    }
    foreach ($required in @('deck.cir','models.lib','case.json','component_map.json','device_spec.md','run_reference.ps1')) {
        if ($required -notin @($request.inputs | ForEach-Object { $_.path })) { throw ('Missing input '+$required) }
    }
    foreach ($name in @('deck.raw','deck.log','producer.stdout.txt','producer.stderr.txt')) {
        if (Test-Path (Join-Path $root $name)) { throw 'Stale producer output' }
    }
    $owned = Start-Process -FilePath $ExecutablePath -WorkingDirectory $root -ArgumentList @('-b','deck.cir') -PassThru `
        -RedirectStandardOutput (Join-Path $root 'producer.stdout.txt') -RedirectStandardError (Join-Path $root 'producer.stderr.txt')
    $null = $owned.Handle
    $started = $owned.StartTime.ToUniversalTime().ToString('o')
    if (-not $owned.WaitForExit(1800000)) {
        # Never terminate by image name. Verify identity before killing this tree.
        $current = Get-Process -Id $owned.Id -ErrorAction SilentlyContinue
        if ($current -and $current.StartTime.ToUniversalTime().ToString('o') -eq $started) {
            & taskkill.exe /PID $owned.Id /T /F | Out-Null
            $owned.WaitForExit()
        }
        $completion = 'timed_out'
        throw 'Native producer timeout'
    }
    $owned.WaitForExit()
    $owned.Refresh()
    $nativeExit = $owned.ExitCode
    if ($nativeExit -ne 0) { throw 'Native producer failed' }
    foreach ($expected in $request.expected_outputs) {
        $path = Local-Path $expected
        # Exclusive open checks that native writers have released the file.
        $stream = [IO.File]::Open($path, 'Open', 'Read', 'None')
        $stream.Close()
        $info = Get-Item -LiteralPath $path
        if ($info.Length -eq 0) { throw 'Empty native output' }
        $files += @{path=$expected;size_bytes=$info.Length;sha256=(Hash-File $path)}
    }
    if ((Hash-File $requestPath) -ne $requestHash) { throw 'Request changed during execution' }
    $completion = 'completed'
} catch {
    $message = $_.Exception.Message
} finally {
    $watch.Stop()
    $result = @{
        schema_version=1; request_id=$request.request_id; request_sha256=$requestHash;
        physical_case_sha256=$request.physical_case_sha256;
        producer=@{execution_profile='wsl2-windows-native-v1';executable_path=$ExecutablePath;
            executable_sha256=$exeHash;version=$exe.VersionInfo.ProductVersion;
            windows_version=[Environment]::OSVersion.VersionString;powershell_version=$PSVersionTable.PSVersion.ToString()};
        invocation=@{pid=$(if($owned){$owned.Id}else{$null});start_utc=$started;working_directory=$root;
            argv=@('-b','deck.cir');elapsed_s=$watch.Elapsed.TotalSeconds;exit_code=$nativeExit};
        completion=$completion; files=$files; reason=$message
    }
    $temp = $resultPath+'.tmp'
    [IO.File]::WriteAllText($temp, ($result | ConvertTo-Json -Depth 20), $utf8)
    [IO.File]::Move($temp, $resultPath)
}
if ($completion -ne 'completed') { exit 30 }
