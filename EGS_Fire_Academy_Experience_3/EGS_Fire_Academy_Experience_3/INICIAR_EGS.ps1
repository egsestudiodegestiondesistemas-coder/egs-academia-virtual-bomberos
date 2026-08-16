Write-Host "EGS Experience 3.0 -> http://localhost:8080" -ForegroundColor Cyan
Start-Process "http://localhost:8080"
py -m http.server 8080
