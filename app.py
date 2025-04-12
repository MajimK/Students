import streamlit as st
import DB_work
from data_processor import process_excel_file


DB_work.init_db()


if "form" not in st.session_state:
    st.session_state.form = None
if "is_teacher" not in st.session_state:
    st.session_state.is_teacher = False
if "sort_config" not in st.session_state:
    st.session_state.sort_config = {
        "name": "asc",
        "points": "desc"
    }

st.title("🏫 Sistema de Puntos para Estudiantes")
if st.session_state.is_teacher:
    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            uploaded_file = st.file_uploader("", type=["xlsx"], label_visibility="collapsed")
            
            if uploaded_file:
                # Procesar el archivo
                student_names = process_excel_file(uploaded_file)
                
                if student_names:
                    # Mostrar vista previa
                    st.subheader(f"{len(student_names)} estudiantes encontrados")
                    st.write(student_names[:5])  # Muestra solo los primeros 5 como ejemplo
                    
                    # Botón de actualización (grande y llamativo)
                    group = st.selectbox("Grupo",["G-1","G-2"])
                    if st.button("✨ Actualizar Base de Datos", type="primary", use_container_width=True):
                        progress_bar = st.progress(0)
                        
                        for i, name in enumerate(student_names):
                            DB_work.add_student(group,name)
                            progress_bar.progress((i + 1) / len(student_names))
                        
                        st.balloons()
                        st.success(f"¡Base de datos actualizada con {len(student_names)} nombres!")
                else:
                    st.error("No se encontraron nombres en el archivo")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.session_state.is_teacher:
        if st.button("➕ Añadir Estudiante"):
            st.session_state.form = "add_student"
with col2:
    if st.session_state.is_teacher:
        if st.button("🚪 Cerrar Sesión"):
            st.session_state.is_teacher = False
            st.session_state.form = None
            st.rerun()
    else:
        if st.button("🔑 Login Profesor"):
            st.session_state.form = "login"
with col3:
    if st.session_state.is_teacher:
        if st.button("🔑 Cambiar credenciales"):
            st.session_state.form="Change_credentials"
with col4:
    if st.session_state.is_teacher:
        if st.button("🧹 Limpiar Base de Datos", type="primary"):
            st.session_state.form = "confirm_clear"

if st.session_state.form == "add_student":
    with st.form("add_student_form"):
        group = st.selectbox("Grupo",["G-1","G-2"])
        new_student = st.text_input("Nombre del estudiante")
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Agregar")
        with col2:
            if st.form_submit_button("❌ Cerrar"):
                st.session_state.form = None
                st.rerun()

        if submitted and new_student:
            if DB_work.add_student(group,new_student):
                st.success(f"Estudiante {new_student} agregado con éxito.")
                st.rerun()
            else:
                st.error("Ya existe un estudiante con ese nombre")

elif st.session_state.form == "login":
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Iniciar Sesión"):
                if DB_work.Verify_teacher(username, password):
                    st.session_state.is_teacher = True
                    st.session_state.form = None
                    st.success("¡Bienvenido Profesor!")
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas")
        with col2:
            if st.form_submit_button("❌ Cerrar"):
                st.session_state.form = None
                st.rerun()
elif st.session_state.form == "confirm_clear":
    with st.form("confirm_clear_form"):
        st.warning("⚠️ ¿Estás seguro de que quieres borrar TODOS los estudiantes?")
        st.write("Esta acción no se puede deshacer")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("✅ Sí, borrar todo"):
                DB_work.clear_students()
                st.success("Base de datos limpiada")
                st.session_state.form = None
                st.rerun()
        with col2:
            if st.form_submit_button("❌ Cancelar"):
                st.session_state.form = None
                st.rerun()
elif st.session_state.form == "Change_credentials":
    with st.form("update_user_form"):
        current_username = DB_work.get_current_teacher()
        new_username = st.text_input("Nuevo nombre de usuario", value=current_username)
        new_password = st.text_input("Nueva contraseña", type="password")
        confirm_password = st.text_input("Confirmar contraseña", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Actualizar Credenciales")
        with col2:
            if st.form_submit_button("❌ Cancelar"):
                st.session_state.form = None
                st.rerun()
        
        if submitted:
            if not new_username or not new_password:
                st.error("Todos los campos son obligatorios")
            elif new_password != confirm_password:
                st.error("Las contraseñas no coinciden")
            else:
                success = DB_work.update_teacher_credentials(
                    current_username,
                    new_username,
                    new_password
                )
                if success:
                    st.success("Credenciales actualizadas correctamente")
                    st.session_state.form = None
                    st.rerun()
                else:
                    st.error("El nombre de usuario ya existe, elija otro")

students = DB_work.get_students()

if students:
    st.write("### 📋 Tabla de Puntuaciones (Actualizada)")
    
    columns = DB_work.get_table_columns()
    student_df = {col: [] for col in columns}  

    for s in students:
        for i, col in enumerate(columns):
            student_df[col].append(s[i+1])

    st.table(student_df)

    if st.session_state.is_teacher:
        student_options = {s[2]: s[0] for s in students}
        selected_student = st.selectbox("Selecciona un estudiante", list(student_options.keys()))
        new_points = st.number_input("Nuevos puntos", min_value=0, step=1)

        if st.button("💱Actualizar Puntos"):
            DB_work.update_points(student_options[selected_student], new_points)
            st.success("Puntos actualizados.")
            st.rerun()
        if st.button("😥Borrar estudiante"):
            DB_work.remove_student(student_options[selected_student])
            st.rerun()
            
    else:
        st.warning("🔒 Inicia sesión como profesor para modificar puntos")
else:
    st.info("No hay estudiantes registrados aún.")
