# Instrucciones de Actualización del Sistema de Inventario

## Nuevas Funcionalidades Agregadas

### 1. **Gestión Completa de Usuarios**
- ✅ Crear nuevos usuarios
- ✅ Editar usuarios existentes (incluye cambio de contraseña opcional)
- ✅ Activar/desactivar usuarios
- ✅ Registro de quién creó y modificó cada usuario

### 2. **Ajuste Manual de Cantidades de Repuestos**
- ✅ Los administradores y almacenistas pueden ajustar cantidades directamente
- ✅ Historial completo de ajustes con motivo y usuario
- ✅ Visualización de diferencias antes de confirmar

### 3. **Historial de Movimientos Mejorado**
- ✅ Muestra el usuario que registró cada movimiento
- ✅ Registro completo de entradas y salidas
- ✅ Filtros mejorados

### 4. **Validación de Placas Vehiculares**
- ✅ Validación automática de formato
- ✅ Soporte para autos (ABC123) y motos (ABC12D)
- ✅ Búsqueda rápida por placa (preparado para implementación futura)

### 5. **Sistema de Alertas**
- ✅ Visualización completa de alertas de inventario
- ✅ Marcar alertas como leídas
- ✅ Notificaciones automáticas

## Actualización de la Base de Datos

### Opción 1: Base de Datos Nueva (Recomendado)

Si deseas comenzar desde cero con la nueva estructura:

1. **Respaldar datos actuales** (si los tienes):
   ```sql
   mysqldump -u root -p taller_inventario > backup_antes_actualizacion.sql
   ```

2. **Eliminar la base de datos antigua**:
   ```sql
   DROP DATABASE IF EXISTS taller_inventario;
   ```

3. **Importar el nuevo esquema**:
   ```bash
   mysql -u root -p < database/schema_v2.sql
   ```

### Opción 2: Migración de Datos Existentes

Si tienes datos que deseas conservar:

1. **Respaldar la base de datos actual**:
   ```sql
   mysqldump -u root -p taller_inventario > backup_migracion.sql
   ```

2. **Ejecutar el script de migración** (conectarse a MySQL):
   ```sql
   USE taller_inventario;
   
   -- Agregar nuevas columnas a usuarios
   ALTER TABLE usuarios 
   ADD COLUMN created_by INT NULL AFTER updated_at,
   ADD COLUMN updated_by INT NULL AFTER created_by,
   ADD FOREIGN KEY (created_by) REFERENCES usuarios(id) ON DELETE SET NULL,
   ADD FOREIGN KEY (updated_by) REFERENCES usuarios(id) ON DELETE SET NULL;
   
   -- Agregar nuevas columnas a repuestos
   ALTER TABLE repuestos
   ADD COLUMN created_by INT NULL AFTER updated_at,
   ADD COLUMN updated_by INT NULL AFTER created_by,
   ADD FOREIGN KEY (created_by) REFERENCES usuarios(id) ON DELETE SET NULL,
   ADD FOREIGN KEY (updated_by) REFERENCES usuarios(id) ON DELETE SET NULL;
   
   -- Crear tabla de historial de ajustes
   CREATE TABLE IF NOT EXISTS historial_ajustes_inventario (
       id INT PRIMARY KEY AUTO_INCREMENT,
       repuesto_id INT NOT NULL,
       cantidad_anterior INT NOT NULL,
       cantidad_nueva INT NOT NULL,
       diferencia INT NOT NULL,
       usuario_id INT NOT NULL,
       motivo TEXT,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       FOREIGN KEY (repuesto_id) REFERENCES repuestos(id),
       FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
   ) ENGINE=InnoDB;
   
   -- Agregar índices adicionales
   CREATE INDEX IF NOT EXISTS idx_repuestos_nombre ON repuestos(nombre);
   CREATE INDEX IF NOT EXISTS idx_movimientos_usuario ON movimientos_inventario(usuario_id);
   CREATE INDEX IF NOT EXISTS idx_clientes_documento ON clientes(numero_documento);
   CREATE INDEX IF NOT EXISTS idx_usuarios_username ON usuarios(username);
   ```

## Instalación desde Cero

### Requisitos Previos
- Python 3.8 o superior
- MySQL 5.7 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto** (si aún no lo tienes)

2. **Instalar dependencias de Python**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Crear la base de datos**:
   ```bash
   mysql -u root -p < database/schema_v2.sql
   ```
   
   O si prefieres el esquema original:
   ```bash
   mysql -u root -p < database/schema.sql
   ```

4. **Configurar las credenciales** en `config.py`:
   ```python
   MYSQL_HOST = 'localhost'
   MYSQL_USER = 'root'  # Tu usuario de MySQL
   MYSQL_PASSWORD = 'tu_contraseña'  # Tu contraseña de MySQL
   MYSQL_DB = 'taller_inventario'
   MYSQL_PORT = 3306
   ```

5. **Iniciar el servidor**:
   ```bash
   python app.py
   ```
   
   O usar el script de inicio rápido:
   ```bash
   ./inicio.bat  # En Windows
   ```

6. **Acceder al sistema**:
   - URL: http://localhost:5000
   - Usuario: `admin`
   - Contraseña: `admin123`
   
   **⚠️ IMPORTANTE:** Cambia la contraseña del administrador inmediatamente después del primer acceso.

## Credenciales por Defecto

- **Usuario**: admin
- **Contraseña**: admin123
- **Rol**: Administrador

## Nuevas Rutas Disponibles

### Usuarios
- `/usuarios` - Lista de usuarios
- `/usuarios/nuevo` - Crear usuario
- `/usuarios/<id>/editar` - Editar usuario
- `/usuarios/<id>/toggle-estado` - Activar/desactivar usuario

### Repuestos
- `/repuestos/<id>/ajustar-cantidad` - Ajustar cantidad de inventario

### Alertas
- `/alertas` - Ver alertas activas
- `/api/alertas/marcar-leida/<id>` - Marcar alerta como leída

### Movimientos
- `/movimientos` - Ver historial de movimientos
- `/movimientos/entrada` - Registrar entrada
- `/movimientos/salida` - Registrar salida

## Archivos Nuevos Creados

1. `database/schema_v2.sql` - Nueva estructura de base de datos mejorada
2. `templates/usuarios/lista.html` - Lista de usuarios (actualizado)
3. `templates/usuarios/form.html` - Formulario de usuarios (actualizado)
4. `templates/alertas/lista.html` - Lista de alertas
5. `templates/movimientos/lista.html` - Lista de movimientos
6. `templates/movimientos/entrada.html` - Formulario de entrada
7. `templates/movimientos/salida.html` - Formulario de salida
8. `templates/repuestos/ajustar_cantidad.html` - Ajuste de cantidad
9. `static/js/validacion_placas.js` - Validación de placas vehiculares
10. `INSTRUCCIONES_ACTUALIZACION.md` - Este archivo

## Cambios en app.py

Se agregaron las siguientes funciones:
- `editar_usuario(id)` - Editar usuario
- `toggle_estado_usuario(id)` - Activar/desactivar usuario
- `ajustar_cantidad_repuesto(id)` - Ajustar cantidades manualmente

Se actualizó:
- `nuevo_usuario()` - Ahora registra quién creó el usuario
- Todas las funciones de movimientos ahora registran el usuario que los realizó

## Verificación de Funcionamiento

Después de actualizar, verifica:

1. ✅ Puedes iniciar sesión con admin/admin123
2. ✅ Puedes ver la lista de usuarios
3. ✅ Puedes crear, editar y activar/desactivar usuarios
4. ✅ Puedes ajustar cantidades de repuestos
5. ✅ Puedes ver alertas de inventario
6. ✅ Los movimientos muestran el usuario que los registró

## Solución de Problemas

### Error de Conexión a MySQL
- Verifica que MySQL esté corriendo
- Confirma las credenciales en `config.py`
- Verifica que el puerto sea el correcto (3306 por defecto)

### Error de Tablas No Encontradas
- Asegúrate de haber ejecutado el script SQL correcto
- Verifica que la base de datos `taller_inventario` exista

### Error de Módulos No Encontrados
- Ejecuta: `pip install -r requirements.txt`

### Los Templates No Se Muestran
- Verifica que la carpeta `templates` tenga las subcarpetas correctas:
  - `templates/usuarios/`
  - `templates/alertas/`
  - `templates/movimientos/`
  - `templates/repuestos/`

## Soporte

Si encuentras algún problema durante la actualización, revisa:
1. Los logs del servidor (en la consola donde ejecutas `python app.py`)
2. Los logs de MySQL
3. El archivo `README.md` para información adicional

## Próximas Características Planificadas

- [ ] Búsqueda avanzada de vehículos por placa
- [ ] Reportes de inventario en PDF
- [ ] Gráficos de estadísticas
- [ ] API REST completa
- [ ] Módulo de facturación
- [ ] Integración con impresoras de tickets
