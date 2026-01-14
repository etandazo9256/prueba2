# diagnostico.py
import sys
import os

# Asegura que pueda importar app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db

with app.app_context():
    from sqlalchemy import inspect as sa_inspect

    inspector = sa_inspect(db.engine)

    print("=" * 50)
    print("📦 TABLAS EXISTENTES EN LA BASE DE DATOS")
    print("=" * 50)

    for table in inspector.get_table_names():
        print(f"- {table}")

    # -----------------------------
    # DETALLE COMPRA
    # -----------------------------
    print("\n" + "=" * 50)
    print("🔍 INSPECCIÓN DE DetalleCompra")
    print("=" * 50)

    try:
        from app import DetalleCompra

        print("Columnas del modelo DetalleCompra:")
        for col in DetalleCompra.__table__.columns:
            print(f"  - {col.name} ({col.type})")

        detalle = DetalleCompra.query.first()
        if detalle:
            print("\nPrimer registro DetalleCompra:")
            print(f"  id_detalle     : {detalle.id_detalle}")
            print(f"  id_compra      : {detalle.id_compra}")
            print(f"  id_producto    : {detalle.id_producto}")
            print(f"  cantidad       : {detalle.cantidad}")
            print(f"  precio_unitario: {detalle.precio_unitario}")
            print(f"  subtotal       : {detalle.subtotal}")
        else:
            print("⚠️ No hay registros en detalle_compras")

    except Exception as e:
        print(f"❌ Error en DetalleCompra: {e}")

    # -----------------------------
    # DETALLE VENTA
    # -----------------------------
    print("\n" + "=" * 50)
    print("🔍 INSPECCIÓN DE DetalleVenta")
    print("=" * 50)

    try:
        from app import DetalleVenta

        print("Columnas del modelo DetalleVenta:")
        for col in DetalleVenta.__table__.columns:
            print(f"  - {col.name} ({col.type})")

        detalle = DetalleVenta.query.first()
        if detalle:
            print("\nPrimer registro DetalleVenta:")
            print(f"  id_detalle     : {detalle.id_detalle}")
            print(f"  id_venta       : {detalle.id_venta}")
            print(f"  id_producto    : {detalle.id_producto}")
            print(f"  cantidad       : {detalle.cantidad}")
            print(f"  precio_unitario: {detalle.precio_unitario}")
            print(f"  subtotal       : {detalle.subtotal}")

            if hasattr(detalle, "producto") and detalle.producto:
                print(f"  producto.nombre: {detalle.producto.nombre}")
        else:
            print("⚠️ No hay registros en detalle_ventas")

    except Exception as e:
        print(f"❌ Error en DetalleVenta: {e}")
