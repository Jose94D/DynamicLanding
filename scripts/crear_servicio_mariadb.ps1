# Crea la MariaDB de desarrollo como servicio de Windows (puerto 3307), con el usuario y las bases
# del proyecto, e importa el respaldo mas reciente de respaldos\*.sql.
# Ejecutar UNA vez, en PowerShell COMO ADMINISTRADOR, desde la raiz del proyecto:
#   powershell -ExecutionPolicy Bypass -File scripts\crear_servicio_mariadb.ps1
$ErrorActionPreference = 'Stop'
$bin = 'C:\Program Files\MariaDB 13.0\bin'
$datos = 'C:\ProgramData\DynamicLanding\mariadb'
$servicio = 'DynamicLandingDB'
$raiz = Split-Path $PSScriptRoot

$yo = [Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
if (-not $yo.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { throw 'Abre PowerShell como administrador.' }
if (Test-Path $datos) { throw "Ya existe $datos. Si quieres crearla de nuevo, deten y borra el servicio y esa carpeta." }

# Usuario, clave y base de la app: salen de backend\.env, asi no se escriben a mano.
$linea = Get-Content "$raiz\backend\.env" | Where-Object { $_ -like 'DATABASE_URL=*' }
if ($linea -notmatch '://([^:]+):([^@]+)@[^/]+/([^?]+)') { throw 'No encontre DATABASE_URL en backend\.env' }
$usuario, $clave, $base = $Matches[1], $Matches[2], $Matches[3]

# Servicio anterior (si quedo uno a medias)
if (Get-Service $servicio -ErrorAction SilentlyContinue) {
    Stop-Service $servicio -ErrorAction SilentlyContinue
    sc.exe delete $servicio | Out-Null
    Start-Sleep 2
}

# Clave de root aleatoria. Se guarda en un archivo que solo pueden leer administradores y SYSTEM.
$bytes = New-Object byte[] 18
[Security.Cryptography.RandomNumberGenerator]::Create().GetBytes($bytes)
$root = [Convert]::ToBase64String($bytes) -replace '[+/=]', 'x'

Write-Host '1/4 Creando la base de datos y el servicio...'
New-Item -ItemType Directory -Force (Split-Path $datos) | Out-Null  # mariadb-install-db no crea la carpeta padre
& "$bin\mariadb-install-db.exe" "--datadir=$datos" --port=3307 "--service=$servicio" "--password=$root"
if ($LASTEXITCODE) { throw 'mariadb-install-db fallo (ver mensajes arriba).' }
$archivoRoot = 'C:\ProgramData\DynamicLanding\root.txt'
Set-Content $archivoRoot $root -Encoding ascii
icacls $archivoRoot /inheritance:r /grant:r '*S-1-5-32-544:F' '*S-1-5-18:F' | Out-Null

Write-Host '2/4 Iniciando el servicio...'
Start-Service $servicio

Write-Host '3/4 Creando usuario y bases...'
$sql = "CREATE DATABASE IF NOT EXISTS $base CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; " +
       "CREATE DATABASE IF NOT EXISTS ${base}_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci; " +
       "CREATE USER IF NOT EXISTS '$usuario'@'localhost' IDENTIFIED BY '$clave'; " +
       "GRANT ALL PRIVILEGES ON $base.* TO '$usuario'@'localhost'; " +
       "GRANT ALL PRIVILEGES ON ${base}_test.* TO '$usuario'@'localhost'; FLUSH PRIVILEGES;"
& "$bin\mariadb.exe" -u root "-p$root" -P 3307 -h 127.0.0.1 -e $sql
if ($LASTEXITCODE) { throw 'No se pudo crear el usuario o las bases.' }

Write-Host '4/4 Importando datos...'
$respaldo = Get-ChildItem "$raiz\respaldos\*.sql" -ErrorAction SilentlyContinue | Sort-Object LastWriteTime | Select-Object -Last 1
if ($respaldo) {
    # 'source' en vez de una tuberia: PowerShell 5.1 estropea los acentos al pasar texto por tuberia.
    & "$bin\mariadb.exe" -u root "-p$root" -P 3307 -h 127.0.0.1 -e "source $($respaldo.FullName -replace '\\', '/')"
    if ($LASTEXITCODE) { throw "No se pudo importar $($respaldo.Name)." }
    Write-Host "   Importado: $($respaldo.Name)"
} else {
    Write-Host '   Sin respaldo: crea las tablas con "alembic upgrade head" y "python -m app.seed" en backend\.'
}

& "$bin\mariadb.exe" -u $usuario "-p$clave" -P 3307 -h 127.0.0.1 $base -e 'SELECT COUNT(*) AS modulos FROM modulos'
Write-Host ''
Write-Host "Listo. Servicio ${servicio}: $((Get-Service $servicio).Status), inicio $((Get-Service $servicio).StartType)." -ForegroundColor Green
Write-Host "La clave de root quedo en $archivoRoot (solo administradores)."
