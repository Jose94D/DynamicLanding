# Arranca la MariaDB de desarrollo (puerto 3307), separada de la MariaDB 11.8 del sistema.
# Uso: powershell -File scripts\iniciar_mariadb.ps1
$ini = "$env:LOCALAPPDATA\DynamicLanding\mariadb\my.ini"
$corriendo = Get-CimInstance Win32_Process -Filter "Name='mysqld.exe'" | Where-Object { $_.CommandLine -like "*DynamicLanding*" }
if ($corriendo) {
    Write-Host "MariaDB de desarrollo ya esta corriendo en el puerto 3307."
    exit 0
}
Start-Process -WindowStyle Hidden -FilePath "C:\Program Files\MariaDB 13.0\bin\mysqld.exe" -ArgumentList "--defaults-file=`"$ini`""
Write-Host "MariaDB de desarrollo iniciada en el puerto 3307."
