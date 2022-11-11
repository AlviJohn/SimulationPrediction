from pycaret.regression import load_model, predict_model
import streamlit as st
import pandas as pd
import numpy as np
import pickle


st.set_page_config(page_title="Dimension Optimization Model", page_icon="muscleman.jpg", layout="wide", initial_sidebar_state="auto")
st.title('Dimension Optimization Model')
st.write('This application predicts ContactArea and FpIndex based on the input variables')

@st.cache(suppress_st_warning=True,allow_output_mutation=True)
def predict_quality(model, df):   
    predictions_data = predict_model(model,data=df)
    return predictions_data['Label'][0]
    
@st.cache(suppress_st_warning=True,allow_output_mutation=True)
def loadmodel():
    with open('FP_Index_Model.pkl', "rb") as f:
        model_fpindex = pickle.load(f)
    with open('Contactarea_Model.pkl', "rb") as f:
        model_contactarea = pickle.load(f)
    return model_fpindex,model_contactarea
        

models=loadmodel()
model_fpindex=models[0]
model_contactarea=models[1]
#st.write(model_contactarea)    

Mould_SD = st.sidebar.slider(label = 'Mould_SD', min_value = 3,
                          max_value = 15 ,
                          value = 10,
                          step = 1)

Target_OD = st.sidebar.slider(label = 'Target_OD', min_value = 1041,
                          max_value = 1069,
                          value = 1050,
                          step = 1)



features = {'Mould_SD': Mould_SD, 'Target_OD': Target_OD}
features_df  = pd.DataFrame([features])

st.write('The data you selected is')
st.write(features_df)

if st.button('Predict'):   
    fpIndexprediction = round(predict_quality(model_fpindex, features_df),1)
    contactareaprediction = round(predict_quality(model_contactarea, features_df),1)
    st.write(' Based on feature values, FP Index Value is  '+ str(fpIndexprediction))
    st.write(' Based on feature values, Contactarea Value is '+ str(contactareaprediction))