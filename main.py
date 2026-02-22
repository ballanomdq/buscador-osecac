# HEADER PROFESIONAL CORREGIDO
col1, col2 = st.columns([5,1])

with col1:
    st.markdown("""
    <div class="capsula-header-mini">
        <div class="shimmer-efecto"></div>
        <h1 class="titulo-mini">OSECAC MDP / AGENCIAS</h1>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <style>
    .logo-container img {
        border-radius: 50%;
        box-shadow: 0 0 12px #38bdf8;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .logo-container img:hover {
        transform: scale(1.08);
        box-shadow: 0 0 22px #38bdf8;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image("LOGO1.png", width=90)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="subtitulo-lema">PORTAL DE APOYO PARA COMPAÑEROS</div>', unsafe_allow_html=True)
st.markdown("---")
