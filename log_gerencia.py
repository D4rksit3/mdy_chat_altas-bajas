import pyodbc
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Conexión a la base de datos
connection_string = 'mssql+pyodbc://jroque:Mdy12345*@10.200.52.245/master?driver=SQL+Server'

engine = create_engine(connection_string)
# Consulta SQL
query = """
SELECT
    c.session_id,
	s.login_name AS 'Nombre de inicio de sesión',
    c.client_net_address AS 'Dirección IP',
	DB_NAME(s.database_id) AS 'Base de datos' ,

	 CASE WHEN s.host_name = 'WIN-7GRO1967G2K' THEN 'Server_ofisis' ELSE s.host_name END AS Hostname,
	s.program_name AS 'Nombre de programa',
	s.client_interface_name 'Interfaz de conexion',
	s.login_time AS 'Inicio de conexion',
	s.last_request_end_time AS 'Fin de conexion',
	 CONVERT(VARCHAR(10), DATEDIFF(HOUR, s.login_time, s.last_request_end_time)) + ':' +
    CONVERT(VARCHAR(10), DATEDIFF(MINUTE, s.login_time, s.last_request_end_time) % 60) + ':' +
    CONVERT(VARCHAR(10), DATEDIFF(SECOND, s.login_time, s.last_request_end_time) % 60) AS 'Tiempo de conexion',
    s.status AS 'Estado'
FROM sys.dm_exec_sessions AS s
JOIN sys.dm_exec_connections AS c ON s.session_id = c.session_id  where s.login_time BETWEEN DATEADD(DAY, -7, GETDATE()) AND GETDATE() order by s.login_time desc

"""

# Ejecutar la consulta y obtener los resultados en un DataFrame de pandas
df = pd.read_sql(query, engine)


fecha_actual = datetime.now().strftime("%Y-%m-%d")
# Nombre del archivo Excel
file_name = f'log_{fecha_actual}.xlsx'

# Guardar los resultados en un archivo Excel
df.to_excel(file_name, index=False)

# Configuración del correo electrónico
sender_email = "auditorialog@mdycontactcenter.com"
receiver_email = "sabino.delacruz@mdybpo.com"
cc_email = "pe_cl_iteje4@mdybpo.com,ejecutivositcolonial@mdycontactcenter.com"
subject = f"Auditoria de conexiones ofisis {fecha_actual}"

# Crear un objeto MIMEMultipart para el correo electrónico
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Cc"] = cc_email
message["Subject"] = subject

# Agregar un cuerpo de texto al correo electrónico
body = """
Se comparte la auditoria de conexiones.
"""
message.attach(MIMEText(body, "plain"))

# Adjuntar el archivo Excel al correo electrónico
part = MIMEBase("application", "octet-stream")
part.set_payload(open(file_name, "rb").read())
encoders.encode_base64(part)
part.add_header("Content-Disposition", f"attachment; filename= {file_name}")
message.attach(part)

# Configurar el servidor SMTP y enviar el correo electrónico
smtp_server = "mail.mdycontactcenter.com"
smtp_port = 587
smtp_username = "auditorialog@mdycontactcenter.com"
smtp_password = "Mdy12345*"

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_username, smtp_password)
    receiver_emails = [receiver_email, cc_email]
    server.sendmail(sender_email, receiver_emails, message.as_string())
    print("Correo enviado.")
