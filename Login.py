# -*- coding: utf-8 -*-
'''
Created on 2022年5月3日

@author: xiaoyw
'''

import streamlit as st
import streamlit_authenticator as stauth
import BigBooks

names = ['肖永威', '管理员']
usernames = ['xiaoyw', 'admin']
passwords = ['S0451', 'ad4516']

hashed_passwords = stauth.Hasher(passwords).generate()

authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
    'some_cookie_name', 'some_signature_key', cookie_expiry_days=30)

name, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status:
    with st.container():
        cols1,cols2 = st.columns(2)
        cols1.write('欢迎 *%s*' % (name))
        with cols2.container():
            authenticator.logout('Logout', 'main')
    #authenticator.logout('Logout', 'main')
    #st.write('欢迎 *%s*' % (name))
    #st.title('Some content')
    BigBooks.main()
elif authentication_status == False:
    st.error('Username/password is incorrect')
elif authentication_status == None:
    st.warning('Please enter your username and password')
    
#if st.session_state['authentication_status']:
#    authenticator.logout('Logout', 'main')
#    st.write('Welcome *%s*' % (st.session_state['name']))
#    st.title('Some content')
#elif st.session_state['authentication_status'] == False:
#    st.error('Username/password is incorrect')
#elif st.session_state['authentication_status'] == None:
#    st.warning('Please enter your username and password')