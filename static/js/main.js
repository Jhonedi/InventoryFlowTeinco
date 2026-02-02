// Sistema de Inventario - JavaScript Principal

$(document).ready(function() {
    // Cargar notificaciones de alertas
    loadAlertasCount();
    
    // Actualizar notificaciones cada 30 segundos
    setInterval(loadAlertasCount, 30000);
    
    // Confirmar eliminaciones
    $('.btn-delete').on('click', function(e) {
        if (!confirm('¿Está seguro de que desea eliminar este registro?')) {
            e.preventDefault();
        }
    });
    
    // Auto-hide alerts después de 5 segundos
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Búsqueda en tiempo real para repuestos
    $('#repuesto-search').on('input', debounce(function() {
        const query = $(this).val();
        if (query.length >= 2) {
            searchRepuestos(query);
        }
    }, 300));
    
    // Formatear números como moneda
    $('.currency').each(function() {
        const value = parseFloat($(this).text());
        $(this).text(formatCurrency(value));
    });
});

// Cargar contador de alertas
function loadAlertasCount() {
    $.ajax({
        url: '/api/notificaciones',
        method: 'GET',
        success: function(data) {
            const count = data.length;
            if (count > 0) {
                $('#alertas-count').text(count).show();
            } else {
                $('#alertas-count').hide();
            }
        },
        error: function(error) {
            console.error('Error cargando notificaciones:', error);
        }
    });
}

// Buscar repuestos (para autocomplete)
function searchRepuestos(query) {
    $.ajax({
        url: '/api/repuestos/buscar',
        method: 'GET',
        data: { q: query },
        success: function(repuestos) {
            displayRepuestosResults(repuestos);
        },
        error: function(error) {
            console.error('Error buscando repuestos:', error);
        }
    });
}

// Mostrar resultados de búsqueda de repuestos
function displayRepuestosResults(repuestos) {
    const resultsContainer = $('#repuestos-results');
    resultsContainer.empty();
    
    if (repuestos.length === 0) {
        resultsContainer.append('<div class="list-group-item">No se encontraron repuestos</div>');
        return;
    }
    
    repuestos.forEach(function(repuesto) {
        const item = `
            <a href="#" class="list-group-item list-group-item-action" 
               data-repuesto-id="${repuesto.id}"
               data-repuesto-codigo="${repuesto.codigo}"
               data-repuesto-nombre="${repuesto.nombre}"
               data-repuesto-precio="${repuesto.precio_venta}"
               data-repuesto-stock="${repuesto.cantidad_actual}">
                <div class="d-flex justify-content-between">
                    <div>
                        <strong>${repuesto.codigo}</strong> - ${repuesto.nombre}
                    </div>
                    <div>
                        <span class="badge bg-secondary">Stock: ${repuesto.cantidad_actual}</span>
                        <span class="badge bg-success">$${repuesto.precio_venta}</span>
                    </div>
                </div>
            </a>
        `;
        resultsContainer.append(item);
    });
}

// Marcar alerta como leída
function marcarAlertaLeida(alertaId) {
    $.ajax({
        url: `/api/alertas/marcar-leida/${alertaId}`,
        method: 'POST',
        success: function() {
            $(`#alerta-${alertaId}`).fadeOut();
            loadAlertasCount();
        },
        error: function(error) {
            console.error('Error marcando alerta:', error);
        }
    });
}

// Cargar vehículos de un cliente
function loadVehiculosCliente(clienteId) {
    $.ajax({
        url: `/api/vehiculos-cliente/${clienteId}`,
        method: 'GET',
        success: function(vehiculos) {
            const select = $('#vehiculo_cliente_id');
            select.empty();
            select.append('<option value="">Seleccione un vehículo</option>');
            
            vehiculos.forEach(function(vehiculo) {
                select.append(`
                    <option value="${vehiculo.id}">
                        ${vehiculo.placa} - ${vehiculo.marca} ${vehiculo.modelo}
                    </option>
                `);
            });
        },
        error: function(error) {
            console.error('Error cargando vehículos:', error);
        }
    });
}

// Utilidades

// Debounce function para optimizar búsquedas
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Formatear números como moneda
function formatCurrency(value) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 0
    }).format(value);
}

// Formatear fecha
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-CO', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Validar formularios
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
        form.classList.add('was-validated');
        return false;
    }
    return true;
}

// Mostrar loading spinner
function showLoading(containerId) {
    const container = $(`#${containerId}`);
    container.html(`
        <div class="spinner-container">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando...</span>
            </div>
        </div>
    `);
}

// Calcular total de factura
function calcularTotalFactura() {
    let subtotal = 0;
    $('.item-factura').each(function() {
        const precio = parseFloat($(this).data('precio')) || 0;
        const cantidad = parseInt($(this).find('.cantidad-input').val()) || 0;
        subtotal += precio * cantidad;
    });
    
    const iva = subtotal * 0.19; // IVA 19%
    const total = subtotal + iva;
    
    $('#subtotal').text(formatCurrency(subtotal));
    $('#iva').text(formatCurrency(iva));
    $('#total').text(formatCurrency(total));
}

// Event listeners para formularios específicos
$(document).on('change', '#cliente_id', function() {
    const clienteId = $(this).val();
    if (clienteId) {
        loadVehiculosCliente(clienteId);
    }
});

$(document).on('click', '.marcar-leida-btn', function(e) {
    e.preventDefault();
    const alertaId = $(this).data('alerta-id');
    marcarAlertaLeida(alertaId);
});

$(document).on('change', '.cantidad-input', function() {
    calcularTotalFactura();
});

// Exportar funciones globales
window.tallerInventario = {
    loadAlertasCount,
    searchRepuestos,
    marcarAlertaLeida,
    loadVehiculosCliente,
    formatCurrency,
    formatDate,
    validateForm,
    showLoading,
    calcularTotalFactura
};
