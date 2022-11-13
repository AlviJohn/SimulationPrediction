import collections.abc
collections.Iterable = collections.abc.Iterable
collections.Mapping = collections.abc.Mapping
collections.MutableSet = collections.abc.MutableSet
collections.MutableMapping = collections.abc.MutableMapping
from pycaret.regression import *
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from PIL import Image
import evidently
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulation Prediction Engine", page_icon="muscleman.jpg", layout="wide", initial_sidebar_state="auto")
st.title('SW,OD and Footprint Models')
st.write('This application predicts SW Inflation, OD Inflation, and Footprint values based on tyre parameters.Please upload the input data template')




@st.cache(suppress_st_warning=True,allow_output_mutation=True)
def loadmodel():
    model_SW = load_model('Final_SW_Model')
    model_OD = load_model('Final_OD_Model')
    Footprint_width = load_model('Footprint_width_final')
    Footprint_length = load_model('Footprint_length_final')
    Footprint_length80 = load_model('Footprint_length80_final') 
   
    return model_SW,model_OD,Footprint_width, Footprint_length, Footprint_length80

model_SW,model_OD,Footprint_width, Footprint_length, Footprint_length80 =  loadmodel()
Rawdata = pd.read_csv('RawData1.csv')
##Correction In Belt_Angle Difference
Rawdata['Belt_Angle_Difference'] =  abs(Rawdata['RBELT1_cured_angle']) - abs(Rawdata['RBELT2_cured_angle'])
##Correction In Belt_Angle Difference
Rawdata['CuringRim_Width_Difference'] =  abs(Rawdata['Curing Width_UDMSIteration']) - abs(Rawdata['Rim Width_UDMSIteration'])



with st.expander('Update the Data For Prediction'):
	uploaded_file = st.file_uploader("Choose a file")

	if uploaded_file is not None:
	    # Can be used wherever a "file-like" object is accepted:
	    features_df = pd.read_excel(uploaded_file,sheet_name='Template') 
	    features_df['CuringRim_Width_Difference'] =  abs(features_df['Curing Width_UDMSIteration']) - abs(features_df['Rim Width_UDMSIteration'])
	    features_df['Belt_Angle_Difference'] =  abs(features_df['RBELT1_cured_angle']) - abs(features_df['RBELT2_cured_angle'])
	    features_df['Belt_Width_Difference'] =  features_df['Belt Width 1'] - features_df['Belt Width 2']
	    features_df['Section Ratio'] =  features_df['Section Height']/features_df['Cavity Section Width']
	    features_df["Aspect_ratio"] =features_df["size"].str.split("/").str[-1].str.extract('(\d+)').astype(int)
	    st.write('The data you selected is')
	    st.write(features_df)
	    st.write('Data also contains dervived variables from data. Please scroll to the right to see')



if uploaded_file is not None:
	with st.expander('Data Drift Analysis'):
		if st.button('Plese click for drift calculation'):
			data_drift_report = Report(metrics=[DataDriftPreset(),])
			data_drift_report.run(current_data=features_df, reference_data=Rawdata, column_mapping=None)
			data_drift_report.save_html("file.html")
			with open("file.html", "rb") as pdf_file:
				PDFbyte = pdf_file.read()
			st.download_button(label="Download Data Drift Report",
                    data=PDFbyte,
                    file_name="file.html",
                    mime='application/octet-stream')





if st.button('Please click this button for Prediction'):
	SW_value = float(round(predict_model(model_SW, features_df),2).Label)
	OD_value = float(round(predict_model(model_OD, features_df),2).Label)
	
	features_df['OD Inflation'] = OD_value + features_df['Cavity Outer Diameter']
	features_df['SW Inflation'] = SW_value + features_df['Cavity Section Width']
	features_df['SW Inflation']=200
	features_df['load'] = 300
	FP_width_value = float(round(predict_model(Footprint_width, features_df),2).Label)
	FP_length_value = float(round(predict_model(Footprint_length, features_df),2).Label)
	FP_length80_value = float(round(predict_model(Footprint_length80, features_df),2).Label)
	st.write(' SW Inflation Prediction -->',float(round(features_df['SW Inflation'],2)) )
	st.write(' OD Inflation Prediction -->',float(round(features_df['OD Inflation'],2)))
	st.write(' FP Width Prediction -->',FP_width_value)
	st.write(' FP Length Prediction -->',FP_length_value)
	st.write(' FP Length 80 Prediction -->',FP_length80_value)


image = Image.open('muscle_man2.png')
st.sidebar.image(image)


st.sidebar.write('Please upload the template data for prediction.\n\n' )              
st.sidebar.write('Please note that model predictions might not be accurate for data outside the training dataset ranges')
