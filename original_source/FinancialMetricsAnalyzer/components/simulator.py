import streamlit as st
import numpy as np
import pandas as pd
from utils.calculations import simulate_investment_paths
from utils.visualizations import (
    create_simulation_histogram, 
    create_cagr_histogram, 
    create_path_visualization,
    create_percentile_chart
)

def render_simulator():
    """Render the Monte Carlo simulator page"""
    
    st.header("🎲 Monte Carlo Investment Simulator")
    
    st.markdown("""
    This simulator runs thousands of possible investment scenarios to show the range of 
    outcomes and help you understand the probability distribution of returns.
    """)
    
    # Simulation parameters
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🎯 Simulation Parameters")
        
        initial_investment = st.number_input(
            "Initial investment ($)",
            min_value=1000,
            max_value=1000000,
            value=10000,
            step=1000,
            help="Starting amount to invest"
        )
        
        up_return = st.slider(
            "Up scenario return (%)",
            min_value=-50,
            max_value=200,
            value=60,
            step=5,
            help="Return in favorable periods"
        ) / 100
        
        down_return = st.slider(
            "Down scenario return (%)",
            min_value=-90,
            max_value=50,
            value=-20,
            step=5,
            help="Return in unfavorable periods"
        ) / 100
        
        prob_up = st.slider(
            "Probability of up scenario (%)",
            min_value=1,
            max_value=99,
            value=50,
            step=1,
            help="Chance of favorable outcome each period"
        ) / 100
        
        investment_periods = st.slider(
            "Investment periods",
            min_value=1,
            max_value=30,
            value=10,
            step=1,
            help="Number of periods to simulate (e.g., years)"
        )
        
        num_simulations = st.selectbox(
            "Number of simulations",
            options=[1000, 5000, 10000, 25000, 50000],
            index=2,
            help="More simulations = more accurate results but slower computation"
        )
        
        # Calculate expected returns
        arithmetic_expected = prob_up * up_return + (1 - prob_up) * down_return
        
        st.markdown("**Expected Returns:**")
        st.metric("Arithmetic Mean", f"{arithmetic_expected:.1%}")
        
        if st.button("🚀 Run Simulation", type="primary"):
            st.session_state.run_simulation = True
            st.session_state.sim_params = {
                'initial_investment': initial_investment,
                'up_return': up_return,
                'down_return': down_return,
                'prob_up': prob_up,
                'investment_periods': investment_periods,
                'num_simulations': num_simulations
            }
    
    with col2:
        st.subheader("📊 Simulation Results")
        
        if hasattr(st.session_state, 'run_simulation') and st.session_state.run_simulation:
            
            # Run the simulation
            with st.spinner("Running Monte Carlo simulation..."):
                params = st.session_state.sim_params
                results = simulate_investment_paths(
                    initial_value=params['initial_investment'],
                    up_return=params['up_return'],
                    down_return=params['down_return'],
                    prob_up=params['prob_up'],
                    periods=params['investment_periods'],
                    num_simulations=params['num_simulations']
                )
            
            # Display key statistics
            st.markdown("**Key Statistics:**")
            
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            
            with stat_col1:
                st.metric(
                    "Mean Final Value",
                    f"${results['mean_final_value']:,.0f}",
                    help="Average outcome across all simulations"
                )
                st.metric(
                    "Median Final Value",
                    f"${results['median_final_value']:,.0f}",
                    help="Middle value (50th percentile)"
                )
            
            with stat_col2:
                st.metric(
                    "Probability of Loss",
                    f"{results['prob_loss']:.1%}",
                    help="Chance of ending with less than initial investment"
                )
                st.metric(
                    "Probability of Doubling",
                    f"{results['prob_double']:.1%}",
                    help="Chance of doubling your money"
                )
            
            with stat_col3:
                median_cagr = np.median(results['cagr_values'])
                st.metric(
                    "Median CAGR",
                    f"{median_cagr:.1%}",
                    delta=f"{median_cagr - results['arithmetic_expected']:.1%}",
                    help="Compound annual growth rate (50th percentile)"
                )
                st.metric(
                    "Standard Deviation",
                    f"${results['std_final_value']:,.0f}",
                    help="Measure of outcome variability"
                )
            
            # Visualization tabs
            tab1, tab2, tab3, tab4 = st.tabs(["💰 Final Values", "📈 CAGR Distribution", "🛤️ Investment Paths", "📊 Percentiles"])
            
            with tab1:
                st.plotly_chart(
                    create_simulation_histogram(results),
                    use_container_width=True
                )
                
                st.markdown(f"""
                **Distribution Analysis:**
                - The mean final value (${results['mean_final_value']:,.0f}) is typically higher than the median (${results['median_final_value']:,.0f})
                - This positive skew occurs because extreme positive outcomes have unlimited upside
                - {results['prob_loss']:.1%} of simulations result in a loss
                """)
            
            with tab2:
                st.plotly_chart(
                    create_cagr_histogram(results),
                    use_container_width=True
                )
                
                st.markdown(f"""
                **CAGR Analysis:**
                - Arithmetic expected return: {results['arithmetic_expected']:.1%}
                - Median CAGR: {median_cagr:.1%}
                - The difference ({results['arithmetic_expected'] - median_cagr:.1%}) represents volatility drag
                """)
            
            with tab3:
                num_paths_to_show = st.slider(
                    "Number of paths to display",
                    min_value=10,
                    max_value=min(500, len(results['all_paths'])),
                    value=100,
                    help="More paths show more variety but can clutter the chart"
                )
                
                st.plotly_chart(
                    create_path_visualization(results, num_paths_to_show),
                    use_container_width=True
                )
                
                st.markdown("""
                **Path Analysis:**
                - Each line represents one possible investment journey
                - The red line shows the median path across all simulations
                - Notice how paths can diverge dramatically due to compounding
                """)
            
            with tab4:
                st.plotly_chart(
                    create_percentile_chart(results),
                    use_container_width=True
                )
                
                # Percentile table
                st.markdown("**Outcome Percentiles:**")
                
                percentile_data = []
                for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]:
                    percentile_data.append({
                        'Percentile': f"{p}%",
                        'Final Value': f"${results['value_percentiles'][p]:,.0f}",
                        'CAGR': f"{results['cagr_percentiles'][p]:.1%}",
                        'Multiple': f"{results['value_percentiles'][p] / params['initial_investment']:.2f}x"
                    })
                
                st.dataframe(
                    pd.DataFrame(percentile_data),
                    use_container_width=True,
                    hide_index=True
                )
        
        else:
            st.info("👈 Set your parameters and click 'Run Simulation' to see results")
    
    # Educational content
    st.markdown("---")
    st.markdown("""
    ### 🎓 Understanding Monte Carlo Simulation
    
    **What it does:**
    - Runs thousands of random scenarios based on your parameters
    - Shows the full range of possible outcomes, not just averages
    - Helps quantify risk and understand probability distributions
    
    **Key insights:**
    - **Mean vs Median**: In volatile investments, mean outcomes are often higher than median due to positive skew
    - **Volatility Drag**: Higher volatility reduces median returns even with same arithmetic mean
    - **Path Dependency**: The order of returns matters in compounding scenarios
    - **Risk Assessment**: Probability of loss is as important as expected return
    """)
