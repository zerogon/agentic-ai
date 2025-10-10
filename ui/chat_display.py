import streamlit as st


def display_messages():
    """Display chat messages from session state."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Display SQL code if present (without expander to avoid nesting)
            if "code" in message and message["code"]:
                st.caption("📝 Generated SQL:")
                st.code(message["code"], language="sql")

            # Display Folium map if present
            if "folium_map" in message and message["folium_map"]:
                st.components.v1.html(
                    message["folium_map"],
                    height=600,
                    scrolling=True
                )

            # Display Plotly visualization if present
            if "chart_data" in message:
                st.plotly_chart(message["chart_data"], use_container_width=True)

            # Display table if present (skip if Folium map shown)
            if "table_data" in message and not message["table_data"].empty:
                # Only show table if not a map visualization
                if "folium_map" not in message:
                    st.dataframe(message["table_data"], use_container_width=True)
