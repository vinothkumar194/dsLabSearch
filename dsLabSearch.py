import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration to wide mode
st.set_page_config(layout="wide")


# Function to reset filters
def reset_filters():
    if 'reset' not in st.session_state:
        st.session_state.reset = True


# Initialize session state for filters
if 'reset' in st.session_state and st.session_state.reset:
    st.session_state.equipment_search = "All"
    st.session_state.school_department_search = "All"
    st.session_state.measure_search = "All"
    st.session_state.reset = False
elif 'equipment_search' not in st.session_state:
    st.session_state.equipment_search = "All"
    st.session_state.school_department_search = "All"
    st.session_state.measure_search = "All"

# Title of the application
st.title("Dhanalakshmi Srinivasan University Laboratory Equipment Search - Beta 0.1")

# Google Sheets link
sheet_url = "https://docs.google.com/spreadsheets/d/13TE6wJbMV9iDaQaBIKoQOG9rHavqQZKq/export?format=xlsx"

try:
    # Download the data from the Google Sheets link
    response = requests.get(sheet_url)
    response.raise_for_status()

    # Read the Excel file into a DataFrame
    data = pd.read_excel(BytesIO(response.content))

    # Create two columns for layout
    col1, col2 = st.columns([1, 4])

    with col1:
        st.sidebar.header("Search Filters")

        # Extract relevant columns for search functionality
        equipment_names = sorted(data.iloc[:, 1].dropna().unique().tolist())
        schools_departments = sorted(data.iloc[:, 2].dropna().unique().tolist())
        measures = sorted(data.iloc[:, 14].dropna().unique().tolist())

        # Dropdown search for equipment name
        equipment_search = st.sidebar.selectbox(
            "Search by Equipment Name:",
            ["All"] + equipment_names,
            index=0 if st.session_state.equipment_search == "All" else equipment_names.index(
                st.session_state.equipment_search) + 1,
            key="equipment_search"
        )

        # Dropdown search for school/department
        school_department_search = st.sidebar.selectbox(
            "Search by School/Department:",
            ["All"] + schools_departments,
            index=0 if st.session_state.school_department_search == "All" else schools_departments.index(
                st.session_state.school_department_search) + 1,
            key="school_department_search"
        )

        # Dropdown search for what to measure
        measure_search = st.sidebar.selectbox(
            "Search by Measurement Purpose:",
            ["All"] + measures,
            index=0 if st.session_state.measure_search == "All" else measures.index(
                st.session_state.measure_search) + 1,
            key="measure_search"
        )

        # Reset button functionality
        if st.sidebar.button("Reset Search Filters", on_click=reset_filters):
            st.rerun()

    # Filter data based on search inputs
    filtered_data = data.copy()

    if equipment_search != "All":
        filtered_data = filtered_data[filtered_data.iloc[:, 1].fillna('').str.contains(equipment_search, case=False)]

    if school_department_search != "All":
        filtered_data = filtered_data[
            filtered_data.iloc[:, 2].fillna('').str.contains(school_department_search, case=False)]

    if measure_search != "All":
        filtered_data = filtered_data[filtered_data.iloc[:, 14].fillna('').str.contains(measure_search, case=False)]

    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Data Table", "Column View", "Department Analytics", "Equipment Distribution"])

    with tab1:
        st.subheader("Filtered Results - Full Table View")
        if not filtered_data.empty:
            # Add column selection
            st.write("Select columns to display:")
            cols_to_display = st.multiselect(
                "Choose columns:",
                options=filtered_data.columns.tolist(),
                default=filtered_data.columns.tolist()[:5]  # Show first 5 columns by default
            )

            # Display selected columns with horizontal scrolling
            if cols_to_display:
                st.dataframe(
                    filtered_data[cols_to_display],
                    use_container_width=True,
                    height=400
                )

                # Add download button
                csv = filtered_data[cols_to_display].to_csv(index=False)
                st.download_button(
                    label="Download filtered data as CSV",
                    data=csv,
                    file_name="filtered_equipment_data.csv",
                    mime="text/csv",
                )
            else:
                st.warning("Please select at least one column to display.")
        else:
            st.write("No matching records found.")

    with tab2:
        st.subheader("Column-wise View")
        if not filtered_data.empty:
            # Create column selector
            selected_column = st.selectbox(
                "Select column to view:",
                options=filtered_data.columns.tolist()
            )

            # Display selected column data
            col_data = filtered_data[[selected_column]]
            st.dataframe(
                col_data,
                use_container_width=True,
                height=400
            )

            # Show basic statistics for numeric columns
            if pd.api.types.is_numeric_dtype(filtered_data[selected_column]):
                st.write("Basic Statistics:")
                stats = col_data.describe()
                st.dataframe(stats)

    with tab3:
        st.subheader("Department-wise Equipment Distribution")

        # Count equipment per department
        dept_counts = data.iloc[:, 2].value_counts()

        # Create horizontal bar chart in green color
        fig_dept = px.bar(
            y=dept_counts.index,
            x=dept_counts.values,
            labels={'x': 'Number of Equipment', 'y': 'Department'},
            title='Equipment Distribution Across Departments',
            orientation='h',  # Make the bar plot horizontal
            color_discrete_sequence=['#2ecc71']  # Set green color
        )
        fig_dept.update_layout(
            showlegend=False,
            height=max(400, len(dept_counts) * 30)  # Adjust height based on number of departments
        )
        st.plotly_chart(fig_dept, use_container_width=True)

        # Department equipment value analysis
        if 'Cost' in data.columns:
            dept_value = data.groupby(data.iloc[:, 2])['Cost'].sum().sort_values(
                ascending=True)  # Changed to ascending for bottom-to-top
            fig_value = px.bar(
                y=dept_value.index,
                x=dept_value.values,
                labels={'x': 'Total Equipment Value', 'y': 'Department'},
                title='Department-wise Equipment Value Distribution',
                orientation='h',  # Make the bar plot horizontal
                color_discrete_sequence=['#27ae60']  # Different shade of green
            )
            fig_value.update_layout(
                height=max(400, len(dept_value) * 30)  # Adjust height based on number of departments
            )
            st.plotly_chart(fig_value, use_container_width=True)

    with tab4:
        st.subheader("Equipment Analytics")

        # Equipment type distribution - horizontal bar chart
        equipment_counts = data.iloc[:, 1].value_counts().head(15)  # Increased to show top 15
        fig_equip = px.bar(
            y=equipment_counts.index,
            x=equipment_counts.values,
            labels={'x': 'Count', 'y': 'Equipment Type'},
            title='Most Common Equipment Types',
            orientation='h',  # Make the bar plot horizontal
        )
        fig_equip.update_layout(
            height=max(400, len(equipment_counts) * 30)  # Adjust height based on number of equipment types
        )
        st.plotly_chart(fig_equip, use_container_width=True)

        # Measurement purpose distribution
        measure_counts = data.iloc[:, 14].value_counts()
        fig_measure = px.bar(
            y=measure_counts.index,
            x=measure_counts.values,
            labels={'x': 'Count', 'y': 'Measurement Purpose'},
            title='Distribution of Measurement Purposes',
            orientation='h',  # Make the bar plot horizontal
        )
        fig_measure.update_layout(
            height=max(400, len(measure_counts) * 30)  # Adjust height based on number of measurement purposes
        )
        st.plotly_chart(fig_measure, use_container_width=True)

        # Add equipment age analysis if date information is available
        if 'Purchase Date' in data.columns:
            data['Purchase Date'] = pd.to_datetime(data['Purchase Date'])
            data['Age'] = (pd.Timestamp.now() - data['Purchase Date']).dt.days / 365

            fig_age = px.histogram(
                data,
                x='Age',
                nbins=20,
                title='Equipment Age Distribution (Years)'
            )
            st.plotly_chart(fig_age, use_container_width=True)

    # Add summary statistics at the bottom
    st.subheader("Summary Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Equipment Count", len(filtered_data))

    with col2:
        st.metric("Number of Departments", filtered_data.iloc[:, 2].nunique())

    with col3:
        st.metric("Number of Equipment Types", filtered_data.iloc[:, 1].nunique())

except Exception as e:
    st.error(f"An error occurred while accessing the data: {e}")
