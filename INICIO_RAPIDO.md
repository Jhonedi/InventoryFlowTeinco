# 🚀 Guía de Inicio Rápido

## Pasos para ejecutar la aplicación

### 1️⃣ Configurar la Base de Datos

**Opción A - Usando MySQL desde línea de comandos:**
```bash
mysql -u root -p
```
Luego ejecutar:
```sql
source C:\Users\Jhon Edison Trujillo\taller_inventario\database\schema.sql
```

**Opción B - Usando phpMyAdmin:**
1. Abrir http://localhost/phpmyadmin en tu navegador
2. Crear nueva base de datos: `taller_inventario`
3. Ir a la pestaña "Importar"
4. Seleccionar el archivo: `C:\Users\Jhon Edison Trujillo\taller_inventario\database\schema.sql`
5. Hacer clic en "Continuar"

### 2️⃣ Configurar Credenciales de MySQL (si es necesario)

Si tu usuario de MySQL no es `root` o tiene contraseña, editar el archivo `config.py`:

```python
MYSQL_USER = 'tu_usuario'
MYSQL_PASSWORD = 'tu_contraseña'
```

### 3️⃣ Iniciar la Aplicación

**Método Simple - Usar el script de inicio:**
```bash
# Hacer doble clic en inicio.bat
# O ejecutar desde la terminal:
inicio.bat
```

**Método Manual:**
```bash
# 1. Crear entorno virtual
python -m venv venv

# 2. Activar entorno virtual
venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar aplicación
python app.py
```

### 4️⃣ Acceder a la Aplicación

Abrir el navegador y visitar:
```
http://localhost:5000
```

### 5️⃣ Iniciar Sesión

**Credenciales por defecto:**
- Usuario: `admin`
- Contraseña: `admin123`

## ⚡ Primeros Pasos en el Sistema

### Como Administrador:

1. **Crear Usuarios**
   - Ir a Usuarios → Nuevo Usuario
   - Crear al menos un Almacenista, un Vendedor y un Técnico

2. **Agregar Repuestos**
   - Ir a Repuestos → Nuevo Repuesto
   - Llenar información del repuesto
   - Establecer cantidad mínima para alertas

3. **Registrar Entrada de Inventario**
   - Ir a Movimientos → Entrada de Inventario
   - Seleccionar repuesto y cantidad
   - Tipo: "Compra"

4. **Registrar Cliente**
   - En el módulo de clientes (si ya está implementado)
   - O usar la base de datos directamente

### Como Almacenista:

1. **Controlar Entradas y Salidas**
   - Registrar cuando llegan repuestos
   - Procesar solicitudes de técnicos

2. **Revisar Alertas**
   - Ir a Alertas
   - Ver repuestos con stock bajo o agotados

### Como Vendedor:

1. **Confirmar Ventas**
   - Ver salidas pendientes
   - Confirmar cuando el cliente pague
   - Generar factura

### Como Técnico:

1. **Consultar Disponibilidad**
   - Ver lista de repuestos
   - Verificar stock disponible
   - Solicitar al almacenista

## 🔧 Solución de Problemas Comunes

### Error: "Can't connect to MySQL server"
**Solución:**
- Verificar que MySQL esté corriendo
- En Windows: abrir Servicios y buscar "MySQL"
- Verificar credenciales en `config.py`

### Error: "ModuleNotFoundError"
**Solución:**
```bash
# Activar el entorno virtual primero
venv\Scripts\activate
# Luego instalar dependencias
pip install -r requirements.txt
```

### La página no carga
**Solución:**
- Verificar que el servidor Flask esté corriendo
- Revisar que el puerto 5000 no esté ocupado
- Ver los mensajes de error en la consola

### No puedo iniciar sesión
**Solución:**
- Verificar que la base de datos esté creada e importada
- Usar las credenciales por defecto: admin / admin123
- Revisar que la tabla `usuarios` tenga datos

## 📞 Soporte

Si tienes problemas, verifica:
1. ✅ MySQL está corriendo
2. ✅ Base de datos `taller_inventario` existe
3. ✅ Entorno virtual está activado
4. ✅ Todas las dependencias están instaladas
5. ✅ No hay errores en la consola de Python

## 🎯 Funciones Clave

| Rol | Puede hacer |
|-----|-------------|
| **Administrador** | Todo: gestionar usuarios, repuestos, ver reportes |
| **Almacenista** | Gestionar inventario, entradas/salidas, ver alertas |
| **Vendedor** | Confirmar ventas, generar facturas |
| **Técnico** | Solo consultar información (lectura) |

## 📋 Checklist de Configuración Inicial

- [ ] MySQL instalado y corriendo
- [ ] Base de datos `taller_inventario` creada
- [ ] Schema SQL importado
- [ ] Python 3.8+ instalado
- [ ] Dependencias instaladas (`requirements.txt`)
- [ ] Aplicación iniciada sin errores
- [ ] Login funciona con admin/admin123
- [ ] Dashboard carga correctamente

¡Listo para usar! 🎉
