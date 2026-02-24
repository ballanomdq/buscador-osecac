# Reemplaza la sección de LOGIN con esto:
if not st.session_state.autenticado:
    _, col2, _ = st.columns([1,2,1])
    with col2:
        st.markdown('<br><br>', unsafe_allow_html=True)
        
        # Secuencia secreta (3 toques, pausa, 2 toques)
        SECUENCIA = [3, 2]  # Tres toques, pausa, dos toques
        if 'toques' not in st.session_state:
            st.session_state.toques = []
        if 'ultimo_toque' not in st.session_state:
            st.session_state.ultimo_toque = time.time()
        
        # Logo clickeable
        try:
            with open("LOGO1.png", "rb") as f:
                img_b64 = base64.b64encode(f.read()).decode()
            
            # CSS para animación del logo
            st.markdown("""
            <style>
            .logo-tap {
                cursor: pointer;
                transition: all 0.1s;
                animation: breathe 3s infinite;
            }
            .logo-tap:active {
                transform: scale(0.95);
                filter: drop-shadow(0 0 20px #38bdf8);
            }
            @keyframes breathe {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.05); opacity: 0.9; }
                100% { transform: scale(1); opacity: 1; }
            }
            .tap-indicator {
                display: flex;
                gap: 10px;
                justify-content: center;
                margin: 20px 0;
            }
            .tap-dot {
                width: 15px;
                height: 15px;
                border-radius: 50%;
                background: #334155;
                transition: all 0.3s;
            }
            .tap-dot.active {
                background: #38bdf8;
                box-shadow: 0 0 15px #38bdf8;
                transform: scale(1.2);
            }
            </style>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                # Logo con detección de toques
                logo_clicked = st.button("", key="logo_tap", help="TOCÁ EL LOGO EN SECUENCIA")
                st.markdown(f'<center><img src="data:image/png;base64,{img_b64}" style="width:150px; margin-bottom:10px;" class="logo-tap"></center>', unsafe_allow_html=True)
                
                if logo_clicked:
                    ahora = time.time()
                    # Si pasó más de 2 segundos, reiniciar secuencia
                    if ahora - st.session_state.ultimo_toque > 2:
                        st.session_state.toques = []
                    
                    st.session_state.toques.append(ahora)
                    st.session_state.ultimo_toque = ahora
                    
                    # Mostrar indicadores visuales
                    dots = []
                    for i in range(max(SECUENCIA)):
                        if i < len(st.session_state.toques):
                            dots.append('<span class="tap-dot active"></span>')
                        else:
                            dots.append('<span class="tap-dot"></span>')
                    
                    st.markdown(f'<div class="tap-indicator">{"".join(dots)}</div>', unsafe_allow_html=True)
                    
                    # Verificar secuencia
                    if len(st.session_state.toques) == SECUENCIA[0]:
                        st.info("✅ PAUSA AHORA...")
                        time.sleep(1)  # Pausa para siguiente grupo
                    elif len(st.session_state.toques) > SECUENCIA[0]:
                        segundo_grupo = len(st.session_state.toques) - SECUENCIA[0]
                        if segundo_grupo == SECUENCIA[1]:
                            st.success("🎉 SECUENCIA CORRECTA")
                            st.session_state.autenticado = True
                            st.rerun()
                        elif segundo_grupo > SECUENCIA[1]:
                            st.error("❌ Secuencia incorrecta")
                            st.session_state.toques = []
                            time.sleep(1)
                            st.rerun()
                else:
                    # Mostrar dots vacíos si no hay toques
                    dots = ['<span class="tap-dot"></span>' for _ in range(max(SECUENCIA))]
                    st.markdown(f'<div class="tap-indicator">{"".join(dots)}</div>', unsafe_allow_html=True)
                    
        except Exception as e:
            st.error("Esperando logo...")
        
        st.markdown("<p style='text-align:center; color:#94a3b8; font-size:0.9rem; margin-top:50px;'>👆 TOCÁ EL LOGO EN SECUENCIA</p>", unsafe_allow_html=True)
    st.stop()
