import streamlit as st
import numpy as np
import pandas as pd
from utils.calculations import calculate_volatility_scenarios, calculate_single_scenario_outcomes
from utils.visualizations import create_return_comparison_chart, create_outcome_tree_chart

def render_calculator():
    """Render the interactive calculator page"""
    
    st.header("📊 Interactive Return vs Volatility Calculator")
    
    st.markdown("""
    This calculator demonstrates how volatility affects investment returns while keeping 
    the arithmetic mean return constant. Adjust the parameters below to see the impact.
    """)
    
    # Create two columns for different calculation modes
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Single Scenario Analysis")
        
        # Input parameters for single scenario
        st.markdown("**Define your investment scenario:**")
        
        up_return = st.slider(
            "Up scenario return (%)",
            min_value=-50,
            max_value=200,
            value=100,
            step=5,
            help="Return in the favorable outcome"
        ) / 100
        
        down_return = st.slider(
            "Down scenario return (%)",
            min_value=-90,
            max_value=50,
            value=-60,
            step=5,
            help="Return in the unfavorable outcome"
        ) / 100
        
        prob_up = st.slider(
            "Probability of up scenario (%)",
            min_value=1,
            max_value=99,
            value=50,
            step=1,
            help="Probability of the favorable outcome occurring"
        ) / 100
        
        periods = st.selectbox(
            "Number of periods to analyze",
            options=[1, 2, 3, 4, 5],
            index=1,
            help="Number of investment periods (e.g., years)"
        )
        
        # Calculate single scenario outcomes
        outcomes = calculate_single_scenario_outcomes(up_return, down_return, periods)
        
        # Display results
        st.markdown("**Results:**")
        
        arithmetic_mean = prob_up * up_return + (1 - prob_up) * down_return
        
        metrics_col1, metrics_col2 = st.columns(2)
        
        with metrics_col1:
            st.metric(
                "Arithmetic Mean Return",
                f"{arithmetic_mean:.1%}",
                help="Simple average of possible returns"
            )
            st.metric(
                "Geometric Mean Return",
                f"{outcomes['geometric_mean']:.1%}",
                delta=f"{outcomes['geometric_mean'] - arithmetic_mean:.1%}",
                help="Compound annual growth rate"
            )
        
        with metrics_col2:
            st.metric(
                "Median CAGR",
                f"{outcomes['median_cagr']:.1%}",
                help="Middle value of all possible CAGRs"
            )
            st.metric(
                "Probability of Loss",
                f"{outcomes['prob_loss']:.1%}",
                help="Chance of losing money over the period"
            )
        
        # Show outcome tree for periods <= 3
        if periods <= 3:
            st.plotly_chart(
                create_outcome_tree_chart(outcomes),
                use_container_width=True
            )
        
        # Detailed breakdown
        with st.expander("📋 Detailed Breakdown"):
            st.markdown(f"""
            **Scenario Parameters:**
            - Up return: {up_return:.1%}
            - Down return: {down_return:.1%}
            - Probability of up: {prob_up:.1%}
            - Number of periods: {periods}
            
            **Calculated Metrics:**
            - Best case terminal value: {outcomes['best_case']:.3f}x
            - Worst case terminal value: {outcomes['worst_case']:.3f}x
            - Mean terminal value: {outcomes['mean_terminal']:.3f}x
            - Median terminal value: {outcomes['median_terminal']:.3f}x
            """)
    
    with col2:
        st.subheader("📈 Volatility Impact Analysis")
        
        # Input for volatility analysis
        st.markdown("**Compare different volatility levels:**")
        
        target_return = st.slider(
            "Target arithmetic mean return (%)",
            min_value=1,
            max_value=50,
            value=20,
            step=1,
            help="The arithmetic mean return to maintain across all scenarios"
        ) / 100
        
        max_volatility = st.slider(
            "Maximum volatility ratio",
            min_value=1.1,
            max_value=10.0,
            value=5.0,
            step=0.1,
            help="Highest ratio of up return to down return to analyze"
        )
        
        # Generate volatility scenarios
        volatility_ratios = np.linspace(1.1, max_volatility, 20)
        scenarios_df = calculate_volatility_scenarios(target_return, volatility_ratios)
        
        # Display volatility comparison chart
        st.plotly_chart(
            create_return_comparison_chart(scenarios_df),
            use_container_width=True
        )
        
        # Key insights
        st.markdown("**Key Insights:**")
        
        min_geometric = scenarios_df['geometric_mean_2period'].min()
        max_geometric = scenarios_df['geometric_mean_2period'].max()
        
        st.info(f"""
        📊 **Volatility Impact Summary:**
        - Arithmetic mean return: **{target_return:.1%}** (constant across all scenarios)
        - Geometric mean range: **{min_geometric:.1%}** to **{max_geometric:.1%}**
        - Maximum volatility drag: **{target_return - min_geometric:.1%}**
        
        As volatility increases, the geometric mean return decreases significantly while 
        the arithmetic mean stays constant. This demonstrates the "volatility drag" effect.
        """)
        
        # Scenarios table
        with st.expander("📊 Detailed Scenarios Table"):
            display_df = scenarios_df.copy()
            display_df['up_return'] = display_df['up_return'].apply(lambda x: f"{x:.1%}")
            display_df['down_return'] = display_df['down_return'].apply(lambda x: f"{x:.1%}")
            display_df['geometric_mean_2period'] = display_df['geometric_mean_2period'].apply(lambda x: f"{x:.1%}")
            display_df['median_return_2period'] = display_df['median_return_2period'].apply(lambda x: f"{x:.1%}")
            
            st.dataframe(
                display_df[['volatility_ratio', 'up_return', 'down_return', 
                           'geometric_mean_2period', 'median_return_2period']].round(3),
                column_config={
                    'volatility_ratio': 'Volatility Ratio',
                    'up_return': 'Up Return',
                    'down_return': 'Down Return',
                    'geometric_mean_2period': 'Geometric Mean',
                    'median_return_2period': 'Median Return'
                },
                use_container_width=True
            )
    
    # Educational callout
    st.markdown("---")
    st.markdown("""
    ### 💡 Key Takeaways
    
    1. **Volatility Drag**: Higher volatility reduces compound returns even when arithmetic mean stays constant
    2. **Multiplicative Process**: Investing involves multiplying returns, not adding them
    3. **Geometric vs Arithmetic**: Geometric mean better represents actual investment experience
    4. **Risk Assessment**: Consider both expected return AND volatility when evaluating investments
    """)
