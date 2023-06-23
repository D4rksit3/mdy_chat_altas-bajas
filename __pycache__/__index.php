<?php
// Datos de conexión a MongoDB
$mongodbHost = '10.200.52.229';
$mongodbPort = 27017;
$mongodbDatabase = 'rocketchat';

// Verificar si se ha enviado el formulario
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Obtener los datos ingresados por el usuario
    $username = $_POST['username'];
    $password = $_POST['password'];

    // Crear la conexión a MongoDB
    $mongodb = new MongoDB\Driver\Manager("mongodb://$mongodbHost:$mongodbPort");

    // Realizar una consulta para verificar las credenciales
    $query = new MongoDB\Driver\Query(['username' => $username, 'password' => $password]);
    $result = $mongodb->executeQuery("$mongodbDatabase.collection_name", $query);

    // Verificar si se encontraron resultados
    if ($result->valid()) {
        // Las credenciales son válidas, el usuario ha iniciado sesión correctamente
        echo 'Inicio de sesión exitoso.';
    } else {
        // Las credenciales son inválidas, mostrar mensaje de error
        echo 'Usuario o contraseña incorrectos.';
    }
}
?>

<!DOCTYPE html>
<html>
<head>
    <title>Iniciar sesión</title>
</head>
<body>
    <h2>Iniciar sesión</h2>
    <form method="POST" action="">
        <label for="username">Usuario:</label>
        <input type="text" id="username" name="username" required><br>

        <label for="password">Contraseña:</label>
        <input type="password" id="password" name="password" required><br>

        <input type="submit" value="Iniciar sesión">
    </form>
</body>
</html>
