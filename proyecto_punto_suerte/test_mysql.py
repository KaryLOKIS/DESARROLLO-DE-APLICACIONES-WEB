from conexion.conexion import conectar

conn = conectar()
print("✅ Conectado a MySQL correctamente")
conn.close()