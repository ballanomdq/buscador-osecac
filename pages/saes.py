# ... (todo el código anterior se mantiene igual hasta el bloque de login)

        if btn_ingresar:
            if usuario and password:
                with st.spinner("Conectando con SAES..."):
                    session = requests.Session()
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3",
                    }
                    login_url = "http://portal.gmssa.com.ar/saes/Login.aspx"
                    
                    try:
                        # 1. GET inicial para obtener la página y los tokens
                        r = session.get(login_url, headers=headers, timeout=30)
                        soup = BeautifulSoup(r.text, 'html.parser')
                        
                        # 2. Extraer TODOS los inputs (no solo los hidden)
                        payload = {}
                        for input_tag in soup.find_all('input'):
                            name = input_tag.get('name')
                            if name:
                                payload[name] = input_tag.get('value', '')
                        
                        # 3. Agregar credenciales
                        payload['txtUsuario'] = usuario
                        payload['txtPassword'] = password
                        
                        # 4. Identificar el botón de login para el __EVENTTARGET
                        # Buscamos un input de tipo submit o button que contenga 'Ingresar' o 'Aceptar'
                        boton_login = None
                        for input_tag in soup.find_all(['input', 'a']):
                            if input_tag.get('type') in ['submit', 'button'] or input_tag.name == 'a':
                                value = input_tag.get('value', '') or input_tag.text
                                if 'ingresar' in value.lower() or 'aceptar' in value.lower() or 'login' in value.lower():
                                    boton_login = input_tag
                                    break
                        
                        if boton_login:
                            # En ASP.NET, el __EVENTTARGET suele ser el 'name' del botón
                            nombre_boton = boton_login.get('name')
                            if nombre_boton:
                                payload['__EVENTTARGET'] = nombre_boton
                                payload['__EVENTARGUMENT'] = ''
                        
                        # 5. POST con todos los datos
                        r_post = session.post(login_url, data=payload, headers=headers, timeout=30)
                        
                        # 6. Verificar si entramos (buscando si sigue apareciendo el input de password)
                        soup_post = BeautifulSoup(r_post.text, 'html.parser')
                        if not soup_post.find('input', {'type': 'password'}):
                            st.session_state.saes_logueado = True
                            st.session_state.usuario = usuario
                            st.session_state.password = password
                            st.session_state.session_cookies = session.cookies
                            st.success("✅ Acceso correcto.")
                            st.rerun()
                        else:
                            st.error("❌ SAES rechazó el formulario. Puede faltar un token de seguridad.")
                            with st.expander("Ver detalles técnicos"):
                                st.write("Código de estado:", r_post.status_code)
                                st.write("URL final:", r_post.url)
                                # Mostramos los campos que enviamos para ver si falta alguno
                                st.write("Campos enviados:", list(payload.keys()))
                                
                    except Exception as e:
                        st.error(f"💥 Error inesperado: {e}")
            else:
                st.warning("⚠️ Ingrese usuario y contraseña.")
