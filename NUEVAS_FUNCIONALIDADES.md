# Nuevas Funcionalidades Agregadas - Módulo de Clientes y Vehículos

## 📋 Resumen de Cambios

Se han agregado las siguientes funcionalidades al sistema:

### ✅ 1. **Módulo Completo de Clientes**
- **Crear clientes** con toda su información básica (documento, nombre, teléfono, email, dirección)
- **Editar clientes** existentes
- **Buscar clientes** por documento o nombre
- **Ver historial** de vehículos de cada cliente
- Soporte para diferentes tipos de documento (CC, NIT, CE, Pasaporte)

### ✅ 2. **Módulo Completo de Vehículos**
- **Registrar vehículos** asociados a clientes con validación de placas
- **Editar información** de vehículos
- **Validación automática** de formato de placas (ABC123 para autos, ABC12D para motos)
- Información completa: marca, modelo, año, color, kilometraje, motor, chasis
- Vista organizada de vehículos por cliente

### ✅ 3. **Dashboard Interactivo**
- **Tarjetas clicables** que navegan a las secciones correspondientes:
  - Total Repuestos → Lista de repuestos
  - Valor Inventario → Lista de repuestos
  - Alertas Activas → Lista de alertas
  - Movimientos Hoy → Historial de movimientos
- Efectos visuales mejorados al pasar el mouse

### ✅ 4. **Datos de Prueba Completos**
- Archivo SQL con datos listos para usar
- 8 clientes de ejemplo
- 13 vehículos registrados (incluye autos y motos)
- 40 repuestos en diferentes categorías
- Movimientos de inventario de ejemplo
- Alertas activas
- Usuarios adicionales (almacenista, vendedor, técnicos)

## 🚀 Cómo Usar las Nuevas Funcionalidades

### Acceder al Módulo de Clientes

1. Inicia sesión en el sistema
2. En el menú superior, haz clic en **"Clientes"**
3. Verás la lista de todos los clientes registrados

### Crear un Nuevo Cliente

1. En la lista de clientes, haz clic en **"Nuevo Cliente"**
2. Completa el formulario:
   - Tipo de documento (CC, NIT, CE, Pasaporte)
   - Número de documento (único por cliente)
   - Nombre completo
   - Teléfono (opcional)
   - Email (opcional)
   - Dirección (opcional)
3. Haz clic en **"Guardar Cliente"**

### Registrar un Vehículo

1. En la lista de clientes, haz clic en el botón **"Ver Vehículos"** (ícono de auto)
2. Haz clic en **"Registrar Vehículo"**
3. Completa la información:
   - **Placa** (validación automática de formato)
   - Marca y Modelo (selección desde lista)
   - Año (opcional)
   - Color (opcional)
   - Kilometraje actual (opcional)
   - Número de motor (opcional)
   - Número de chasis (opcional)
   - Observaciones (opcional)
4. Haz clic en **"Guardar Vehículo"**

### Validación de Placas

El sistema valida automáticamente el formato de las placas:
- **Autos**: ABC123 (3 letras + 3 números)
- **Motos**: ABC12D (3 letras + 2 números + 1 letra)

Si ingresas una placa inválida, el sistema te alertará antes de guardar.

### Dashboard Mejorado

Ahora puedes hacer clic en cualquiera de las 4 tarjetas del dashboard para navegar rápidamente:
- **Total Repuestos** / **Valor Inventario** → Ir a lista de repuestos
- **Alertas Activas** → Ver todas las alertas
- **Movimientos Hoy** → Ver historial completo

## 📂 Archivos Nuevos Creados

### Templates
1. `templates/clientes/lista.html` - Lista de clientes
2. `templates/clientes/form.html` - Formulario crear/editar cliente
3. `templates/clientes/vehiculos.html` - Vista de vehículos de un cliente
4. `templates/vehiculos/form.html` - Formulario crear/editar vehículo

### Base de Datos
5. `database/datos_prueba.sql` - Datos de ejemplo para cargar

### Estilos
6. Actualización en `static/css/style.css` - Estilos para dashboard clicable

## 🗄️ Cargar Datos de Prueba

Si quieres empezar con datos de ejemplo para probar el sistema:

```bash
# Primero crea la base de datos con el schema v2
mysql -u root -p < database/schema_v2.sql

# Luego carga los datos de prueba
mysql -u root -p < database/datos_prueba.sql
```

### Qué Incluyen los Datos de Prueba

- **4 usuarios adicionales**:
  - `almacenista1` / `pass123` - Carlos Mendoza
  - `vendedor1` / `pass123` - María Rodríguez
  - `tecnico1` / `pass123` - Juan Pérez
  - `tecnico2` / `pass123` - Ana García

- **8 clientes**:
  - Pedro Martínez López (CC 1234567890)
  - Laura Gómez Ruiz (CC 9876543210)
  - Transportes Rápidos S.A.S. (NIT)
  - Y 5 más...

- **13 vehículos**:
  - 11 autos con placas válidas
  - 2 motos con placas válidas
  - Diferentes marcas: Chevrolet, Ford, Nissan, Toyota, Honda, Mazda

- **40 repuestos** en 8 categorías:
  - Filtros (4)
  - Lubricantes (4)
  - Frenos (4)
  - Suspensión (4)
  - Motor (4)
  - Eléctrico (4)
  - Neumáticos (4)
  - Iluminación (4)
  - Accesorios (4)

- **Movimientos de inventario** de ejemplo
- **3 alertas activas** de stock bajo

## 🔗 Nuevas Rutas Disponibles

### Clientes
- `GET /clientes` - Lista de clientes
- `GET /clientes/nuevo` - Formulario nuevo cliente
- `POST /clientes/nuevo` - Crear cliente
- `GET /clientes/<id>/editar` - Formulario editar cliente
- `POST /clientes/<id>/editar` - Actualizar cliente
- `GET /clientes/<id>/vehiculos` - Ver vehículos del cliente

### Vehículos
- `GET /vehiculos/nuevo/<cliente_id>` - Formulario nuevo vehículo
- `POST /vehiculos/nuevo/<cliente_id>` - Crear vehículo
- `GET /vehiculos/<id>/editar` - Formulario editar vehículo
- `POST /vehiculos/<id>/editar` - Actualizar vehículo

## 🎨 Permisos de Usuario

### Quién puede gestionar clientes y vehículos:
- ✅ **Administrador**: Acceso completo
- ✅ **Almacenista**: Puede crear y editar
- ✅ **Vendedor**: Puede crear y editar
- ❌ **Técnico**: Solo puede ver

## 📊 Flujo de Trabajo Recomendado

1. **Registrar el cliente** primero con sus datos básicos
2. **Registrar sus vehículos** (uno o varios)
3. Cuando haya un **servicio o venta**:
   - Ir a Movimientos → Salida de Inventario
   - Seleccionar el repuesto
   - Asociar al técnico, cliente y vehículo correspondiente
4. El sistema automáticamente:
   - Actualiza el inventario
   - Genera alertas si es necesario
   - Registra quién hizo el movimiento

## 🔍 Buscar Información

### Buscar Clientes
- Por número de documento
- Por nombre completo
- Usa el buscador en la lista de clientes

### Buscar Vehículos
- Ve directamente al cliente
- Todas sus vehículos aparecerán en tarjetas organizadas
- Cada tarjeta muestra: placa, marca/modelo, año, color, kilometraje

### Información de Placa
La placa de cada vehículo es **única** en el sistema, lo que permite:
- Identificación rápida del vehículo
- Evitar duplicados
- Asociación directa en movimientos de inventario

## ⚠️ Notas Importantes

1. **Placas Únicas**: No puedes registrar dos vehículos con la misma placa
2. **Documentos Únicos**: No puedes registrar dos clientes con el mismo número de documento
3. **Validación de Placas**: El sistema valida el formato automáticamente
4. **Vehículos Activos**: Los vehículos desactivados no aparecen en las listas principales
5. **Historial Completo**: Todos los cambios quedan registrados con fecha y usuario

## 🚦 Estado del Proyecto

### Funcionalidades Completadas
- ✅ CRUD completo de clientes
- ✅ CRUD completo de vehículos
- ✅ Validación de placas vehiculares
- ✅ Dashboard interactivo
- ✅ Datos de prueba completos
- ✅ Integración con módulo de movimientos
- ✅ Búsqueda y filtros

### Próximas Mejoras Sugeridas
- [ ] Historial de servicios por vehículo
- [ ] Búsqueda avanzada por placa desde cualquier módulo
- [ ] Recordatorios de mantenimiento por kilometraje
- [ ] Exportar lista de clientes a Excel
- [ ] Fotos de vehículos
- [ ] Múltiples contactos por cliente

## 💡 Ejemplos de Uso

### Caso 1: Cliente con Múltiples Vehículos
```
Cliente: Transportes Rápidos S.A.S.
Vehículos:
- JKL012 - Toyota Hilux 2021
- MNO345 - Toyota Hilux 2020
- PQR678 - Toyota Hilux 2019
```

### Caso 2: Cliente Particular
```
Cliente: Pedro Martínez López
Vehículos:
- ABC123 - Chevrolet Spark 2018 (Auto)
- DEF456 - Nissan Sentra 2020 (Auto)
- HIJ45K - Mazda 2 2021 (Moto)
```

## 📞 Soporte

Si encuentras algún problema:
1. Verifica que la base de datos esté actualizada con schema_v2.sql
2. Revisa los logs del servidor (consola donde corre `python app.py`)
3. Verifica los permisos del usuario actual
4. Asegúrate de tener todos los templates en sus carpetas correspondientes

## 🎉 ¡Listo!

Ahora tienes un sistema completo para:
- Gestionar clientes
- Registrar vehículos
- Asociar servicios a vehículos específicos
- Hacer seguimiento completo del inventario
- Tener un dashboard interactivo y funcional

¡Disfruta del sistema mejorado!
