import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
from scipy import stats

def calculate_arithmetic_return(returns: List[float]) -> float:
    """Calculate arithmetic mean return"""
    return np.mean(returns)

def calculate_geometric_return(returns: List[float]) -> float:
    """Calculate geometric mean return (CAGR)"""
    # Convert returns to multiplicative factors
    factors = [1 + r for r in returns]
    geometric_mean = np.prod(factors) ** (1/len(factors)) - 1
    return geometric_mean

def calculate_log_return(returns: List[float]) -> float:
    """Calculate log return (continuous compounding)"""
    # Convert returns to multiplicative factors and take log
    factors = [1 + r for r in returns]
    log_returns = [np.log(factor) for factor in factors]
    return np.mean(log_returns)

def simulate_investment_paths(
    initial_value: float,
    up_return: float,
    down_return: float,
    prob_up: float,
    periods: int,
    num_simulations: int = 10000
) -> Dict:
    """
    Simulate multiple investment paths using Monte Carlo
    
    Args:
        initial_value: Starting investment amount
        up_return: Return in up scenario (as decimal, e.g., 0.21 for 21%)
        down_return: Return in down scenario (as decimal, e.g., -0.19 for -19%)
        prob_up: Probability of up scenario
        periods: Number of investment periods
        num_simulations: Number of Monte Carlo simulations
    
    Returns:
        Dictionary with simulation results
    """
    
    # Run simulations
    final_values = []
    all_paths = []
    
    for _ in range(num_simulations):
        value = initial_value
        path = [value]
        
        for period in range(periods):
            # Generate random outcome
            if np.random.random() < prob_up:
                value *= (1 + up_return)
            else:
                value *= (1 + down_return)
            path.append(value)
        
        final_values.append(value)
        all_paths.append(path)
    
    # Calculate statistics
    final_values = np.array(final_values)
    cagr_values = (final_values / initial_value) ** (1/periods) - 1
    
    # Expected arithmetic return
    arithmetic_expected = prob_up * up_return + (1 - prob_up) * down_return
    
    # Calculate percentiles for final values
    percentiles = [1, 5, 10, 25, 50, 75, 90, 95, 99]
    value_percentiles = np.percentile(final_values, percentiles)
    cagr_percentiles = np.percentile(cagr_values, percentiles)
    
    results = {
        'final_values': final_values,
        'cagr_values': cagr_values,
        'all_paths': all_paths[:1000],  # Store first 1000 paths for visualization
        'arithmetic_expected': arithmetic_expected,
        'geometric_mean': np.median(cagr_values),
        'mean_final_value': np.mean(final_values),
        'median_final_value': np.median(final_values),
        'std_final_value': np.std(final_values),
        'value_percentiles': dict(zip(percentiles, value_percentiles)),
        'cagr_percentiles': dict(zip(percentiles, cagr_percentiles)),
        'prob_loss': np.sum(final_values < initial_value) / len(final_values),
        'prob_double': np.sum(final_values >= 2 * initial_value) / len(final_values)
    }
    
    return results

def calculate_volatility_scenarios(
    mean_return: float = 0.20,
    volatility_ratios: List[float] = None
) -> pd.DataFrame:
    """
    Calculate different volatility scenarios with same mean return
    
    Args:
        mean_return: Target arithmetic mean return
        volatility_ratios: List of volatility ratios (up_return / down_return factors)
    
    Returns:
        DataFrame with scenario analysis
    """
    
    if volatility_ratios is None:
        volatility_ratios = [1.1, 1.5, 2.0, 3.0, 4.0, 5.0]
    
    scenarios = []
    
    for ratio in volatility_ratios:
        # For a given mean return and volatility ratio, solve for up/down returns
        # Let up_return = r_up, down_return = r_down
        # Constraint 1: 0.5 * r_up + 0.5 * r_down = mean_return
        # Constraint 2: (1 + r_up) / (1 + r_down) = ratio
        
        # From constraint 1: r_down = 2 * mean_return - r_up
        # Substituting into constraint 2:
        # (1 + r_up) / (1 + 2 * mean_return - r_up) = ratio
        # Solving for r_up:
        
        denominator = ratio + 1
        r_up = (ratio * (1 + 2 * mean_return) - 1) / denominator
        r_down = 2 * mean_return - r_up
        
        # Calculate geometric return for 2 periods
        outcomes_2period = [
            (1 + r_up) * (1 + r_up),  # up, up
            (1 + r_up) * (1 + r_down),  # up, down
            (1 + r_down) * (1 + r_up),  # down, up
            (1 + r_down) * (1 + r_down)  # down, down
        ]
        
        geometric_2period = np.mean(outcomes_2period) ** 0.5 - 1
        median_2period = np.median(outcomes_2period) ** 0.5 - 1
        
        scenarios.append({
            'volatility_ratio': ratio,
            'up_return': r_up,
            'down_return': r_down,
            'arithmetic_mean': mean_return,
            'geometric_mean_2period': geometric_2period,
            'median_return_2period': median_2period,
            'terminal_wealth_up_up': outcomes_2period[0],
            'terminal_wealth_up_down': outcomes_2period[1],
            'terminal_wealth_down_down': outcomes_2period[3],
            'volatility_description': f"±{abs(r_up - mean_return):.1%}"
        })
    
    return pd.DataFrame(scenarios)

def calculate_single_scenario_outcomes(up_return: float, down_return: float, periods: int = 2) -> Dict:
    """
    Calculate all possible outcomes for a single scenario over multiple periods
    
    Args:
        up_return: Return in up scenario (as decimal)
        down_return: Return in down scenario (as decimal)  
        periods: Number of periods
    
    Returns:
        Dictionary with all outcomes and statistics
    """
    
    # Generate all possible sequences
    from itertools import product
    
    sequences = list(product([up_return, down_return], repeat=periods))
    outcomes = []
    
    for sequence in sequences:
        terminal_value = 1.0
        for return_rate in sequence:
            terminal_value *= (1 + return_rate)
        outcomes.append(terminal_value)
    
    outcomes = np.array(outcomes)
    cagr_values = outcomes ** (1/periods) - 1
    
    # Calculate statistics
    arithmetic_mean = 0.5 * up_return + 0.5 * down_return
    geometric_mean = np.mean(cagr_values)
    median_cagr = np.median(cagr_values)
    
    return {
        'sequences': sequences,
        'terminal_values': outcomes,
        'cagr_values': cagr_values,
        'arithmetic_mean': arithmetic_mean,
        'geometric_mean': geometric_mean,
        'median_cagr': median_cagr,
        'mean_terminal': np.mean(outcomes),
        'median_terminal': np.median(outcomes),
        'prob_loss': np.sum(outcomes < 1.0) / len(outcomes),
        'worst_case': np.min(outcomes),
        'best_case': np.max(outcomes)
    }
