# reportes.py
import os
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import xlsxwriter

def generar_reporte_ventas_pdf(ventas, fecha_inicio=None, fecha_fin=None):
    """Generar reporte de ventas en PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("Reporte de Ventas", styles['Title'])
    elements.append(title)
    
    # Filtros aplicados
    if fecha_inicio or fecha_fin:
        filtros_text = "Filtros aplicados: "
        if fecha_inicio:
            filtros_text += f"Desde: {fecha_inicio.strftime('%d/%m/%Y')} "
        if fecha_fin:
            filtros_text += f"Hasta: {fecha_fin.strftime('%d/%m/%Y')}"
        elements.append(Paragraph(filtros_text, styles['Normal']))
    
    elements.append(Spacer(1, 12))
    
    # Datos de ventas
    data = [['ID', 'Fecha', 'Cliente', 'Productos', 'Total']]
    
    total_general = 0
    for venta in ventas:
        total_general += float(venta.total)
        productos = ', '.join([f"{d.cantidad}x {d.producto.nombre[:20]}" 
                              for d in venta.detalles[:3]])
        if len(venta.detalles) > 3:
            productos += f"... (+{len(venta.detalles)-3} más)"
        
        cliente_nombre = venta.cliente.nombre if venta.cliente else "Sin cliente"
        
        data.append([
            venta.id_venta,
            venta.fecha_venta.strftime('%d/%m/%Y'),
            cliente_nombre,
            productos,
            f"${venta.total:.2f}"
        ])
    
    # Total general
    data.append(['', '', '', 'TOTAL GENERAL:', f"${total_general:.2f}"])
    
    # Crear tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(table)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generar_reporte_compras_pdf(compras, fecha_inicio=None, fecha_fin=None):
    """Generar reporte de compras en PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("Reporte de Compras", styles['Title'])
    elements.append(title)
    
    # Filtros aplicados
    if fecha_inicio or fecha_fin:
        filtros_text = "Filtros aplicados: "
        if fecha_inicio:
            filtros_text += f"Desde: {fecha_inicio.strftime('%d/%m/%Y')} "
        if fecha_fin:
            filtros_text += f"Hasta: {fecha_fin.strftime('%d/%m/%Y')}"
        elements.append(Paragraph(filtros_text, styles['Normal']))
    
    elements.append(Spacer(1, 12))
    
    # Datos de compras
    data = [['ID', 'Fecha', 'Proveedor', 'Productos', 'Total']]
    
    total_general = 0
    for compra in compras:
        total_general += float(compra.total)
        productos = ', '.join([f"{d.cantidad}x {d.producto.nombre[:20]}" 
                              for d in compra.detalles[:3]])
        if len(compra.detalles) > 3:
            productos += f"... (+{len(compra.detalles)-3} más)"
        
        data.append([
            compra.id_compra,
            compra.fecha_compra.strftime('%d/%m/%Y'),
            compra.proveedor.nombre if compra.proveedor else "Sin proveedor",
            productos,
            f"${compra.total:.2f}"
        ])
    
    # Total general
    data.append(['', '', '', 'TOTAL GENERAL:', f"${total_general:.2f}"])
    
    # Crear tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
        ('GRID', (0, 0), (-1, -2), 1, colors.black),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(table)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generar_reporte_inventario_excel(productos):
    """Generar reporte de inventario en Excel"""
    buffer = BytesIO()
    
    # Crear libro de Excel
    workbook = xlsxwriter.Workbook(buffer)
    worksheet = workbook.add_worksheet('Inventario')
    
    # Formato para encabezados
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#366092',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    # Formato para datos
    data_format = workbook.add_format({
        'border': 1,
        'align': 'center'
    })
    
    # Formato para números
    money_format = workbook.add_format({
        'border': 1,
        'num_format': '$#,##0.00',
        'align': 'right'
    })
    
    # Formato para stock bajo
    low_stock_format = workbook.add_format({
        'border': 1,
        'bg_color': '#FFC7CE',
        'font_color': '#9C0006',
        'align': 'center'
    })
    
    # Encabezados
    headers = ['ID', 'Producto', 'Descripción', 'Precio Compra', 
               'Precio Venta', 'Stock', 'Valor en Inventario', 'Estado']
    
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Datos
    row = 1
    total_valor_inventario = 0
    
    for producto in productos:
        stock = producto.stock
        valor_inventario = float(producto.precio_compra) * stock
        total_valor_inventario += valor_inventario
        
        if stock <= 0:
            estado = "AGOTADO"
            cell_format = low_stock_format
        elif stock <= 5:
            estado = "BAJO STOCK"
            cell_format = low_stock_format
        else:
            estado = "NORMAL"
            cell_format = data_format
        
        worksheet.write(row, 0, producto.id_producto, data_format)
        worksheet.write(row, 1, producto.nombre, data_format)
        worksheet.write(row, 2, producto.descripcion or "", data_format)
        worksheet.write(row, 3, float(producto.precio_compra), money_format)
        worksheet.write(row, 4, float(producto.precio_venta), money_format)
        worksheet.write(row, 5, stock, data_format)
        worksheet.write(row, 6, valor_inventario, money_format)
        worksheet.write(row, 7, estado, cell_format)
        
        row += 1
    
    # Total general
    worksheet.write(row, 5, 'TOTAL:', header_format)
    worksheet.write(row, 6, total_valor_inventario, money_format)
    
    # Ajustar anchos de columna
    worksheet.set_column('A:A', 8)
    worksheet.set_column('B:B', 25)
    worksheet.set_column('C:C', 30)
    worksheet.set_column('D:E', 15)
    worksheet.set_column('F:F', 10)
    worksheet.set_column('G:G', 18)
    worksheet.set_column('H:H', 15)
    
    workbook.close()
    buffer.seek(0)
    return buffer

def generar_reporte_clientes_pdf(clientes):
    """Generar reporte de clientes en PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("Reporte de Clientes", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Estadísticas
    total_clientes = len(clientes)
    clientes_con_ventas = sum(1 for c in clientes if c.get('total_compras', 0) > 0)
    
    stats_text = f"Total Clientes: {total_clientes} | Clientes con Ventas: {clientes_con_ventas}"
    elements.append(Paragraph(stats_text, styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Datos de clientes
    data = [['ID', 'Nombre', 'Cédula', 'Email', 'Total Compras', 'Total Gastado']]
    
    for cliente in clientes:
        total_gastado = cliente.get('total_gastado', '$0.00')
        if isinstance(total_gastado, str) and total_gastado.startswith('$'):
            total_gastado_num = float(total_gastado.replace('$', '').replace(',', ''))
        else:
            total_gastado_num = float(total_gastado or 0)
        
        data.append([
            cliente['id'],
            cliente['nombre'],
            cliente.get('cedula', 'N/A'),
            cliente.get('email', 'Sin email')[:30],
            cliente.get('total_compras', 0),
            f"${total_gastado_num:.2f}"
        ])
    
    # Crear tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
    ]))
    
    elements.append(table)
    
    # Pie de página
    elements.append(Spacer(1, 20))
    fecha_generacion = Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Italic'])
    elements.append(fecha_generacion)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generar_reporte_proveedores_pdf(proveedores):
    """Generar reporte de proveedores en PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("Reporte de Proveedores", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Estadísticas
    total_proveedores = len(proveedores)
    stats_text = f"Total Proveedores Registrados: {total_proveedores}"
    elements.append(Paragraph(stats_text, styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Datos de proveedores
    data = [['ID', 'Nombre', 'RUC', 'Teléfono', 'Email', 'Dirección']]
    
    for proveedor in proveedores:
        direccion = proveedor.direccion or "Sin dirección"
        if len(direccion) > 30:
            direccion = direccion[:27] + "..."
        
        email = proveedor.correo or "Sin email"
        if len(email) > 25:
            email = email[:22] + "..."
        
        data.append([
            proveedor.id_proveedor,
            proveedor.nombre,
            proveedor.ruc,
            proveedor.telefono or "N/A",
            email,
            direccion
        ])
    
    # Crear tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8e44ad')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f4ecf7')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d7bde2')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    ]))
    
    elements.append(table)
    
    # Pie de página
    elements.append(Spacer(1, 20))
    fecha_generacion = Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Italic'])
    elements.append(fecha_generacion)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generar_reporte_productos_pdf(productos):
    """Generar reporte de productos en PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("Reporte de Productos", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Estadísticas
    total_productos = len(productos)
    productos_bajo_stock = sum(1 for p in productos if p.stock <= 5)
    productos_agotados = sum(1 for p in productos if p.stock <= 0)
    
    stats_text = f"Total Productos: {total_productos} | Bajo Stock: {productos_bajo_stock} | Agotados: {productos_agotados}"
    elements.append(Paragraph(stats_text, styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Datos de productos
    data = [['ID', 'Nombre', 'Precio Compra', 'Precio Venta', 'Stock', 'Valor Inventario', 'Estado']]
    
    for producto in productos:
        stock = producto.stock
        valor_inventario = float(producto.precio_compra) * stock
        
        if stock <= 0:
            estado = "AGOTADO"
        elif stock <= 5:
            estado = "BAJO STOCK"
        else:
            estado = "NORMAL"
        
        data.append([
            producto.id_producto,
            producto.nombre[:25],
            f"${float(producto.precio_compra):.2f}",
            f"${float(producto.precio_venta):.2f}",
            stock,
            f"${valor_inventario:.2f}",
            estado
        ])
    
    # Crear tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#e8f6f3')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#a3e4d7')),
    ]))
    
    elements.append(table)
    
    # Pie de página
    elements.append(Spacer(1, 20))
    fecha_generacion = Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Italic'])
    elements.append(fecha_generacion)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def generar_reporte_usuarios_pdf(usuarios):
    """Generar reporte de usuarios en PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("Reporte de Usuarios del Sistema", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Estadísticas
    total_usuarios = len(usuarios)
    fecha_mas_antigua = min([u.fecha_registro for u in usuarios]) if usuarios else datetime.now()
    fecha_mas_reciente = max([u.fecha_registro for u in usuarios]) if usuarios else datetime.now()
    
    stats_text = f"Total Usuarios: {total_usuarios} | Usuario más antiguo: {fecha_mas_antigua.strftime('%d/%m/%Y')}"
    elements.append(Paragraph(stats_text, styles['Normal']))
    elements.append(Spacer(1, 12))
    
    # Datos de usuarios
    data = [['ID', 'Usuario', 'Fecha Registro', 'Antigüedad']]
    
    for usuario in usuarios:
        antiguedad = (datetime.now() - usuario.fecha_registro).days
        antiguedad_text = f"{antiguedad} días"
        
        if antiguedad > 365:
            antiguedad_text = f"{antiguedad//365} años, {antiguedad%365} días"
        elif antiguedad > 30:
            antiguedad_text = f"{antiguedad//30} meses, {antiguedad%30} días"
        
        data.append([
            usuario.id,
            usuario.usuario,
            usuario.fecha_registro.strftime('%d/%m/%Y %H:%M'),
            antiguedad_text
        ])
    
    # Crear tabla
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#fadbd8')),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#f1948a')),
    ]))
    
    elements.append(table)
    
    # Pie de página
    elements.append(Spacer(1, 20))
    fecha_generacion = Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Italic'])
    elements.append(fecha_generacion)
    
    # Nota de seguridad
    nota = Paragraph("Nota: Este reporte contiene información sensible. Manténgalo en un lugar seguro.", 
                     styles['Italic'])
    nota.textColor = colors.HexColor('#c0392b')
    elements.append(nota)
    
    # Generar PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer