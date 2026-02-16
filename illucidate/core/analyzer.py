"""
Autonomous Early Detection Signal Analyzer

This agent explores Victor Nivo data to find:
1. Early divergence signals between samples
2. Multi-modal correlations (OD + RLU + Temperature)
3. Temporal patterns that predict outcomes earlier than standard thresholds

It generates hundreds of candidate features and tests them systematically.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats
from scipy.signal import find_peaks
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import warnings
warnings.filterwarnings('ignore')


class EarlyDetectionAnalyzer:
    """Autonomous analyzer for finding early detection signals."""
    
    def __init__(self, data_df, sample_labels=None, verbose=True):
        """
        Args:
            data_df: Wide-format dataframe from parser
            sample_labels: Dict mapping well names to labels (e.g., {'A1': 'E.coli', 'A2': 'Blank'})
            verbose: Print progress
        """
        self.data = data_df
        self.sample_labels = sample_labels or {}
        self.verbose = verbose
        self.features = None
        self.results = []
        
    def log(self, msg):
        if self.verbose:
            print(msg)
    
    def analyze(self):
        """Run full autonomous analysis."""
        self.log("\n" + "="*80)
        self.log("AUTONOMOUS EARLY DETECTION ANALYSIS")
        self.log("="*80 + "\n")
        
        # Step 1: Generate all possible features
        self.log("Step 1: Generating features...")
        self.features = self._generate_features()
        self.log(f"  ✓ Generated {len(self.features.columns)-1} features from {len(self.data)} wells\n")
        
        # Step 2: Find early divergence signals
        self.log("Step 2: Finding early divergence signals...")
        divergence_signals = self._find_early_divergence()
        self.log(f"  ✓ Found {len(divergence_signals)} potential early indicators\n")
        
        # Step 3: Test temporal correlations
        self.log("Step 3: Testing cross-measurement correlations...")
        correlations = self._find_cross_correlations()
        self.log(f"  ✓ Found {len(correlations)} significant correlations\n")
        
        # Step 4: Identify optimal thresholds
        self.log("Step 4: Optimizing detection thresholds...")
        thresholds = self._optimize_thresholds()
        self.log(f"  ✓ Optimized {len(thresholds)} threshold combinations\n")
        
        # Compile results
        self.results = {
            'features': self.features,
            'early_divergence': divergence_signals,
            'correlations': correlations,
            'thresholds': thresholds
        }
        
        return self.results
    
    def _generate_features(self):
        """Generate hundreds of candidate features from raw data."""
        features_list = []
        
        # Get measurement types from column names
        measurement_types = set()
        for col in self.data.columns:
            if '_T' in col:
                measurement_type = col.split('_T')[0]
                measurement_types.add(measurement_type)
        
        measurement_types = list(measurement_types)
        
        # Get number of timepoints
        time_cols = [c for c in self.data.columns if 'Time_' in c and '_seconds' in c]
        n_timepoints = len(time_cols)
        
        for well_idx, row in self.data.iterrows():
            well_name = row['Well']
            feature_row = {'Well': well_name}
            
            if well_name in self.sample_labels:
                feature_row['Label'] = self.sample_labels[well_name]
            
            # For each measurement type
            for mtype in measurement_types:
                # Extract time series
                values = []
                for t_idx in range(n_timepoints):
                    col_name = f'{mtype}_T{t_idx}_sec'
                    if col_name in self.data.columns:
                        values.append(row[col_name])
                
                values = np.array(values)
                valid_mask = ~np.isnan(values)
                valid_values = values[valid_mask]
                
                if len(valid_values) < 5:
                    continue
                
                # ===== BASIC STATISTICS =====
                feature_row[f'{mtype}_mean'] = np.mean(valid_values)
                feature_row[f'{mtype}_std'] = np.std(valid_values)
                feature_row[f'{mtype}_max'] = np.max(valid_values)
                feature_row[f'{mtype}_min'] = np.min(valid_values)
                feature_row[f'{mtype}_range'] = np.ptp(valid_values)
                
                # ===== EARLY TIMEPOINT STATISTICS =====
                for early_n in [3, 5, 10, 15, 20]:
                    if early_n < len(valid_values):
                        early_vals = valid_values[:early_n]
                        feature_row[f'{mtype}_early{early_n}_mean'] = np.mean(early_vals)
                        feature_row[f'{mtype}_early{early_n}_max'] = np.max(early_vals)
                        feature_row[f'{mtype}_early{early_n}_slope'] = self._calculate_slope(early_vals)
                        feature_row[f'{mtype}_early{early_n}_var'] = np.var(early_vals)
                
                # ===== GROWTH CHARACTERISTICS =====
                # First derivative (rate of change)
                if len(valid_values) > 1:
                    deriv = np.diff(valid_values)
                    feature_row[f'{mtype}_max_growth_rate'] = np.max(deriv) if len(deriv) > 0 else 0
                    feature_row[f'{mtype}_mean_growth_rate'] = np.mean(deriv) if len(deriv) > 0 else 0
                    feature_row[f'{mtype}_growth_rate_std'] = np.std(deriv) if len(deriv) > 0 else 0
                    
                    # Time to max growth rate
                    if len(deriv) > 0:
                        max_rate_idx = np.argmax(deriv)
                        feature_row[f'{mtype}_time_to_max_rate'] = max_rate_idx
                
                # Second derivative (acceleration)
                if len(valid_values) > 2:
                    deriv2 = np.diff(np.diff(valid_values))
                    feature_row[f'{mtype}_max_acceleration'] = np.max(np.abs(deriv2)) if len(deriv2) > 0 else 0
                
                # ===== LAG PHASE DETECTION =====
                # Find when value first exceeds baseline + threshold
                baseline = np.mean(valid_values[:min(5, len(valid_values))])
                for threshold_factor in [1.1, 1.2, 1.5, 2.0]:
                    threshold = baseline * threshold_factor
                    exceed_idx = np.where(valid_values > threshold)[0]
                    if len(exceed_idx) > 0:
                        feature_row[f'{mtype}_time_to_{int(threshold_factor*10)}x'] = exceed_idx[0]
                    else:
                        feature_row[f'{mtype}_time_to_{int(threshold_factor*10)}x'] = n_timepoints
                
                # ===== CURVE SHAPE FEATURES =====
                # Area under curve (total signal)
                try:
                    feature_row[f'{mtype}_auc'] = np.trapezoid(valid_values)
                except AttributeError:
                    feature_row[f'{mtype}_auc'] = np.trapz(valid_values)  # Older numpy
                
                # Skewness and kurtosis
                if len(valid_values) > 3:
                    feature_row[f'{mtype}_skewness'] = stats.skew(valid_values)
                    feature_row[f'{mtype}_kurtosis'] = stats.kurtosis(valid_values)
                
                # Peak detection
                peaks, _ = find_peaks(valid_values, prominence=0.01)
                feature_row[f'{mtype}_n_peaks'] = len(peaks)
                if len(peaks) > 0:
                    feature_row[f'{mtype}_first_peak_time'] = peaks[0]
                    feature_row[f'{mtype}_first_peak_value'] = valid_values[peaks[0]]
            
            # ===== CROSS-MEASUREMENT FEATURES =====
            if len(measurement_types) >= 2:
                for i, mtype1 in enumerate(measurement_types):
                    for mtype2 in measurement_types[i+1:]:
                        # Get values
                        vals1 = [row[f'{mtype1}_T{t}_sec'] for t in range(n_timepoints) 
                                if f'{mtype1}_T{t}_sec' in row.index]
                        vals2 = [row[f'{mtype2}_T{t}_sec'] for t in range(n_timepoints) 
                                if f'{mtype2}_T{t}_sec' in row.index]
                        
                        vals1 = np.array([v for v in vals1 if not np.isnan(v)])
                        vals2 = np.array([v for v in vals2 if not np.isnan(v)])
                        
                        if len(vals1) > 3 and len(vals2) > 3:
                            min_len = min(len(vals1), len(vals2))
                            vals1 = vals1[:min_len]
                            vals2 = vals2[:min_len]
                            
                            # Ratio features
                            with np.errstate(divide='ignore', invalid='ignore'):
                                ratio = vals1 / vals2
                                ratio = ratio[np.isfinite(ratio)]
                                if len(ratio) > 0:
                                    feature_row[f'{mtype1}_div_{mtype2}_mean'] = np.mean(ratio)
                                    feature_row[f'{mtype1}_div_{mtype2}_early_mean'] = np.mean(ratio[:min(5, len(ratio))])
                                    feature_row[f'{mtype1}_div_{mtype2}_slope'] = self._calculate_slope(ratio)
                            
                            # Correlation
                            if len(vals1) == len(vals2):
                                corr, _ = stats.pearsonr(vals1, vals2)
                                feature_row[f'{mtype1}_vs_{mtype2}_corr'] = corr
            
            features_list.append(feature_row)
        
        return pd.DataFrame(features_list)
    
    def _calculate_slope(self, values):
        """Calculate linear regression slope."""
        if len(values) < 2:
            return 0
        x = np.arange(len(values))
        try:
            slope, _ = np.polyfit(x, values, 1)
            return slope
        except:
            return 0
    
    def _find_early_divergence(self):
        """Find features that show early divergence between labeled groups."""
        if len(self.sample_labels) == 0:
            self.log("    ⚠ No sample labels provided, skipping divergence analysis")
            return []
        
        divergence_signals = []
        
        # Get unique labels
        labels_in_data = self.features['Label'].unique() if 'Label' in self.features.columns else []
        
        if len(labels_in_data) < 2:
            self.log("    ⚠ Need at least 2 different labels for divergence analysis")
            return []
        
        # For each feature column
        feature_cols = [c for c in self.features.columns if c not in ['Well', 'Label']]
        
        for col in feature_cols:
            # Check if this is an "early" feature
            is_early = any(x in col for x in ['early', 'time_to'])
            
            if not is_early:
                continue
            
            # Group by label
            groups = self.features.groupby('Label')[col].apply(list)
            
            if len(groups) >= 2:
                # Perform t-test between groups
                group_vals = [g for g in groups.values if len(g) > 1]
                
                if len(group_vals) >= 2:
                    try:
                        statistic, pvalue = stats.ttest_ind(group_vals[0], group_vals[1], equal_var=False)
                        
                        if pvalue < 0.05:  # Significant difference
                            divergence_signals.append({
                                'feature': col,
                                'p_value': pvalue,
                                't_statistic': statistic,
                                'group1_mean': np.mean(group_vals[0]),
                                'group2_mean': np.mean(group_vals[1]),
                                'effect_size': abs(np.mean(group_vals[0]) - np.mean(group_vals[1])) / 
                                              np.sqrt((np.var(group_vals[0]) + np.var(group_vals[1])) / 2)
                            })
                    except:
                        pass
        
        # Sort by effect size
        divergence_signals.sort(key=lambda x: x['effect_size'], reverse=True)
        
        return divergence_signals
    
    def _find_cross_correlations(self):
        """Find significant correlations between different measurement types over time."""
        correlations = []
        
        # Look for columns with measurement ratios or cross-measurements
        cross_cols = [c for c in self.features.columns if '_div_' in c or '_vs_' in c or 'corr' in c]
        
        for col in cross_cols:
            values = self.features[col].dropna()
            
            if len(values) > 3:
                # Check variability - if all samples show similar pattern, it's informative
                cv = np.std(values) / np.mean(values) if np.mean(values) != 0 else 0
                
                correlations.append({
                    'feature': col,
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'cv': cv,
                    'min': np.min(values),
                    'max': np.max(values)
                })
        
        # Sort by coefficient of variation (higher = more discriminative)
        correlations.sort(key=lambda x: x['cv'], reverse=True)
        
        return correlations
    
    def _optimize_thresholds(self):
        """Find optimal threshold combinations for early detection."""
        if len(self.sample_labels) == 0:
            return []
        
        thresholds = []
        
        # Get early features
        early_features = [c for c in self.features.columns 
                         if any(x in c for x in ['early', 'time_to']) and c not in ['Well', 'Label']]
        
        for feature in early_features[:50]:  # Limit to top 50 to avoid too much computation
            values = self.features[feature].dropna()
            
            if len(values) < 5:
                continue
            
            # Try different threshold values
            for percentile in [25, 50, 75, 90]:
                threshold = np.percentile(values, percentile)
                
                thresholds.append({
                    'feature': feature,
                    'threshold': threshold,
                    'percentile': percentile
                })
        
        return thresholds
    
    def generate_report(self, output_path=None):
        """Generate a comprehensive analysis report."""
        report_lines = []
        
        report_lines.append("="*80)
        report_lines.append("EARLY DETECTION ANALYSIS REPORT")
        report_lines.append("="*80)
        report_lines.append("")
        
        # Dataset summary
        report_lines.append("DATASET SUMMARY")
        report_lines.append("-" * 80)
        report_lines.append(f"Total wells analyzed: {len(self.data)}")
        report_lines.append(f"Total features generated: {len(self.features.columns)-1}")
        report_lines.append("")
        
        # Early divergence signals
        if self.results.get('early_divergence'):
            report_lines.append("TOP EARLY DIVERGENCE SIGNALS")
            report_lines.append("-" * 80)
            
            for i, signal in enumerate(self.results['early_divergence'][:10], 1):
                report_lines.append(f"\n{i}. {signal['feature']}")
                report_lines.append(f"   P-value: {signal['p_value']:.4e}")
                report_lines.append(f"   Effect size: {signal['effect_size']:.3f}")
                report_lines.append(f"   Group 1 mean: {signal['group1_mean']:.3f}")
                report_lines.append(f"   Group 2 mean: {signal['group2_mean']:.3f}")
            
            report_lines.append("")
        
        # Cross-correlations
        if self.results.get('correlations'):
            report_lines.append("TOP CROSS-MEASUREMENT PATTERNS")
            report_lines.append("-" * 80)
            
            for i, corr in enumerate(self.results['correlations'][:10], 1):
                report_lines.append(f"\n{i}. {corr['feature']}")
                report_lines.append(f"   Mean: {corr['mean']:.3f}")
                report_lines.append(f"   Std: {corr['std']:.3f}")
                report_lines.append(f"   Range: [{corr['min']:.3f}, {corr['max']:.3f}]")
            
            report_lines.append("")
        
        report = "\n".join(report_lines)
        
        if output_path:
            with open(output_path, 'w') as f:
                f.write(report)
            self.log(f"\n✓ Report saved to: {output_path}")
        
        return report


if __name__ == "__main__":
    # Example usage
    print("Early Detection Analyzer - Ready to use")
    print("Usage:")
    print("  analyzer = EarlyDetectionAnalyzer(df, sample_labels={'A1': 'E.coli', 'B1': 'Blank'})")
    print("  results = analyzer.analyze()")
    print("  report = analyzer.generate_report('report.txt')")
