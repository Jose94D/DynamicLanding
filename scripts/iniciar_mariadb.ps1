# Arranca la MariaDB de desarrollo (puerto 3307), separada de la MariaDB 11.8 del sistema.
# Uso: powershell -File scripts\iniciar_mariadb.ps1   (VS Code lo ejecuta solo antes de F5)
# Termina con error si MariaDB no queda aceptando conexiones, para que el fallo se vea aquí y no como un 500.
$ErrorActionPreference = 'Stop'
$datos = "$env:LOCALAPPDATA\DynamicLanding\mariadb"
$mysqld = 'C:\Program Files\MariaDB 13.0\bin\mysqld.exe'
$puerto = 3307

function Escuchando {
    # Conexión con tope de 300 ms: un Connect normal tarda ~2 s en fallar en Windows.
    $c = New-Object Net.Sockets.TcpClient
    try { $c.ConnectAsync('127.0.0.1', $puerto).Wait(300) -and $c.Connected } catch { $false } finally { $c.Dispose() }
}

if (Escuchando) {
    Write-Host "MariaDB de desarrollo ya esta corriendo en el puerto $puerto."
    exit 0
}

# Si existe como servicio de Windows (ver README), se usa ese; si no, se lanza el proceso.
if (Get-Service DynamicLandingDB -ErrorAction SilentlyContinue) {
    $datos = 'C:\ProgramData\DynamicLanding\mariadb'  # donde la crea crear_servicio_mariadb.ps1 (para leer su log)
    Start-Service DynamicLandingDB
} else {
    # shortcut: proceso suelto; si Windows se apaga con MariaDB corriendo, la cierra de golpe y puede dañar
    # las tablas Aria (pasó una vez). El servicio DynamicLandingDB (ver README) la apaga ordenadamente.
    $proceso = Start-Process -WindowStyle Hidden -PassThru -FilePath $mysqld -ArgumentList "--defaults-file=`"$datos\my.ini`""
}

for ($i = 0; $i -lt 40; $i++) {
    if ($proceso -and $proceso.HasExited) { break }  # se cayó al arrancar: no esperar los 30 s
    Start-Sleep -Milliseconds 500
    if (Escuchando) {
        Write-Host "MariaDB de desarrollo iniciada en el puerto $puerto."
        exit 0
    }
}

Write-Host "ERROR: MariaDB no arranco. Ultimas lineas del log:" -ForegroundColor Red
Get-ChildItem "$datos\*.err" | ForEach-Object { Get-Content $_ -Tail 12 }
exit 1
