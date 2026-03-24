# test_developer_api.ps1
# EcoFlow Developer API Credential Test v4
#
# Run: PowerShell -ExecutionPolicy Bypass -File test_developer_api.ps1
#
# v4 fix: EcoFlow signing spec has TWO modes:
#   GET:  sign = HMAC(accessKey=...&nonce=...&timestamp=..., secretKey)
#   PUT:  sign = HMAC(flat_body_params_sorted & accessKey=...&nonce=...&timestamp=..., secretKey)
#         where nested params are flattened with dot notation (params.enabled=0)

# -- Fill in your credentials ---------------------------------------------
$ACCESS_KEY = ""     # From https://developer-eu.ecoflow.com/us/security
$SECRET_KEY = ""     # From https://developer-eu.ecoflow.com/us/security
$DEVICE_SN  = ""     # Your device serial number (e.g. D361ZEH49GAR0848)

# API host - EU by default. Change to https://api.ecoflow.com for US.
$API_HOST = "https://api-e.ecoflow.com"
# -- End credentials -------------------------------------------------------

function Flatten-Params {
    # Recursively flatten nested hashtable/object with dot notation
    # @{sn="X"; params=@{enabled=0}} -> @{sn="X"; params.enabled="0"}
    param([hashtable]$Obj, [string]$Prefix = "")

    $result = @{}
    foreach ($key in $Obj.Keys) {
        $fullKey = if ($Prefix) { "$Prefix.$key" } else { $key }
        $val = $Obj[$key]
        if ($val -is [hashtable]) {
            $sub = Flatten-Params -Obj $val -Prefix $fullKey
            foreach ($sk in $sub.Keys) { $result[$sk] = $sub[$sk] }
        } else {
            $result[$fullKey] = "$val"
        }
    }
    return $result
}

function Get-EcoFlowHeaders {
    param(
        [string]$AccessKey,
        [string]$SecretKey,
        [hashtable]$BodyParams = $null
    )

    $nonce = "$(Get-Random -Minimum 100000 -Maximum 999999)"
    $timestamp = "$([long]([DateTimeOffset]::UtcNow.ToUnixTimeMilliseconds()))"

    # EcoFlow signing spec:
    #   GET:  sign only accessKey + nonce + timestamp
    #   PUT:  flatten body params with dot notation, sort by ASCII,
    #         then append accessKey + nonce + timestamp at the end
    $authPart = "accessKey=$AccessKey&nonce=$nonce&timestamp=$timestamp"

    if ($BodyParams -and $BodyParams.Count -gt 0) {
        # PUT: flatten nested params, sort, then append auth
        $flat = Flatten-Params -Obj $BodyParams
        $sortedParams = ($flat.GetEnumerator() | Sort-Object Name |
            ForEach-Object { "$($_.Name)=$($_.Value)" }) -join "&"
        $signInput = "$sortedParams&$authPart"
    } else {
        # GET: only auth fields
        $signInput = $authPart
    }

    $hmacsha = New-Object System.Security.Cryptography.HMACSHA256
    $hmacsha.Key = [System.Text.Encoding]::UTF8.GetBytes($SecretKey)
    $hash = $hmacsha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($signInput))
    $sign = -join ($hash | ForEach-Object { $_.ToString("x2") })

    return @{
        "Content-Type" = "application/json"
        "accessKey"    = $AccessKey
        "nonce"        = $nonce
        "timestamp"    = $timestamp
        "sign"         = $sign
        "_signInput"   = $signInput
    }
}

# -- Test 1: Device List ---------------------------------------------------
function Test-DeviceList {
    Write-Host ""
    Write-Host ("=" * 60)
    Write-Host "TEST 1: GET /device/list"
    Write-Host ("=" * 60)

    $url = "$API_HOST/iot-open/sign/device/list"
    $headers = Get-EcoFlowHeaders -AccessKey $ACCESS_KEY -SecretKey $SECRET_KEY
    $dbg = $headers["_signInput"]; $headers.Remove("_signInput")

    try {
        $resp = Invoke-RestMethod -Uri $url -Headers $headers -Method GET -TimeoutSec 15
        Write-Host "  Code:    $($resp.code)"
        Write-Host "  Message: $($resp.message)"

        if ("$($resp.code)" -eq "0") {
            $devices = $resp.data
            if ($devices -is [array]) {
                Write-Host "  SUCCESS: $($devices.Count) device(s) found"
                foreach ($d in $devices) {
                    Write-Host "           - $($d.sn) ($($d.productName)) online=$($d.online)"
                }
            }
            return $true
        } else {
            Write-Host "  FAILED:  $($resp.message)"
            return $false
        }
    } catch {
        Write-Host "  ERROR:   $_"
        return $false
    }
}

# -- Test 2: MQTT Credentials ---------------------------------------------
function Test-MqttCredentials {
    Write-Host ""
    Write-Host ("=" * 60)
    Write-Host "TEST 2: GET /certification (MQTT credentials)"
    Write-Host ("=" * 60)

    $url = "$API_HOST/iot-open/sign/certification"
    $headers = Get-EcoFlowHeaders -AccessKey $ACCESS_KEY -SecretKey $SECRET_KEY
    $headers.Remove("_signInput")

    try {
        $resp = Invoke-RestMethod -Uri $url -Headers $headers -Method GET -TimeoutSec 15
        Write-Host "  Code:    $($resp.code)"
        Write-Host "  Message: $($resp.message)"

        if ("$($resp.code)" -eq "0") {
            $data = $resp.data
            Write-Host "  SUCCESS: MQTT credentials received"
            Write-Host "           host=$($data.url) port=$($data.port)"
            return $true
        } else {
            Write-Host "  FAILED:  $($resp.message)"
            return $false
        }
    } catch {
        Write-Host "  ERROR:   $_"
        return $false
    }
}

# -- Test 3: Quota GET -----------------------------------------------------
function Test-QuotaGet {
    if (-not $DEVICE_SN) { return $null }

    Write-Host ""
    Write-Host ("=" * 60)
    Write-Host "TEST 3: GET /device/quota/all (SN=$DEVICE_SN)"
    Write-Host ("=" * 60)

    # GET: sn as URL query param, NOT in signature
    $url = "$API_HOST/iot-open/sign/device/quota/all?sn=$DEVICE_SN"
    $headers = Get-EcoFlowHeaders -AccessKey $ACCESS_KEY -SecretKey $SECRET_KEY
    $headers.Remove("_signInput")

    try {
        $resp = Invoke-RestMethod -Uri $url -Headers $headers -Method GET -TimeoutSec 15
        $code = "$($resp.code)"
        Write-Host "  Code:    $code"
        Write-Host "  Message: $($resp.message)"

        if ($code -eq "0") {
            Write-Host "  SUCCESS: quota data received"
            return $true
        } elseif ($code -match "1006") {
            Write-Host "  NOTE:    1006 - expected for Delta 3 (use App Login for telemetry)"
            return $null
        } else {
            Write-Host "  RESULT:  $($resp.message)"
            return $null
        }
    } catch {
        Write-Host "  ERROR:   $_"
        return $false
    }
}

# -- Test 4: Quota SET (beep ON - safe) ------------------------------------
function Test-QuotaSet {
    if (-not $DEVICE_SN) { return $null }

    Write-Host ""
    Write-Host ("=" * 60)
    Write-Host "TEST 4: PUT /device/quota - SET test (SN=$DEVICE_SN)"
    Write-Host ("=" * 60)

    $url = "$API_HOST/iot-open/sign/device/quota"

    # Body params - these get flattened and signed for PUT
    $setBody = @{
        sn          = $DEVICE_SN
        moduleType  = 5
        operateType = "quietMode"
        params      = @{ enabled = 0 }
    }

    $headers = Get-EcoFlowHeaders -AccessKey $ACCESS_KEY -SecretKey $SECRET_KEY `
        -BodyParams $setBody
    $dbg = $headers["_signInput"]; $headers.Remove("_signInput")

    $jsonBody = $setBody | ConvertTo-Json -Compress
    $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($jsonBody)

    Write-Host "  URL:     $url"
    Write-Host "  Body:    $jsonBody"
    Write-Host "  Sign:    $dbg"
    Write-Host "  NOTE:    beep=ON command (safe, non-destructive)"

    try {
        $resp = Invoke-RestMethod -Uri $url -Headers $headers -Method PUT `
            -Body $bodyBytes -ContentType "application/json; charset=utf-8" -TimeoutSec 15
        $code = "$($resp.code)"
        Write-Host "  Code:    $code"
        Write-Host "  Message: $($resp.message)"

        if ($code -eq "0") {
            Write-Host "  SUCCESS: REST SET accepted! Hybrid mode confirmed."
            return $true
        } elseif ($code -match "1006") {
            Write-Host "  NOTE:    1006 - device offline. Re-test when powered on."
            return $null
        } elseif ($code -match "8521") {
            Write-Host "  FAILED:  Signature wrong - signing bug remains."
            return $false
        } else {
            Write-Host "  RESULT:  code=$code (not 8521 = signing is correct)"
            return $null
        }
    } catch {
        Write-Host "  ERROR:   $_"
        return $false
    }
}

# -- Main ------------------------------------------------------------------
Write-Host "EcoFlow Developer API Credential Test v4"
Write-Host "Host:       $API_HOST"
if ($ACCESS_KEY) { Write-Host "Access Key: $($ACCESS_KEY.Substring(0,8))..." }
else             { Write-Host "Access Key: NOT SET" }
if ($SECRET_KEY) { Write-Host "Secret Key: ********..." }
else             { Write-Host "Secret Key: NOT SET" }
if ($DEVICE_SN)  { Write-Host "Device SN:  $DEVICE_SN" }
else             { Write-Host "Device SN:  NOT SET" }

if (-not $ACCESS_KEY -or -not $SECRET_KEY) {
    Write-Host "`nERROR: Fill in ACCESS_KEY and SECRET_KEY before running."
    exit 1
}

$r1 = Test-DeviceList
$r2 = Test-MqttCredentials
$r3 = Test-QuotaGet
$r4 = Test-QuotaSet

Write-Host ""
Write-Host ("=" * 60)
Write-Host "SUMMARY"
Write-Host ("=" * 60)

function Format-Result($val) {
    if ($val -eq $true) { "PASS" }
    elseif ($null -eq $val) { "SKIP/NOTE" }
    else { "FAIL" }
}

Write-Host ("  device_list:       " + (Format-Result $r1))
Write-Host ("  mqtt_credentials:  " + (Format-Result $r2))
Write-Host ("  quota_get:         " + (Format-Result $r3))
Write-Host ("  quota_set:         " + (Format-Result $r4))

Write-Host ""
$sigOk = ($r1 -eq $true) -or ($r2 -eq $true)
if ($sigOk -and ($r4 -eq $true)) {
    Write-Host "  CONCLUSION: Developer API fully functional. Hybrid mode confirmed."
} elseif ($sigOk -and ($null -eq $r4)) {
    Write-Host "  CONCLUSION: Signing works. Device offline - re-test when powered on."
} elseif ($sigOk -and ($r4 -eq $false)) {
    Write-Host "  CONCLUSION: GET signing works but PUT signing fails."
    Write-Host "              Check Sign: line above for the signing input string."
} else {
    Write-Host "  CONCLUSION: Credentials problem. Check Access Key and Secret Key."
}

Write-Host ""
Write-Host "Press Enter to close..."
Read-Host
