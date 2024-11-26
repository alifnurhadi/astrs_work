import streamlit as st
import dashboard1 as dashb

st.set_page_config(layout='wide',initial_sidebar_state='collapsed')
pages = st.sidebar.selectbox('Pilih Halaman :' ,['Executive','Correlation'])

if pages == 'Executive':
    dashb.main()

elif pages == 'Correlation':
    dashb.correlation()

else :
    None