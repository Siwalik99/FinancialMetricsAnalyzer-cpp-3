import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List
import streamlit as st

def create_return_comparison_chart(scenarios_df: pd.DataFrame) -> go.Figure:
    """Create a chart comparing arithmetic vs geometric returns across volatility levels"""
    
    fig = go.Figure()
    
    # Arithmetic mean line (constant)
    fig.add_trace(go.Scatter(
        x=scenarios_df['volatility_ratio'],
        y=[scenarios_df['arithmetic_mean'].iloc[0]] * len(scenarios_df),
        mode='lines',
        name='Arithmetic Mean Return',
        line=dict(color='blue', width=3, dash='dash'),
        hovertemplate='Arithmetic Mean: %{y:.1%}<extra></extra>'
    ))
    
    # Geometric mean
    fig.add_trace(go.Scatter(
        x=scenarios_df['volatility_ratio'],
        y=scenarios_df['geometric_mean_2period'],
        mode='lines+markers',
        name='Geometric Mean Return (2-period)',
        line=dict(color='red', width=3),
        marker=dict(size=8),
        hovertemplate='Volatility Ratio: %{x}<br>Geometric Mean: %{y:.1%}<extra></extra>'
    ))
    
    # Median return
    fig.add_trace(go.Scatter(
        x=scenarios_df['volatility_ratio'],
        y=scenarios_df['median_return_2period'],
        mode='lines+markers',
        name='Median Return (2-period)',
        line=dict(color='green', width=3),
        marker=dict(size=8),
        hovertemplate='Volatility Ratio: %{x}<br>Median Return: %{y:.1%}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Impact of Volatility on Compounded Returns',
        xaxis_title='Volatility Ratio (Up Return / Down Return)',
        yaxis_title='Annualized Return',
        hovermode='x unified',
        legend=dict(x=0.02, y=0.98),
        height=500
    )
    
    fig.update_yaxes(tickformat='.1%')
    
    return fig

def create_simulation_histogram(results: Dict) -> go.Figure:
    """Create histogram of final values from Monte Carlo simulation"""
    
    fig = go.Figure()
    
    # Histogram of final values
    fig.add_trace(go.Histogram(
        x=results['final_values'],
        nbinsx=50,
        name='Final Values',
        opacity=0.7,
        hovertemplate='Value Range: %{x}<br>Count: %{y}<extra></extra>'
    ))
    
    # Add vertical lines for statistics
    fig.add_vline(
        x=results['mean_final_value'],
        line_dash="dash",
        line_color="red",
        annotation_text=f"Mean: ${results['mean_final_value']:,.0f}"
    )
    
    fig.add_vline(
        x=results['median_final_value'],
        line_dash="dash", 
        line_color="green",
        annotation_text=f"Median: ${results['median_final_value']:,.0f}"
    )
    
    fig.update_layout(
        title='Distribution of Final Investment Values',
        xaxis_title='Final Value ($)',
        yaxis_title='Frequency',
        height=400,
        showlegend=False
    )
    
    return fig

def create_cagr_histogram(results: Dict) -> go.Figure:
    """Create histogram of CAGR values from Monte Carlo simulation"""
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=results['cagr_values'] * 100,  # Convert to percentage
        nbinsx=50,
        name='CAGR Distribution',
        opacity=0.7,
        hovertemplate='CAGR Range: %{x:.1f}%<br>Count: %{y}<extra></extra>'
    ))
    
    # Add vertical lines for statistics
    fig.add_vline(
        x=results['arithmetic_expected'] * 100,
        line_dash="dash",
        line_color="blue",
        annotation_text=f"Arithmetic Expected: {results['arithmetic_expected']:.1%}"
    )
    
    fig.add_vline(
        x=np.median(results['cagr_values']) * 100,
        line_dash="dash",
        line_color="red", 
        annotation_text=f"Median CAGR: {np.median(results['cagr_values']):.1%}"
    )
    
    fig.update_layout(
        title='Distribution of Compound Annual Growth Rates (CAGR)',
        xaxis_title='CAGR (%)',
        yaxis_title='Frequency',
        height=400,
        showlegend=False
    )
    
    return fig

def create_path_visualization(results: Dict, num_paths: int = 100) -> go.Figure:
    """Create visualization of investment paths over time"""
    
    fig = go.Figure()
    
    # Sample random paths for visualization
    paths_to_show = np.random.choice(len(results['all_paths']), 
                                   min(num_paths, len(results['all_paths'])), 
                                   replace=False)
    
    for i, path_idx in enumerate(paths_to_show):
        path = results['all_paths'][path_idx]
        periods = list(range(len(path)))
        
        fig.add_trace(go.Scatter(
            x=periods,
            y=path,
            mode='lines',
            line=dict(width=1, color='rgba(100,100,100,0.3)'),
            showlegend=False,
            hovertemplate='Period: %{x}<br>Value: $%{y:,.0f}<extra></extra>'
        ))
    
    # Add median path
    median_path = np.median(np.array(results['all_paths']), axis=0)
    periods = list(range(len(median_path)))
    
    fig.add_trace(go.Scatter(
        x=periods,
        y=median_path,
        mode='lines',
        line=dict(width=4, color='red'),
        name='Median Path',
        hovertemplate='Period: %{x}<br>Median Value: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f'Investment Paths Over Time ({num_paths} sample paths)',
        xaxis_title='Period',
        yaxis_title='Investment Value ($)',
        height=500,
        hovermode='x unified'
    )
    
    return fig

def create_outcome_tree_chart(outcomes_data: Dict) -> go.Figure:
    """Create a tree chart showing all possible outcomes for a simple scenario"""
    
    sequences = outcomes_data['sequences']
    terminal_values = outcomes_data['terminal_values']
    
    # Create a simple bar chart of outcomes
    outcome_labels = []
    for i, seq in enumerate(sequences):
        label = ""
        for return_val in seq:
            if return_val > 0:
                label += "↑ "
            else:
                label += "↓ "
        outcome_labels.append(label.strip())
    
    fig = go.Figure()
    
    colors = ['green' if val >= 1.0 else 'red' for val in terminal_values]
    
    fig.add_trace(go.Bar(
        x=outcome_labels,
        y=terminal_values,
        marker_color=colors,
        opacity=0.7,
        hovertemplate='Sequence: %{x}<br>Terminal Value: %{y:.3f}<br>Return: %{customdata:.1%}<extra></extra>',
        customdata=(terminal_values - 1)
    ))
    
    # Add horizontal line at break-even
    fig.add_hline(y=1.0, line_dash="dash", line_color="black", 
                  annotation_text="Break-even")
    
    fig.update_layout(
        title='All Possible Outcomes Tree',
        xaxis_title='Outcome Sequence (↑ = Up, ↓ = Down)',
        yaxis_title='Terminal Wealth (Multiple of Initial)',
        height=400,
        showlegend=False
    )
    
    return fig

def create_percentile_chart(results: Dict) -> go.Figure:
    """Create a chart showing percentile distribution of outcomes"""
    
    percentiles = list(results['value_percentiles'].keys())
    values = list(results['value_percentiles'].values())
    cagr_values = list(results['cagr_percentiles'].values())
    
    fig = go.Figure()
    
    # Final values
    fig.add_trace(go.Scatter(
        x=percentiles,
        y=values,
        mode='lines+markers',
        name='Final Values ($)',
        yaxis='y1',
        line=dict(color='blue'),
        hovertemplate='Percentile: %{x}%<br>Value: $%{y:,.0f}<extra></extra>'
    ))
    
    # CAGR values on secondary axis
    fig.add_trace(go.Scatter(
        x=percentiles,
        y=[v * 100 for v in cagr_values],  # Convert to percentage
        mode='lines+markers',
        name='CAGR (%)',
        yaxis='y2',
        line=dict(color='red'),
        hovertemplate='Percentile: %{x}%<br>CAGR: %{y:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title='Outcome Percentiles from Monte Carlo Simulation',
        xaxis_title='Percentile',
        yaxis=dict(title='Final Value ($)', side='left', color='blue'),
        yaxis2=dict(title='CAGR (%)', side='right', overlaying='y', color='red'),
        height=500,
        hovermode='x unified'
    )
    
    return fig
