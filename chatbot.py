import streamlit as st
import mysql

conn = mysql.connector.connect(
	host="localhost",
	port=3306,
	user="GM",
	password="Smilly12345!",
	database="rca_prediction",
	auth_plugin='mysql_native_password'
)

cursor = conn.cursor()

# 2. Function to talk to HeatWave
def ask_heatwave(question, history):
    try:
        # Configure the chat to use your Vector Store (RAG)
        # We set the 'vector_store' option to point to your table

        #options = """
        #{
		#	JSON_OBJECT("vector_store", JSON_ARRAY("rca_prediction.support_vector_store.embedding"))
		#}
        #"""
        		
		#options = """
        #{
		#JSON_OBJECT("model_options", JSON_OBJECT("language", "gr"),
		#"vector_store_columns", JSON_OBJECT("segment", "rca_prediction.rca_training_data.rootcause", "segment_embedding", 
		#"rca_prediction.rca_training_data.embedding"), "embed_model_id", "all_minilm_l12_v2")
		#}
        #"""		

        options = """
        {
			JSON_OBJECT("vector_store", JSON_ARRAY("rca_prediction.rca_training_data.embedding"),
			"vector_store_columns", JSON_OBJECT("segment", "rca_prediction.rca_training_data.rootcause", 
			"segment_embedding", "rca_prediction.rca_training_data.embedding"),
			"model_options", JSON_OBJECT("language", "en"),"embed_model_id", "all_minilm_l12_v2")
		}
        """
		
        # Set the options for this session
        cursor.execute(f"SET @options = '{options}';")
	
        # Call the Chat routine (History is managed by HeatWave automatically in the session)
        # Note: For a simple stateless web app, we might need to pass history manually 
        # if the session resets, but HeatWave Chat handles context if the connection stays open.
        # For this simple example, we rely on RAG retrieval per question.
        
        cursor.callproc('sys.HEATWAVE_CHAT', [question])
        
        # Fetch the answer
        for result in cursor.stored_results():
            response = result.fetchone()[0]
            # The response is a JSON object, we just want the text
            return response

    except Exception as e:
        return f"Error: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# 3. Build the UI with Streamlit
st.caption("🤖 AI Support για την μεθοδολογία RCA (Root Cause Analysis) στη Διαχείριση Έργων")
st.caption("Γεώργιος Μαργέλης ΑΜ: 3262024009")
st.caption("Αθανάσιος Βαρρής  ΑΜ: 3262024001")
st.caption("--")
st.caption("Powered by MySQL HeatWave GenAI")

# Initialize chat history in the app
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
         st.markdown(message["content"])

# Input box for the user
if prompt := st.chat_input("Describe your issue in natural language..."):
    # Show user message
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Get answer from Oracle HeatWave
    with st.chat_message("assistant"):
        with st.spinner("Σε αναμονή της απαντήσεως.."):
            # Parse the JSON response from HeatWave to get clean text
            import json
            raw_answer = ask_heatwave(prompt, st.session_state.messages)
            try:
                # HeatWave often returns JSON like {"text": "Answer..."}
                parsed = json.loads(raw_answer)
                final_text = parsed.get('text', raw_answer)
            except:
                final_text = raw_answer
            
            st.markdown(final_text)
            
    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": final_text})

