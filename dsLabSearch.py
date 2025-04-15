import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
import time

# Set page configuration to wide mode with better title and icon
st.set_page_config(
    page_title="DSU Laboratory Equipment Search",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for improved UI
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1E88E5;
        color: white;
    }
    .metric-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .filter-section {
        background-color: #f0f8ff;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .stButton>button {
        width: 100%;
        background-color: #1E88E5;
        color: white;
    }
    .stButton>button:hover {
        background-color: #0D47A1;
    }
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

# Function to reset filters
def reset_filters():
    if 'reset' not in st.session_state:
        st.session_state.reset = True

# Function to display tooltip for better user guidance
def display_tooltip(text, tooltip_text):
    return f'<div class="tooltip">{text} ℹ️<span class="tooltiptext">{tooltip_text}</span></div>'

# Function to display a custom metric card
def metric_card(title, value, delta=None):
    delta_html = f"<span style='color:{'green' if delta >= 0 else 'red'}'>{delta:+g}%</span>" if delta is not None else ""
    st.markdown(f"""
    <div class="metric-card">
        <h3>{title}</h3>
        <h2>{value}</h2>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

# Initialize session state for filters
if 'reset' in st.session_state and st.session_state.reset:
    st.session_state.equipment_search = "All"
    st.session_state.school_department_search = "All"
    st.session_state.measure_search = "All"
    st.session_state.text_search = ""
    st.session_state.dark_mode = False
    st.session_state.reset = False
elif 'equipment_search' not in st.session_state:
    st.session_state.equipment_search = "All"
    st.session_state.school_department_search = "All"
    st.session_state.measure_search = "All"
    st.session_state.text_search = ""
    st.session_state.dark_mode = False

# App header with logo and improved title
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.markdown('<div style="font-size:48px;text-align:center">🔬</div>', unsafe_allow_html=True)
with col_title:
    st.markdown('<h1 class="main-header">Dhanalakshmi Srinivasan University<br>Laboratory Equipment Search System</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:#666">Version 1.0 - Search and analyze laboratory equipment across all departments</p>', unsafe_allow_html=True)

# Display a progress bar for better loading UX
with st.spinner("Loading laboratory equipment data..."):
    progress_bar = st.progress(0)
    
    # Google Sheets link
    sheet_url = "https://docs.google.com/spreadsheets/d/13TE6wJbMV9iDaQaBIKoQOG9rHavqQZKq/export?format=xlsx"

    try:
        # Simulate loading for better UX
        for i in range(100):
            time.sleep(0.01)
            progress_bar.progress(i + 1)
        
        # Download the data from the Google Sheets link
        response = requests.get(sheet_url)
        response.raise_for_status()

        # Read the Excel file into a DataFrame
        data = pd.read_excel(BytesIO(response.content))
        
        # Clear the progress bar after loading
        progress_bar.empty()
        st.success("Data loaded successfully!")
        
        # Dark mode toggle in sidebar
        st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.sidebar.markdown('<h2 style="text-align:center">Search Controls</h2>', unsafe_allow_html=True)
        dark_mode = st.sidebar.checkbox("Dark Mode", value=st.session_state.dark_mode, key="dark_mode")
        
        if dark_mode:
            # Apply dark mode styling
            st.markdown("""
            <style>
                .stApp {
                    background-color: #121212;
                    color: #E0E0E0;
                }
                .main-header, .sub-header {
                    color: #90CAF9;
                }
                .metric-card {
                    background-color: #1E1E1E;
                    color: #E0E0E0;
                }
                .stTabs [data-baseweb="tab"] {
                    background-color: #333333;
                    color: #E0E0E0;
                }
                .filter-section {
                    background-color: #1E1E1E;
                }
            </style>
            """, unsafe_allow_html=True)
        
        # Create sidebar filter section with improved styling
        st.sidebar.markdown('<div class="filter-section">', unsafe_allow_html=True)
        st.sidebar.markdown(display_tooltip("Search Filters", "Use these filters to narrow down equipment results"), unsafe_allow_html=True)

        # Add a text search box for more flexibility
        text_search = st.sidebar.text_input(
            "Search by keyword:",
            value=st.session_state.text_search,
            key="text_search",
            help="Search across all fields"
        )

        # Extract relevant columns for search functionality
        equipment_names = sorted(data.iloc[:, 1].dropna().unique().tolist())
        schools_departments = sorted(data.iloc[:, 2].dropna().unique().tolist())
        measures = sorted(data.iloc[:, 14].dropna().unique().tolist())

        # Dropdown search for equipment name
        equipment_search = st.sidebar.selectbox(
            "Filter by Equipment Name:",
            ["All"] + equipment_names,
            index=0 if st.session_state.equipment_search == "All" else equipment_names.index(
                st.session_state.equipment_search) + 1,
            key="equipment_search",
            help="Select specific equipment type"
        )

        # Dropdown search for school/department
        school_department_search = st.sidebar.selectbox(
            "Filter by School/Department:",
            ["All"] + schools_departments,
            index=0 if st.session_state.school_department_search == "All" else schools_departments.index(
                st.session_state.school_department_search) + 1,
            key="school_department_search",
            help="Select specific department"
        )

        # Dropdown search for what to measure
        measure_search = st.sidebar.selectbox(
            "Filter by Measurement Purpose:",
            ["All"] + measures,
            index=0 if st.session_state.measure_search == "All" else measures.index(
                st.session_state.measure_search) + 1,
            key="measure_search",
            help="Select what the equipment measures"
        )

        # Reset button functionality with improved styling
        if st.sidebar.button("Reset All Filters", on_click=reset_filters):
            st.rerun()
            
        st.sidebar.markdown('</div>', unsafe_allow_html=True)  # Close filter section
        
        # Add quick help section for better user guidance
        with st.sidebar.expander("🔍 How to use this app"):
            st.markdown("""
            1. **Search**: Use filters or text search to find equipment
            2. **View**: Switch between tabs to see different data views
            3. **Explore**: Click on charts to filter data
            4. **Download**: Export filtered data as CSV or Excel
            """)
            
        # Add contact information
        st.sidebar.markdown("---")
        st.sidebar.markdown("📧 For support: support@dsu.edu")
        st.sidebar.markdown("🔄 Last updated: April 2025")
        st.sidebar.markdown('</div>', unsafe_allow_html=True)  # Close sidebar content

        # Filter data based on search inputs
        filtered_data = data.copy()

        # Text search across all columns - new feature
        if text_search:
            text_filter = filtered_data.astype(str).apply(
                lambda x: x.str.contains(text_search, case=False)
            ).any(axis=1)
            filtered_data = filtered_data[text_filter]

        # Apply other filters
        if equipment_search != "All":
            filtered_data = filtered_data[filtered_data.iloc[:, 1].fillna('').str.contains(equipment_search, case=False)]

        if school_department_search != "All":
            filtered_data = filtered_data[
                filtered_data.iloc[:, 2].fillna('').str.contains(school_department_search, case=False)]

        if measure_search != "All":
            filtered_data = filtered_data[filtered_data.iloc[:, 14].fillna('').str.contains(measure_search, case=False)]

        # Create tabs for different views with enhanced styling and icons
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📋 Data Table", 
            "📊 Column View", 
            "🏫 Department Analytics", 
            "⚙️ Equipment Distribution",
            "📝 Equipment Details"  # New tab
        ])

        with tab1:
            st.markdown('<h2 class="sub-header">Filtered Results - Full Table View</h2>', unsafe_allow_html=True)
            
            if not filtered_data.empty:
                # Add column selection with better UX
                with st.expander("Select columns to display", expanded=True):
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

                    # Add download options with improved UI
                    col1, col2 = st.columns(2)
                    with col1:
                        csv = filtered_data[cols_to_display].to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name="filtered_equipment_data.csv",
                            mime="text/csv",
                        )
                    with col2:
                        excel_buffer = BytesIO()
                        filtered_data[cols_to_display].to_excel(excel_buffer, index=False)
                        excel_data = excel_buffer.getvalue()
                        st.download_button(
                            label="📥 Download as Excel",
                            data=excel_data,
                            file_name="filtered_equipment_data.xlsx",
                            mime="application/vnd.ms-excel",
                        )
                else:
                    st.info("👆 Please select at least one column to display")
            else:
                st.warning("🔍 No matching records found. Try adjusting your filters.")

        with tab2:
            st.markdown('<h2 class="sub-header">Column-wise View and Analysis</h2>', unsafe_allow_html=True)
            
            if not filtered_data.empty:
                # Create column selector with improved visualization
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    selected_column = st.selectbox(
                        "Select column to analyze:",
                        options=filtered_data.columns.tolist()
                    )
                    
                    # Display selected column data
                    col_data = filtered_data[[selected_column]]
                    st.dataframe(
                        col_data,
                        use_container_width=True,
                        height=300
                    )
                
                with col2:
                    # Show visualizations based on column type - enhanced feature
                    if pd.api.types.is_numeric_dtype(filtered_data[selected_column]):
                        st.write("📊 Data Distribution:")
                        fig = px.histogram(
                            filtered_data, 
                            x=selected_column,
                            nbins=20,
                            title=f"Distribution of {selected_column}",
                            color_discrete_sequence=['#1E88E5']
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show basic statistics for numeric columns
                        st.write("📈 Basic Statistics:")
                        stats = col_data.describe()
                        st.dataframe(stats)
                    else:
                        # For categorical columns, show value counts with visualization
                        value_counts = filtered_data[selected_column].value_counts().reset_index()
                        value_counts.columns = [selected_column, 'Count']
                        
                        fig = px.bar(
                            value_counts,
                            y=selected_column,
                            x='Count',
                            title=f"Frequency of {selected_column} Values",
                            orientation='h',
                            color_discrete_sequence=['#1E88E5']
                        )
                        fig.update_layout(height=min(500, len(value_counts) * 25 + 100))
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show unique values count
                        st.metric("Unique Values", filtered_data[selected_column].nunique())

        with tab3:
            st.markdown('<h2 class="sub-header">Department-wise Equipment Distribution</h2>', unsafe_allow_html=True)

            # Count equipment per department with enhanced visualization
            dept_counts = data.iloc[:, 2].value_counts()
            
            # Allow user to limit the number of departments shown
            with st.expander("Chart Settings"):
                top_n_depts = st.slider(
                    "Number of departments to display:", 
                    min_value=5, 
                    max_value=len(dept_counts), 
                    value=min(10, len(dept_counts)),
                    step=1
                )
            
            # Get top N departments
            top_depts = dept_counts.nlargest(top_n_depts)
            
            # Create horizontal bar chart with improved design
            fig_dept = px.bar(
                y=top_depts.index,
                x=top_depts.values,
                labels={'x': 'Number of Equipment', 'y': 'Department'},
                title=f'Equipment Distribution Across Top {top_n_depts} Departments',
                orientation='h',
                color=top_depts.values,  # Color by count for better visualization
                color_continuous_scale='Blues',  # Blue color scale
                text=top_depts.values  # Display values on bars
            )
            fig_dept.update_layout(
                showlegend=False,
                height=max(400, top_n_depts * 30),  # Adjust height based on number of departments
                coloraxis_showscale=False  # Hide color scale
            )
            fig_dept.update_traces(texttemplate='%{text}', textposition='outside')
            st.plotly_chart(fig_dept, use_container_width=True)

            # Department equipment value analysis with interactive features
            if 'Cost' in data.columns:
                dept_value = data.groupby(data.iloc[:, 2])['Cost'].sum().sort_values(ascending=True)
                top_value_depts = dept_value.nlargest(top_n_depts)
                
                fig_value = px.bar(
                    y=top_value_depts.index,
                    x=top_value_depts.values,
                    labels={'x': 'Total Equipment Value', 'y': 'Department'},
                    title=f'Department-wise Equipment Value Distribution (Top {top_n_depts})',
                    orientation='h',
                    color=top_value_depts.values,
                    color_continuous_scale='Greens',
                    text=[f"₹{x:,.0f}" for x in top_value_depts.values]  # Format currency
                )
                fig_value.update_layout(
                    height=max(400, top_n_depts * 30),
                    coloraxis_showscale=False
                )
                fig_value.update_traces(textposition='outside')
                st.plotly_chart(fig_value, use_container_width=True)
                
                # Add a pie chart for department budget allocation - new visualization
                with st.expander("Department Budget Allocation", expanded=False):
                    fig_pie = px.pie(
                        values=top_value_depts.values,
                        names=top_value_depts.index,
                        title=f'Budget Allocation Across Top {top_n_depts} Departments',
                        hole=0.4,  # Create a donut chart
                        color_discrete_sequence=px.colors.sequential.Greens_r
                    )
                    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig_pie, use_container_width=True)

        with tab4:
            st.markdown('<h2 class="sub-header">Equipment Analytics and Distribution</h2>', unsafe_allow_html=True)

            # Create two columns for layout
            col1, col2 = st.columns(2)
            
            with col1:
                # Equipment type distribution - horizontal bar chart with enhanced visuals
                equipment_counts = data.iloc[:, 1].value_counts().head(15)
                fig_equip = px.bar(
                    y=equipment_counts.index,
                    x=equipment_counts.values,
                    labels={'x': 'Count', 'y': 'Equipment Type'},
                    title='Top 15 Most Common Equipment Types',
                    orientation='h',
                    color=equipment_counts.values,
                    color_continuous_scale='Purples',
                    text=equipment_counts.values
                )
                fig_equip.update_layout(
                    height=600,
                    coloraxis_showscale=False
                )
                fig_equip.update_traces(texttemplate='%{text}', textposition='outside')
                st.plotly_chart(fig_equip, use_container_width=True)
            
            with col2:
                # Measurement purpose distribution with enhanced visualization
                measure_counts = data.iloc[:, 14].value_counts().head(15)
                fig_measure = px.bar(
                    y=measure_counts.index,
                    x=measure_counts.values,
                    labels={'x': 'Count', 'y': 'Measurement Purpose'},
                    title='Top 15 Measurement Purposes',
                    orientation='h',
                    color=measure_counts.values,
                    color_continuous_scale='Oranges',
                    text=measure_counts.values
                )
                fig_measure.update_layout(
                    height=600,
                    coloraxis_showscale=False
                )
                fig_measure.update_traces(texttemplate='%{text}', textposition='outside')
                st.plotly_chart(fig_measure, use_container_width=True)

            # Add equipment age analysis if date information is available
            if 'Purchase Date' in data.columns:
                st.markdown('<h3 class="sub-header">Equipment Age Analysis</h3>', unsafe_allow_html=True)
                
                data['Purchase Date'] = pd.to_datetime(data['Purchase Date'], errors='coerce')
                data['Age'] = (pd.Timestamp.now() - data['Purchase Date']).dt.days / 365
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Age distribution histogram with box plot
                    fig_age = px.histogram(
                        data.dropna(subset=['Age']),
                        x='Age',
                        nbins=20,
                        title='Equipment Age Distribution (Years)',
                        color_discrete_sequence=['#4527A0'],
                        marginal="box"  # Add a box plot on the margin
                    )
                    st.plotly_chart(fig_age, use_container_width=True)
                
                with col2:
                    # Equipment value vs age scatter plot - new visualization
                    if 'Cost' in data.columns:
                        fig_value_age = px.scatter(
                            data.dropna(subset=['Age', 'Cost']),
                            x='Age',
                            y='Cost',
                            title='Equipment Value vs Age',
                            color='Age',
                            size='Cost',
                            hover_name=data.iloc[:, 1],  # Equipment name on hover
                            color_continuous_scale='Viridis'
                        )
                        st.plotly_chart(fig_value_age, use_container_width=True)

        # New tab for detailed equipment information
        with tab5:
            st.markdown('<h2 class="sub-header">Equipment Details</h2>', unsafe_allow_html=True)
            
            if not filtered_data.empty:
                # Create selection mechanism for individual equipment
                equipment_list = filtered_data.iloc[:, 1].tolist()
                selected_equipment = st.selectbox(
                    "Select equipment to view details:",
                    options=equipment_list
                )
                
                # Get the row for the selected equipment
                equipment_data = filtered_data[filtered_data.iloc[:, 1] == selected_equipment].iloc[0]
                
                # Display equipment details in a more attractive format
                st.markdown(f"""
                <div style="background-color: {'#1E1E1E' if dark_mode else '#f8f9fa'}; padding: 20px; border-radius: 10px; margin-top: 20px;">
                    <h3 style="color: {'#90CAF9' if dark_mode else '#1E88E5'};">{equipment_data.iloc[1]}</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid {'#444' if dark_mode else '#ddd'}; width: 30%;"><strong>Department:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid {'#444' if dark_mode else '#ddd'};">{equipment_data.iloc[2]}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; border-bottom: 1px solid {'#444' if dark_mode else '#ddd'};"><strong>Measurement Purpose:</strong></td>
                            <td style="padding: 8px; border-bottom: 1px solid {'#444' if dark_mode else '#ddd'};">{equipment_data.iloc[14]}</td>
                        </tr>
                """, unsafe_allow_html=True)
                
                # Add all other equipment details
                for i, col_name in enumerate(data.columns):
                    if i not in [1, 2, 14]:  # Skip already displayed fields
                        value = equipment_data.iloc[i]
                        if pd.notna(value):  # Only show non-NA values
                            st.markdown(f"""
                            <tr>
                                <td style="padding: 8px; border-bottom: 1px solid {'#444' if dark_mode else '#ddd'};"><strong>{col_name}:</strong></td>
                                <td style="padding: 8px; border-bottom: 1px solid {'#444' if dark_mode else '#ddd'};">{value}</td>
                            </tr>
                            """, unsafe_allow_html=True)
                
                st.markdown("</table></div>", unsafe_allow_html=True)
                
                # Add maintenance history section if available
                if 'Maintenance Date' in data.columns or 'Last Service Date' in data.columns:
                    with st.expander("Maintenance History", expanded=False):
                        st.info("Maintenance records would be displayed here")
            else:
                st.warning("No equipment found matching your search criteria")

        # Add summary statistics at the bottom with improved visualization
        st.markdown('<h2 class="sub-header">Dashboard Summary</h2>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            metric_card("Total Equipment", f"{len(filtered_data):,}")

        with col2:
            metric_card("Departments", f"{filtered_data.iloc[:, 2].nunique():,}")

        with col3:
            metric_card("Equipment Types", f"{filtered_data.iloc[:, 1].nunique():,}")
            
        with col4:
            # Calculate percentage of total equipment
            if not filtered_data.empty and not data.empty:
                percentage = (len(filtered_data) / len(data)) * 100
                metric_card("% of Total", f"{percentage:.1f}%")
            else:
                metric_card("% of Total", "0%")

        # Add footer with version info
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: gray; font-size: 0.8em;">
            Dhanalakshmi Srinivasan University Laboratory Equipment Search System - Version 1.0<br>
            Developed by DSU IT Department © 2025
        </div>
        """, unsafe_allow_html=True)

    except requests.exceptions.RequestException as e:
        st.error(f"Failed to download data from Google Sheets: {e}")
        st.info("Please check your internet connection and try again later.")
    except pd.errors.EmptyDataError:
        st.error("The downloaded file contains no data.")
    except pd.errors.ParserError:
        st.error("Unable to parse the data file. The file format may be incorrect.")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.info("Please contact the IT department for assistance.")
