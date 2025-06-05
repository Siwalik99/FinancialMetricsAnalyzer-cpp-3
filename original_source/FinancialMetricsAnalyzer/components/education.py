import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from utils.calculations import calculate_single_scenario_outcomes

def render_education():
    """Render the educational content page"""
    
    st.header("📚 Understanding Return vs Volatility")
    
    st.markdown("""
    This section explains the key concepts from Kris Abdelmessih's analysis of how volatility 
    affects investment returns. Each concept is illustrated with interactive examples.
    """)
    
    # Create tabs for different educational topics
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🧮 Arithmetic vs Geometric", 
        "🎯 Multiplicative Process", 
        "📊 Volatility Drag", 
        "🌳 Outcome Trees",
        "💡 Key Takeaways"
    ])
    
    with tab1:
        st.subheader("Arithmetic vs Geometric Returns")
        
        st.markdown("""
        **Arithmetic Return** is the simple average of returns:
        - If you have a 50% chance of earning 21% and 50% chance of earning 19%
        - Arithmetic mean = (21% + 19%) ÷ 2 = 20%
        
        **Geometric Return** accounts for compounding:
        - It answers: "What constant rate would get me from start to finish?"
        - Formula: (Final Value / Initial Value)^(1/periods) - 1
        """)
        
        # Interactive example
        st.markdown("**Interactive Example:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            return1 = st.slider("Year 1 Return (%)", -50, 100, 50, key="arith1") / 100
            return2 = st.slider("Year 2 Return (%)", -50, 100, -20, key="arith2") / 100
        
        with col2:
            # Calculate results
            arithmetic_mean = (return1 + return2) / 2
            terminal_value = (1 + return1) * (1 + return2)
            geometric_mean = terminal_value ** 0.5 - 1
            
            st.metric("Arithmetic Mean", f"{arithmetic_mean:.1%}")
            st.metric("Terminal Value", f"{terminal_value:.3f}x")
            st.metric("Geometric Mean (CAGR)", f"{geometric_mean:.1%}")
            st.metric("Difference", f"{arithmetic_mean - geometric_mean:.1%}")
        
        st.markdown(f"""
        **Explanation:**
        - Starting with $1, after Year 1: ${1 * (1 + return1):.3f}
        - After Year 2: ${terminal_value:.3f}
        - The geometric mean ({geometric_mean:.1%}) is what you actually earned per year on average
        - The arithmetic mean ({arithmetic_mean:.1%}) overstates your true compounded return
        """)
        
        if arithmetic_mean != geometric_mean:
            st.warning(f"""
            **Volatility Effect:** The {abs(arithmetic_mean - geometric_mean):.1%} difference between 
            arithmetic and geometric means is due to volatility. The more volatile the returns, 
            the larger this gap becomes.
            """)
    
    with tab2:
        st.subheader("Investing as a Multiplicative Process")
        
        st.markdown("""
        **Why Multiplication Matters:**
        
        When you reinvest returns, your wealth grows multiplicatively:
        - Year 1: $1.00 → $1.10 (10% gain)
        - Year 2: $1.10 → $1.21 (10% gain on $1.10)
        - Year 3: $1.21 → $1.33 (10% gain on $1.21)
        
        This is different from additive processes where you'd simply add 10¢ each year.
        """)
        
        # Comparison visualization
        years = st.slider("Number of years", 1, 20, 10, key="mult_years")
        annual_return = st.slider("Annual return (%)", 1, 20, 10, key="mult_return") / 100
        
        # Calculate multiplicative vs additive growth
        multiplicative_values = [(1 + annual_return) ** year for year in range(years + 1)]
        additive_values = [1 + annual_return * year for year in range(years + 1)]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=list(range(years + 1)),
            y=multiplicative_values,
            mode='lines+markers',
            name='Multiplicative (Compounding)',
            line=dict(color='blue', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=list(range(years + 1)),
            y=additive_values,
            mode='lines+markers',
            name='Additive (No Compounding)',
            line=dict(color='red', width=3, dash='dash')
        ))
        
        fig.update_layout(
            title='Multiplicative vs Additive Growth',
            xaxis_title='Years',
            yaxis_title='Value Multiple',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        final_mult = multiplicative_values[-1]
        final_add = additive_values[-1]
        
        st.markdown(f"""
        **After {years} years:**
        - Multiplicative (compounding): {final_mult:.2f}x your initial investment
        - Additive (no compounding): {final_add:.2f}x your initial investment
        - **Compounding bonus:** {final_mult - final_add:.2f}x additional wealth
        """)
    
    with tab3:
        st.subheader("Volatility Drag Effect")
        
        st.markdown("""
        **The Volatility Drag Phenomenon:**
        
        Even when two investments have the same arithmetic mean return, the one with higher 
        volatility will have a lower geometric mean return. This is called "volatility drag."
        """)
        
        # Demonstrate volatility drag
        st.markdown("**Example from the original article:**")
        
        scenarios = [
            {"name": "Low Volatility", "up": 0.21, "down": 0.19, "prob": 0.5},
            {"name": "High Volatility", "up": 1.00, "down": -0.60, "prob": 0.5}
        ]
        
        results_comparison = []
        
        for scenario in scenarios:
            arithmetic_mean = scenario["prob"] * scenario["up"] + (1 - scenario["prob"]) * scenario["down"]
            
            # 2-period outcomes
            outcomes = calculate_single_scenario_outcomes(scenario["up"], scenario["down"], 2)
            
            results_comparison.append({
                "Scenario": scenario["name"],
                "Up Return": f"{scenario['up']:.0%}",
                "Down Return": f"{scenario['down']:.0%}",
                "Arithmetic Mean": f"{arithmetic_mean:.1%}",
                "Geometric Mean (2-period)": f"{outcomes['geometric_mean']:.1%}",
                "Volatility Drag": f"{arithmetic_mean - outcomes['geometric_mean']:.1%}",
                "Probability of Loss": f"{outcomes['prob_loss']:.1%}"
            })
        
        st.dataframe(
            pd.DataFrame(results_comparison),
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("""
        **Key Observations:**
        1. Both scenarios have the same 20% arithmetic mean return
        2. The high volatility scenario has much lower geometric mean return
        3. Higher volatility dramatically increases the probability of loss
        4. The "volatility drag" is the cost of higher uncertainty
        """)
        
        st.info("""
        **Mathematical Insight:** For small returns, the volatility drag is approximately 
        equal to half the variance of returns. This is why diversification (which reduces 
        variance) can improve long-term returns even without changing expected returns.
        """)
    
    with tab4:
        st.subheader("Understanding Outcome Trees")
        
        st.markdown("""
        **Visualizing All Possible Paths:**
        
        For multi-period investments, we can map out every possible sequence of returns. 
        This helps us understand why median outcomes differ from mean outcomes.
        """)
        
        # Interactive outcome tree
        periods = st.selectbox("Number of periods", [1, 2, 3], index=1, key="tree_periods")
        up_ret = st.slider("Up return (%)", 10, 100, 50, key="tree_up") / 100
        down_ret = st.slider("Down return (%)", -80, 10, -20, key="tree_down") / 100
        
        outcomes = calculate_single_scenario_outcomes(up_ret, down_ret, periods)
        
        # Display results
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Summary Statistics:**")
            st.metric("Arithmetic Mean", f"{(up_ret + down_ret) / 2:.1%}")
            st.metric("Geometric Mean", f"{outcomes['geometric_mean']:.1%}")
            st.metric("Median CAGR", f"{outcomes['median_cagr']:.1%}")
            st.metric("Probability of Loss", f"{outcomes['prob_loss']:.1%}")
        
        with col2:
            st.markdown("**All Possible Outcomes:**")
            
            # Create outcomes table
            outcome_data = []
            for i, (sequence, terminal_val, cagr) in enumerate(zip(
                outcomes['sequences'], 
                outcomes['terminal_values'], 
                outcomes['cagr_values']
            )):
                path_description = " → ".join([f"{r:+.0%}" for r in sequence])
                outcome_data.append({
                    "Path": path_description,
                    "Terminal Value": f"{terminal_val:.3f}x",
                    "CAGR": f"{cagr:.1%}"
                })
            
            st.dataframe(
                pd.DataFrame(outcome_data),
                use_container_width=True,
                hide_index=True
            )
        
        st.markdown(f"""
        **Interpretation:**
        - There are {2**periods} equally likely outcomes
        - Median outcome: {outcomes['median_cagr']:.1%} CAGR
        - Best case: {outcomes['best_case']:.2f}x your money
        - Worst case: {outcomes['worst_case']:.2f}x your money
        """)
    
    with tab5:
        st.subheader("Key Takeaways")
        
        st.markdown("""
        ## 🎯 Essential Concepts
        
        ### 1. **Arithmetic vs Geometric Returns**
        - **Arithmetic**: Simple average of returns
        - **Geometric**: Compound annual growth rate (CAGR)
        - **Reality**: Geometric mean better represents your actual investment experience
        
        ### 2. **Volatility Drag**
        - Higher volatility reduces compound returns even with same arithmetic mean
        - Mathematical relationship: Volatility drag ≈ ½ × Variance
        - **Implication**: Reducing volatility can improve long-term returns
        
        ### 3. **Multiplicative Process**
        - Investing involves multiplying returns, not adding them
        - Small differences compound dramatically over time
        - **Order matters**: Sequence of returns affects final outcome
        
        ### 4. **Path Dependency**
        - In volatile investments, most paths may lose money
        - A few extremely positive outcomes skew the average upward
        - **Lived experience**: Usually closer to median than mean
        
        ### 5. **Risk Assessment**
        - Expected return is only half the story
        - Consider probability of loss, not just average gain
        - **Diversification**: Reduces risk without necessarily reducing expected return
        """)
        
        st.markdown("""
        ## 💼 Practical Applications
        
        ### Portfolio Construction
        - Seek investments with favorable risk-adjusted returns
        - Consider correlations to reduce overall portfolio volatility
        - Rebalance periodically to maintain target allocations
        
        ### Risk Management
        - Understand that high expected returns may come with high probability of loss
        - Consider your time horizon and risk tolerance
        - Don't chase arithmetic returns without considering volatility
        
        ### Performance Evaluation
        - Use geometric (compound) returns for multi-period analysis
        - Compare median outcomes, not just averages
        - Account for the impact of volatility on real returns
        """)
        
        st.success("""
        **Remember:** You only get one life to invest. While mathematical expectation matters, 
        your actual experience will be closer to the median outcome than the arithmetic mean. 
        Choose investments that balance growth potential with acceptable downside risk.
        """)
        
        # Final interactive example
        st.markdown("## 🧪 Final Challenge")
        st.markdown("Test your understanding with this scenario:")
        
        challenge_col1, challenge_col2 = st.columns(2)
        
        with challenge_col1:
            st.markdown("""
            **Investment A:**
            - 50% chance of +30% return
            - 50% chance of +10% return
            - Low volatility
            """)
            
            outcomes_a = calculate_single_scenario_outcomes(0.30, 0.10, 2)
            
            st.metric("Arithmetic Mean", "20%")
            st.metric("2-Period Geometric Mean", f"{outcomes_a['geometric_mean']:.1%}")
        
        with challenge_col2:
            st.markdown("""
            **Investment B:**
            - 50% chance of +80% return
            - 50% chance of -40% return  
            - High volatility
            """)
            
            outcomes_b = calculate_single_scenario_outcomes(0.80, -0.40, 2)
            
            st.metric("Arithmetic Mean", "20%")
            st.metric("2-Period Geometric Mean", f"{outcomes_b['geometric_mean']:.1%}")
        
        st.markdown(f"""
        **Question:** Both investments have the same 20% arithmetic mean return. 
        Which would you choose for a 2-year investment?
        
        **Answer:** Investment A provides a {outcomes_a['geometric_mean']:.1%} geometric return 
        vs {outcomes_b['geometric_mean']:.1%} for Investment B. The lower volatility of 
        Investment A results in better compounded returns despite identical arithmetic means.
        """)
