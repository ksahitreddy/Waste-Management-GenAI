import streamlit as st
import pandas as pd
import PIL.Image
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=api_key) #Put your API Key
model = genai.GenerativeModel(model_name="gemini-1.5-pro")

# Dummy credentials for Government and Industry
credentials = {
    "Government": {"admin": "gov_admin", "user": "gov_user"},
    "Industry": {"admin": "ind_admin", "user": "ind_user"}
}

# Initialize Session State for Page Navigation and Data
if "page" not in st.session_state:
    st.session_state.page = "Home"

if "industry_submitted_data" not in st.session_state:
    st.session_state.industry_submitted_data = []  # Initialize the data list for Industry dashboard

# Home Page with Role Selection
def home_page():
    st.markdown(
        "<h1 style='text-align: center; color: #4CAF50;'>Welcome to the Trash Classifier App</h1>",
        unsafe_allow_html=True,
    )
    st.write("### Choose your role to proceed:")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("👤 Public"):
            st.session_state.page = "Public"
    with col2:
        if st.button("🏛️ Government"):
            st.session_state.page = "Login"
            st.session_state.role = "Government"
    with col3:
        if st.button("🏭 Industry"):
            st.session_state.page = "Login"
            st.session_state.role = "Industry"

# Login Page for Government and Industry
def login_page():
    role = st.session_state.role  # Government or Industry
    st.markdown(f"<h1 style='color: #4CAF50;'>Login - {role}</h1>", unsafe_allow_html=True)
    st.write(f"Please enter your login details for {role}.")

    username = st.text_input("👤 Username")
    password = st.text_input("🔒 Password", type="password")

    if st.button("Login"):
        if username in credentials[role] and credentials[role][username] == password:
            st.session_state.page = f"{role} Dashboard"
            st.success(f"Welcome, {role} user!")
        else:
            st.error("Invalid credentials. Please try again.")

# Public Page with Image/Text Classification
def public_page():
    st.markdown("<h1 style='color: #4CAF50;'>Trash Classification - Public</h1>", unsafe_allow_html=True)
    st.write("Upload an image or enter text to classify trash as Renewable or Non-Renewable.")

    # Image Upload Section
    st.subheader("📷 Upload an Image")
    uploaded_image = st.file_uploader("Choose an image file", type=["jpg", "png", "jpeg"])
    if uploaded_image:
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        if st.button("Classify Image"):
            sample_file_1 = PIL.Image.open(uploaded_image)
            prompt = (
                "Tell me what components of the image are useful or renewable, "
                "and by what percentage of the image? What examples of products can I make out of it? "
                "Are the products cost effective?"
            )
            response = model.generate_content(
                [prompt, sample_file_1],
                generation_config=genai.GenerationConfig(
                    max_output_tokens=1000,
                    temperature=1,
                ),
            )
            st.write(response.text)

    # Text Input Section
    st.subheader("💬 Enter Text Data")
    prompt = st.text_area("Enter text related to trash classification")
    if st.button("Classify Text"):
        response = model.generate_content(
            [prompt],
            generation_config=genai.GenerationConfig(
                max_output_tokens=1000,
                temperature=1,
            ),
        )
        st.write(response.text)

# Industry Dashboard for Waste Entry and AI Prompt
def industry_dashboard():
    st.markdown("<h1 style='color: #4CAF50;'>Industry Dashboard</h1>", unsafe_allow_html=True)
    st.write("### Enter Waste Information")

    # Searchable Waste Type
    waste_types = [
        "Plastic Bottle", "Glass Jar", "Aluminum Can", "Paper", "Cardboard",
        "Organic Waste", "E-Waste", "Textiles", "Food Waste", "Metal"
    ]

    waste_type = st.text_input("Enter Waste Type (e.g., Plastic Bottle, Metal, etc.)")

    # Show suggestions as the user types
    if waste_type:
        suggestions = [waste for waste in waste_types if waste_type.lower() in waste.lower()]
        if suggestions:
            st.write("### Suggestions")
            for suggestion in suggestions:
                st.write(suggestion)

    # Choose amount entry type
    amount_type = st.radio("Select Amount Type", ("Kilograms (kg)", "Number of Items"))

    # Amount Entry based on selected type
    if amount_type == "Kilograms (kg)":
        amount = st.number_input("Enter Amount (in kg)", min_value=0.0, step=0.1)
    elif amount_type == "Number of Items":
        amount = st.number_input("Enter Number of Items", min_value=0, step=1)

    # Submit Button
    if st.button("Submit Entry"):
        if waste_type and amount > 0:
            st.session_state.industry_submitted_data.append(
                {"Waste Type": waste_type, "Amount": amount, "Amount Type": amount_type}
            )
            st.success(f"Data for {waste_type} added successfully!")
        else:
            st.warning("Please provide a valid waste type and amount.")

    # Display the submitted data in a table
    if st.session_state.industry_submitted_data:
        st.subheader("Submitted Waste Data")
        df = pd.DataFrame(st.session_state.industry_submitted_data)
        st.dataframe(df)

    # Prompt Field for AI to Generate Suggestions
    st.subheader("🔮 Generate Product Suggestions")
    prompt = st.text_area(
        "Enter your query for generating suggestions based on the data entered (e.g., 'Suggest best products from the waste data')."
    )

    if st.button("Generate Suggestions"):
        if st.session_state.industry_submitted_data:
            # Create a summary of the submitted data for AI
            data_summary = "\n".join(
                [
                    f"{entry['Amount']} {entry['Amount Type']} of {entry['Waste Type']}"
                    for entry in st.session_state.industry_submitted_data
                ]
            )
            # Generate AI prompt
            ai_prompt = (
                f"The following waste data has been submitted:\n\n{data_summary}\n\n"
                f"Based on this, {prompt}"
            )
            response = model.generate_content(
                [ai_prompt],
                generation_config=genai.GenerationConfig(
                    max_output_tokens=1000,
                    temperature=0.7,
                ),
            )
            st.subheader("AI Suggestions")
            st.write(response.text)
        else:
            st.warning("No data submitted yet. Please add waste data before generating suggestions.")

# Government Dashboard
def government_dashboard():
    st.markdown("<h1 style='color: #4CAF50;'>Government Dashboard</h1>", unsafe_allow_html=True)
    st.write("Dashboard options for the Government.")

# Main Function to Handle Page Navigation
def main():
    st.set_page_config(page_title="Trash Classifier", page_icon="♻️", layout="wide")

    if st.session_state.page == "Home":
        home_page()
    elif st.session_state.page == "Login":
        login_page()
    elif st.session_state.page == "Public":
        public_page()
    elif st.session_state.page == "Industry Dashboard":
        industry_dashboard()
    elif st.session_state.page == "Government Dashboard":
        government_dashboard()

if __name__ == "__main__":
    main()

