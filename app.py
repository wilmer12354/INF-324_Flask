from urllib import request
from flask import Flask, render_template, request, redirect, url_for, flash # type: ignore
from flask_mysqldb import MySQL # type: ignore

app=Flask(__name__)


app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='exafinal324'


mysql = MySQL(app)


@app.route('/')
def listar_pacientes():
    cursor = mysql.connection.cursor()
    

    cursor.execute("SELECT * FROM pacientes")
    pacientes = cursor.fetchall()
    

    cursor.execute("""
        SELECT medicos.id, medicos.nombre, especialidades.nombre AS especialidad
        FROM medicos
        LEFT JOIN especialidades ON medicos.especialidad_id = especialidades.id
    """)
    medicos = cursor.fetchall()

    cursor.execute("SELECT id, nombre FROM especialidades")
    especialidades = cursor.fetchall()
    
    cursor.close()
    
    return render_template(
        'Pacientes/pacientes.html', 
        pacientes=pacientes, 
        medicos=medicos, 
        especialidades=especialidades)


@app.route('/eliminar_paciente/<int:id>')
def eliminar_paciente(id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM consultas WHERE paciente_id = %s", (id,))
        cursor.execute("DELETE FROM pacientes WHERE id = %s", (id,))
        
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar: {str(e)}', 'error')
    finally:
        cursor.close()
    
    return redirect(url_for('listar_pacientes'))
@app.route('/editar_paciente/<int:id>', methods=['GET', 'POST'])
def editar_paciente(id):
    cursor = mysql.connection.cursor()
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        fecha_nacimiento = request.form['fecha_nacimiento']
        telefono = request.form['telefono']
    
        cursor.execute("""
            UPDATE pacientes 
            SET nombre = %s, apellido = %s, 
            fecha_nacimiento = %s, telefono = %s 
            WHERE id = %s
        """, (nombre, apellido, fecha_nacimiento, telefono, id))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('listar_pacientes'))
    
    cursor.execute("SELECT * FROM pacientes WHERE id = %s", (id,))
    paciente = cursor.fetchone()
    cursor.close()
    
    return render_template('Pacientes/editar_paciente.html', paciente=paciente)

@app.route('/agregar_paciente', methods=['GET', 'POST'])
def agregar_paciente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        fecha_nacimiento = request.form['fecha_nacimiento']
        telefono = request.form['telefono']
        
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO pacientes 
            (nombre, apellido, fecha_nacimiento, telefono) 
            VALUES (%s, %s, %s, %s)
        """, (nombre, apellido, fecha_nacimiento, telefono))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('listar_pacientes'))
    
    return render_template('Pacientes/agregar_paciente.html')




# CONSULTAS
@app.route('/consultas')
def listar_consultas():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM consultas")
        consultas = cursor.fetchall()
        
        cursor.execute("""
            SELECT medicos.id, medicos.nombre, especialidades.nombre AS especialidad
            FROM medicos
            LEFT JOIN especialidades ON medicos.especialidad_id = especialidades.id
        """)
        medicos = cursor.fetchall()
        
        cursor.execute("SELECT id, nombre FROM especialidades")
        especialidades = cursor.fetchall()
        
        cursor.close()
        
        return render_template(
            'Consultas/consultas.html', 
            consultas=consultas, 
            medicos=medicos, 
            especialidades=especialidades
        )
    except Exception as e:
        return f"Error al obtener datos: {str(e)}"

    
@app.route('/eliminar_consulta/<int:id>')
def eliminar_consulta(id):
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("DELETE FROM consultas WHERE paciente_id = %s", (id,))

        
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar: {str(e)}', 'error')
    finally:
        cursor.close()
    
    return redirect(url_for('listar_consultas'))

@app.route('/editar_consulta/<int:id>', methods=['GET', 'POST'])
def editar_consulta(id):
    cursor = mysql.connection.cursor()
    
    if request.method == 'POST':
        paciente_id = request.form['paciente_id']
        medico_id = request.form['medico_id']
        fecha = request.form['fecha']
        diagnostico = request.form['diagnostico']
        
        cursor.execute("""
            UPDATE consultas 
            SET paciente_id = %s, medico_id = %s, fecha = %s, diagnostico = %s
            WHERE id = %s
        """, (paciente_id, medico_id, fecha, diagnostico, id)) # type: ignore

        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('listar_consultas'))
    
    cursor.execute("SELECT * FROM consultas WHERE id = %s", (id,))
    consulta = cursor.fetchone()

    cursor.execute("SELECT id, CONCAT(nombre, ' ', apellido) AS nombre_completo FROM pacientes")
    pacientes = cursor.fetchall()
    
    cursor.execute("SELECT id, nombre FROM medicos")
    medicos = cursor.fetchall()
    cursor.close()
    
    return render_template('Consultas/editar_consultas.html', consulta=consulta, pacientes=pacientes, medicos=medicos)


@app.route('/agregar_consulta', methods=['GET', 'POST'])
def agregar_consulta():
    cursor = mysql.connection.cursor()
    
    if request.method == 'POST':
        paciente_id = request.form['paciente_id']
        medico_id = request.form['medico_id']
        fecha = request.form['fecha']
        diagnostico = request.form['diagnostico']
        
        cursor.execute("""
            INSERT INTO consultas (paciente_id, medico_id, fecha, diagnostico)
            VALUES (%s, %s, %s, %s)
        """, (paciente_id, medico_id, fecha, diagnostico))
        
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('listar_consultas'))
    
    cursor.execute("SELECT id, CONCAT(nombre, ' ', apellido) AS nombre_completo FROM pacientes")
    pacientes = cursor.fetchall()
    
    cursor.execute("SELECT id, nombre FROM medicos")
    medicos = cursor.fetchall()
    
    cursor.close()
    return render_template('Consultas/agregar_consultas.html', pacientes=pacientes, medicos=medicos)





if __name__ == '__main__':
    app.run(debug=True)
    
    