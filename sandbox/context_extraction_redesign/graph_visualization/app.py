"""
Graph Visualization UI: Streamlit app for operational graph exploration.

UAT Checkpoint: User can load and explore the cascading failures graph.
"""

import streamlit as st
from st_link_analysis import st_link_analysis, NodeStyle, EdgeStyle
from graph_renderer import (
    load_graph_data,
    render_graph,
    get_node_styles,
    get_edge_styles,
    identify_bottleneck,
    calculate_quality_summary
)


def main():
    """Main Streamlit app."""
    
    st.set_page_config(
        page_title="Operational Graph Visualization",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔗 Operational Dependency Graph")
    st.markdown("**Visualizing cascading failures across Marketing → Sales → Production**")
    
    # Sidebar: Controls
    with st.sidebar:
        st.header("⚙️ Controls")
        
        # Load graph
        st.subheader("Load Graph")
        graph_file = st.selectbox(
            "Select graph:",
            ["example_cascading_failures_graph.json"]
        )
        
        # Layout options
        st.subheader("Layout")
        layout = st.selectbox(
            "Algorithm:",
            ["cose", "breadthfirst", "circle", "grid"],
            help="cose=force-directed, breadthfirst=hierarchical"
        )
        
        # Quality filter
        st.subheader("Filters")
        show_quality_issues = st.checkbox("Highlight quality issues", value=True)
        min_quality = st.slider(
            "Min quality threshold:",
            0.0, 1.0, 0.0, 0.1,
            help="Hide nodes above this quality"
        )
    
    # Load and render graph
    try:
        graph_data = load_graph_data(graph_file)
        
        # Display metadata
        metadata = graph_data.get("metadata", {})
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Entities", metadata.get("entities", 0))
        with col2:
            st.metric("Dependencies", metadata.get("dependencies", 0))
        with col3:
            st.metric("Quality Issues", metadata.get("quality_issues", 0))
        with col4:
            quality_summary = calculate_quality_summary(graph_data)
            st.metric("Avg Quality", f"{quality_summary['avg_quality']:.2f}")
        
        st.markdown("---")
        
        # Main visualization
        col_graph, col_details = st.columns([7, 3])
        
        with col_graph:
            st.subheader("📊 Graph Visualization")
            
            # Render graph
            elements = render_graph(graph_data)
            
            # Get styles
            node_styles = get_node_styles()
            edge_styles = get_edge_styles()
            
            # Display graph
            selected = st_link_analysis(
                elements,
                layout=layout,
                node_styles=node_styles,
                edge_styles=edge_styles,
                key="main_graph",
                height=600
            )
            
            # Show selection info
            if selected:
                st.info(f"Selected: {selected}")
        
        with col_details:
            st.subheader("📋 Details")
            
            # Quality analysis
            with st.expander("🎯 Quality Bottleneck", expanded=True):
                bottleneck = identify_bottleneck(graph_data)
                if bottleneck:
                    st.error(f"**{bottleneck['name']}**")
                    st.metric("Quality Score", f"{bottleneck['score']:.2f}")
                    st.caption("Lowest quality artifact in the chain")
            
            # Quality summary
            with st.expander("📊 Quality Summary"):
                summary = calculate_quality_summary(graph_data)
                st.metric("Average", f"{summary['avg_quality']:.2f}")
                st.metric("Minimum", f"{summary['min_quality']:.2f}")
                st.metric("Maximum", f"{summary['max_quality']:.2f}")
                st.metric("With Issues", summary['artifacts_with_issues'])
            
            # Error propagation
            with st.expander("⚠️ Error Propagation"):
                quality_analysis = graph_data.get("quality_analysis", {})
                chain = quality_analysis.get("error_propagation_chain", [])
                
                if chain:
                    st.markdown("**Cascading errors:**")
                    for item in chain:
                        st.markdown(
                            f"- {item['entity']}: "
                            f"quality={item['quality']:.1f}, "
                            f"error={item['error']}"
                        )
            
            # Root causes
            with st.expander("🔍 Root Causes"):
                quality_analysis = graph_data.get("quality_analysis", {})
                root_causes = quality_analysis.get("root_causes", [])
                
                if root_causes:
                    for rc in root_causes[:3]:  # Show top 3
                        st.markdown(f"**{rc['output']}**")
                        st.caption(f"Component: {rc['component']}")
                        st.caption(f"{rc['description']}")
                        st.markdown("---")
        
        # Bottom section: AI Pilot Opportunities
        st.markdown("---")
        st.subheader("🤖 AI Pilot Opportunities")
        
        opportunities = graph_data.get("ai_pilot_opportunities", [])
        if opportunities:
            cols = st.columns(len(opportunities))
            for idx, opp in enumerate(opportunities):
                with cols[idx]:
                    st.markdown(f"**{opp['target_output']}**")
                    st.caption(f"Root cause: {opp['root_cause']}")
                    st.info(opp['ai_solution_category'])
                    with st.expander("Recommendations"):
                        for rec in opp['recommendations']:
                            st.markdown(f"- {rec}")
        
    except FileNotFoundError as e:
        st.error(f"Graph file not found: {e}")
    except Exception as e:
        st.error(f"Error loading graph: {e}")
        st.exception(e)


if __name__ == "__main__":
    main()
