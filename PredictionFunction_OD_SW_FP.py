from pycaret.regression import *
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from PIL import Image
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset
import streamlit.components.v1 as components

st.set_page_config(page_title="Simulation Prediction Engine", page_icon="muscleman.jpg", layout="wide", initial_sidebar_state="auto")
st.title('SW,OD and Footprint Models')
st.write('This application predicts SW Inflation, OD Inflation, and Footprint values based on tyre parameters.\n Please upload the input data template for prediction')

image = Image.open('Tireimage.png')
st.sidebar.image(image)

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

#####



#@st.cache(suppress_st_warning=True,allow_output_mutation=True)
def loadmodel():
    model_SW = load_model('Final_SW_Model')
    model_OD = load_model('Final_OD_Model_V1')
    Footprint_width = load_model('Footprint_width_final_V1')
    Footprint_length = load_model('Footprint_length_final')
    Footprint_length80 = load_model('Footprint_length80_final')
    
    Footprint_width_RF = load_model('Footprint_width_final_RF_V3')
    Footprint_length_RF = load_model('Footprint_length_final_RF_V3')
    Footprint_length80_RF = load_model('Footprint_length80_final_RF_V3')  
   
    return model_SW,model_OD,Footprint_width, Footprint_length, Footprint_length80,Footprint_width_RF,Footprint_length_RF,Footprint_length80_RF

model_SW,model_OD,Footprint_width, Footprint_length, Footprint_length80,Footprint_width_RF,Footprint_length_RF,Footprint_length80_RF =  loadmodel()

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
	    features_df = features_df.dropna(axis=1, how='all')
	    features_df= features_df.transpose()
	    features_df.columns = features_df.iloc[0]
	    features_df= features_df.drop(features_df.index[0]) 
	    features_df['CuringRim_Width_Difference'] =  abs(features_df['Curing Width_UDMSIteration']) - abs(features_df['Rim Width_UDMSIteration'])
	    features_df['Belt_Angle_Difference'] =  abs(features_df['RBELT1_cured_angle']) - abs(features_df['RBELT2_cured_angle'])
	    features_df['Belt_Width_Difference'] =  features_df['Belt Width 1'] - features_df['Belt Width 2']
	    features_df['Section Ratio'] =  features_df['Section Height']/features_df['Cavity Section Width']
	    features_df["Aspect_ratio"] =features_df["size"].str.split("/").str[-1].str.extract('(\d+)').astype(int)

	    # Load_Index_mapping = pd.read_csv('Load_Index_mapping.csv')
	    # features_df= features_df.merge(Load_Index_mapping,on='Load_Index') 
	    


	    cols=[i for i in features_df.columns if i not in ["construction","size"]]
	    for col in cols:
	    	features_df[col]=pd.to_numeric(features_df[col])

	    st.write('The data you selected is')
	    st.write(features_df)
	    st.write('Data also contains dervived variables from data. Please scroll to the right to view')



if uploaded_file is not None:
	with st.expander('Data Drift Analysis'):
		if st.button('Plese click for drift calculation'):
			l1=Rawdata.columns
			l2=features_df.columns
			#st.write(list(set(l2) - set(l1)))

			l1=Rawdata.drop('Apex Ending', axis=1)
			l2=features_df.drop('Apex Ending', axis=1)

			l1 = l1[l2.columns]

			data_drift_report = Report(metrics=[DataDriftPreset(),])
			data_drift_report.run(current_data=l1, reference_data=l2, column_mapping=None)
			data_drift_report.save_html("file.html")
			with open("file.html", "rb") as pdf_file:
				PDFbyte = pdf_file.read()
			st.download_button(label="Download Data Drift Report",
                    data=PDFbyte,
                    file_name="file.html",
                    mime='application/octet-stream')



	
	st.subheader('Please Select')
	col1, col2, col3 = st.columns(3)

	with col1:
		features_df['inflation']= st.slider('Inflation', 180, 420, 210)

	with col3:
		features_df['load']= st.slider('Load', 100,870,420)
		features_df['load_inflation'] = features_df['load'] * features_df['inflation']
	    features_df['load_belt_width1'] = features_df['load'] * features_df['Belt Width 1']
	    features_df['load_load'] = features_df['load'] * features_df['load']
	    features_df['load_SectionRatio'] = features_df['load'] * features_df['Section Ratio']
	    features_df['load_SW'] = features_df['load'] * features_df['Cavity Section Width']
		# features_df['Load_index_ratio'] = features_df['load']/features_df['Load_index_kg']

	if st.button('Please Click for Prediction -'):
		df= pd.DataFrame()
		try:
			SW_value=round(predict_model(model_SW, features_df),2).Label
			df['SW Inflation'] = SW_value + features_df['Cavity Section Width']
			features_df['SW Inflation']=df['SW Inflation']
		except:
			st.write("Error!- Section Width Model Failed")
		try:
			OD_value = round(predict_model(model_OD, features_df),2).Label
			df['OD Inflation'] = features_df['Cavity Outer Diameter'] + OD_value
			features_df['OD Inflation']=df['OD Inflation']
		except:
			st.write("Error!-OD Model Failed")
			
		# try:
		# 	df['FP width'] = round(predict_model(Footprint_width, features_df),2).Label
		# except:
		# 	st.write("Error!-FP Width Model Failed")
		
		try:
			df['FP width RF'] = round(predict_model(Footprint_width_RF, features_df),2).Label
		except:
			st.write("Error!-FP Width Model Failed")

		# try:
		# 	df['FP_length']= round(predict_model(Footprint_length, features_df),2).Label
		# except:
		# 	st.write("Error!-FP Length Model Failed")
		
		try:
			df['FP_length RF']= round(predict_model(Footprint_length_RF, features_df),2).Label
		except:
			st.write("Error!-FP Length Model Failed")

		# try:
		# 	df['FP_length80'] = round(predict_model(Footprint_length80, features_df),2).Label
		# except:
		# 	st.write("Error!-FP Length 80 Model Failed")

		try:
			df['FP_length80 RF'] = round(predict_model(Footprint_length80_RF, features_df),2).Label
		except:
			df['FP_length80 RF'] = round(predict_model(Footprint_length80_RF, features_df),2).Label
			st.write("Error!-FP Length 80 Model Failed")

		try:
			df['FP_Index'] = round(df['FP_length80 RF']/df['FP_length RF'],2)
		except:
			st.write("Error!-FP Index Calculation Failed")
		
		st.write(df)
			    


st.sidebar.write('Please note that model predictions might not be accurate for data outside the training dataset ranges')


