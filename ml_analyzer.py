"""
ML-based Business Rules Discovery and Prediction Engine
Uses Decision Tree, Random Forest, and Apriori algorithm
"""
import pandas as pd
import numpy as np
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Try to import Apriori (mlxtend), fallback if not available
try:
    from mlxtend.frequent_patterns import apriori, association_rules
    APRIORI_AVAILABLE = True
except ImportError:
    APRIORI_AVAILABLE = False


class MLBusinessRulesEngine:
    """ML-based Business Rules Discovery Engine"""
    
    def __init__(self):
        self.decision_tree = None
        self.random_forest = None
        self.label_encoders = {}
        self.feature_columns = []
        self.target_column = None
        self.model_type = None  # 'classification' or 'regression'
        
    def identify_target_column(self, df: pd.DataFrame, domain: str = "HR") -> Optional[str]:
        """
        Identify the target column for prediction
        For HR domain, look for: risk, risk_level, attrition, performance_score, status
        """
        target_keywords = ['risk', 'risk_level', 'attrition', 'attrition_flag', 'churn', 
                          'performance_score', 'performance_rating', 'employee_status', 
                          'status', 'warning', 'outcome']
        
        columns_lower = [col.lower() for col in df.columns]
        
        for keyword in target_keywords:
            for i, col_lower in enumerate(columns_lower):
                if keyword in col_lower:
                    # Check if it's not an ID column
                    if 'id' not in col_lower:
                        return df.columns[i]
        
        return None
    
    def prepare_features(self, df: pd.DataFrame, target_col: str) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare features and target for ML models
        Handles numerical and categorical features
        """
        # Separate features and target
        feature_df = df.drop(columns=[target_col]).copy()
        target_series = df[target_col].copy()
        
        # Store feature column names
        self.feature_columns = feature_df.columns.tolist()
        
        # Handle categorical features
        feature_df_encoded = feature_df.copy()
        for col in feature_df.columns:
            if feature_df[col].dtype == 'object' or feature_df[col].dtype.name == 'category':
                le = LabelEncoder()
                feature_df_encoded[col] = le.fit_transform(feature_df[col].astype(str).fillna('unknown'))
                self.label_encoders[col] = le
        
        # Handle numerical features - fill missing values with median
        for col in feature_df_encoded.select_dtypes(include=[np.number]).columns:
            feature_df_encoded[col] = feature_df_encoded[col].fillna(feature_df_encoded[col].median())
        
        # Encode target if categorical
        target_encoded = target_series.copy()
        if target_series.dtype == 'object':
            le_target = LabelEncoder()
            target_encoded = le_target.fit_transform(target_series.astype(str).fillna('unknown'))
            self.label_encoders[target_col] = le_target
            self.model_type = 'classification'
        else:
            self.model_type = 'regression'
        
        return feature_df_encoded, pd.Series(target_encoded)
    
    def extract_decision_tree_rules(self, tree, feature_names: List[str], target_classes: List[str] = None) -> List[Dict]:
        """
        Extract human-readable IF-ELSE rules from Decision Tree
        """
        rules = []
        tree_ = tree.tree_
        feature_name = [
            feature_names[i] if i != -2 else "undefined!"
            for i in tree_.feature
        ]
        
        def recurse(node, depth, parent_rule=""):
            indent = "  " * depth
            if tree_.feature[node] != -2:
                name = feature_name[node]
                threshold = tree_.threshold[node]
                rule = f"{name} <= {threshold:.2f}"
                if parent_rule:
                    rule = f"{parent_rule} AND {rule}"
                
                recurse(tree_.children_left[node], depth + 1, rule)
                
                rule = f"{name} > {threshold:.2f}"
                if parent_rule:
                    rule = f"{parent_rule} AND {rule}"
                recurse(tree_.children_right[node], depth + 1, rule)
            else:
                # Leaf node
                value = tree_.value[node][0]
                if self.model_type == 'classification':
                    class_idx = np.argmax(value)
                    class_name = target_classes[class_idx] if target_classes else str(class_idx)
                    confidence = value[class_idx] / np.sum(value)
                    rules.append({
                        "rule": f"IF {parent_rule} THEN {self.target_column} = {class_name}",
                        "description": f"If {parent_rule}, then predict {class_name} (confidence: {confidence:.2%})",
                        "confidence": confidence,
                        "support": int(np.sum(value))
                    })
                else:
                    predicted_value = value[0][0]
                    rules.append({
                        "rule": f"IF {parent_rule} THEN {self.target_column} ≈ {predicted_value:.2f}",
                        "description": f"If {parent_rule}, then predict {self.target_column} ≈ {predicted_value:.2f}",
                        "predicted_value": predicted_value,
                        "support": int(np.sum(value))
                    })
        
        recurse(0, 0)
        return rules[:20]  # Limit to top 20 rules for readability
    
    def discover_business_rules(self, df: pd.DataFrame, domain: str = "HR") -> Dict[str, Any]:
        """
        Discover business rules using Decision Tree and Random Forest
        """
        # Identify target column
        target_col = self.identify_target_column(df, domain)
        if target_col is None:
            # If no target column, create a synthetic one based on common patterns
            # For HR, we can create a risk_level based on attendance, late_days, etc.
            return self._create_synthetic_target_rules(df, domain)
        
        self.target_column = target_col
        
        # Prepare data
        try:
            X, y = self.prepare_features(df, target_col)
            
            # Skip if too few samples
            if len(X) < 10:
                return {
                    "rules": [],
                    "feature_importance": {},
                    "message": "Insufficient data for ML analysis (need at least 10 samples)"
                }
            
            # Train Decision Tree
            if self.model_type == 'classification':
                self.decision_tree = DecisionTreeClassifier(max_depth=5, min_samples_split=10)
            else:
                self.decision_tree = DecisionTreeRegressor(max_depth=5, min_samples_split=10)
            
            self.decision_tree.fit(X, y)
            
            # Extract rules from Decision Tree
            target_classes = None
            if self.model_type == 'classification' and target_col in self.label_encoders:
                target_classes = list(self.label_encoders[target_col].classes_)
            
            tree_rules = self.extract_decision_tree_rules(
                self.decision_tree, 
                self.feature_columns,
                target_classes
            )
            
            # Train Random Forest for feature importance
            if self.model_type == 'classification':
                self.random_forest = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
            else:
                self.random_forest = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
            
            self.random_forest.fit(X, y)
            
            # Get feature importance
            feature_importance = dict(zip(
                self.feature_columns,
                self.random_forest.feature_importances_
            ))
            # Sort by importance and convert to percentages
            feature_importance = {
                k: float(v * 100) 
                for k, v in sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
            }
            
            # Store feature importance for predictions
            self.feature_importance = feature_importance
            
            return {
                "rules": tree_rules[:15],  # Top 15 rules
                "feature_importance": feature_importance,
                "target_column": target_col,
                "model_type": self.model_type
            }
            
        except Exception as e:
            return {
                "rules": [],
                "feature_importance": {},
                "message": f"Error in ML analysis: {str(e)}"
            }
    
    def _create_synthetic_target_rules(self, df: pd.DataFrame, domain: str) -> Dict[str, Any]:
        """
        Create business rules when no explicit target column exists
        Generate rules based on HR domain patterns
        """
        rules = []
        feature_importance = {}
        
        # Look for common HR patterns
        attendance_col = None
        late_days_col = None
        leave_days_col = None
        performance_col = None
        
        cols_lower = {col.lower(): col for col in df.columns}
        
        for keyword, col_key in [
            ('attendance', 'attendance'), ('late_days', 'late'), 
            ('leave_days', 'leave'), ('performance', 'performance')
        ]:
            for lower_col, orig_col in cols_lower.items():
                if col_key in lower_col and 'id' not in lower_col:
                    if keyword == 'attendance' and attendance_col is None:
                        attendance_col = orig_col
                    elif keyword == 'late_days' and late_days_col is None:
                        late_days_col = orig_col
                    elif keyword == 'leave_days' and leave_days_col is None:
                        leave_days_col = orig_col
                    elif keyword == 'performance' and performance_col is None:
                        performance_col = orig_col
        
        # Generate simple threshold-based rules
        if attendance_col and df[attendance_col].dtype in [np.int64, np.float64]:
            threshold = df[attendance_col].quantile(0.25)  # 25th percentile
            rules.append({
                "rule": f"IF {attendance_col} < {threshold:.1f} THEN RISK = HIGH",
                "description": f"Employees with {attendance_col} below {threshold:.1f} are at high risk",
                "confidence": 0.75
            })
            feature_importance[attendance_col] = 35.0
        
        if late_days_col and df[late_days_col].dtype in [np.int64, np.float64]:
            threshold = df[late_days_col].quantile(0.75)  # 75th percentile
            rules.append({
                "rule": f"IF {late_days_col} > {threshold:.1f} THEN RISK = HIGH",
                "description": f"Employees with {late_days_col} above {threshold:.1f} are at high risk",
                "confidence": 0.70
            })
            feature_importance[late_days_col] = 30.0
        
        if leave_days_col and df[leave_days_col].dtype in [np.int64, np.float64]:
            threshold = df[leave_days_col].quantile(0.75)
            rules.append({
                "rule": f"IF {leave_days_col} > {threshold:.1f} THEN REVIEW_REQUIRED = TRUE",
                "description": f"Employees with {leave_days_col} above {threshold:.1f} require HR review",
                "confidence": 0.65
            })
            feature_importance[leave_days_col] = 25.0
        
        return {
            "rules": rules,
            "feature_importance": feature_importance,
            "target_column": None,
            "model_type": "synthetic"
        }
    
    def predict(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict outcome for new input data
        """
        if self.decision_tree is None or self.random_forest is None:
            return {
                "error": "Model not trained. Please analyze a dataset first."
            }
        
        try:
            # Prepare input features
            input_df = pd.DataFrame([input_data])
            
            # Encode categorical features
            input_encoded = input_df.copy()
            for col in self.feature_columns:
                if col in input_encoded.columns:
                    if col in self.label_encoders:
                        # Encode categorical
                        try:
                            input_encoded[col] = self.label_encoders[col].transform(
                                input_encoded[col].astype(str).fillna('unknown')
                            )
                        except:
                            input_encoded[col] = 0  # Default value
                    else:
                        # Fill numerical missing values
                        if input_encoded[col].isnull().any():
                            input_encoded[col] = input_encoded[col].fillna(0)
                else:
                    # Missing feature, use default
                    input_encoded[col] = 0
            
            # Ensure all features are present and in correct order
            input_features = input_encoded[self.feature_columns].values
            
            # Make predictions
            dt_pred = self.decision_tree.predict(input_features)[0]
            rf_pred = self.random_forest.predict(input_features)[0]
            rf_proba = None
            
            if self.model_type == 'classification':
                rf_proba = self.random_forest.predict_proba(input_features)[0]
                max_proba_idx = np.argmax(rf_proba)
                
                # Decode predictions
                if self.target_column in self.label_encoders:
                    dt_pred_decoded = self.label_encoders[self.target_column].inverse_transform([dt_pred])[0]
                    rf_pred_decoded = self.label_encoders[self.target_column].inverse_transform([rf_pred])[0]
                    confidence = float(rf_proba[max_proba_idx])
                else:
                    dt_pred_decoded = str(dt_pred)
                    rf_pred_decoded = str(rf_pred)
                    confidence = float(rf_proba[max_proba_idx]) if rf_proba is not None else 0.5
                
                predicted_outcome = rf_pred_decoded
            else:
                dt_pred_decoded = float(dt_pred)
                rf_pred_decoded = float(rf_pred)
                predicted_outcome = rf_pred_decoded
                confidence = 0.8  # Default confidence for regression
            
            # Generate explanation
            explanation = self._generate_explanation(input_data, predicted_outcome, confidence)
            
            return {
                "predicted_outcome": str(predicted_outcome),
                "confidence": confidence,
                "explanation": explanation,
                "decision_tree_prediction": str(dt_pred_decoded),
                "random_forest_prediction": str(rf_pred_decoded)
            }
            
        except Exception as e:
            return {
                "error": f"Prediction error: {str(e)}",
                "details": "Please ensure all required features are provided with correct data types"
            }
    
    def _generate_explanation(self, input_data: Dict, predicted_outcome: Any, confidence: float) -> str:
        """
        Generate human-readable explanation for prediction
        """
        explanation_parts = []
        
        # Analyze input features
        risk_factors = []
        positive_factors = []
        
        for feature, value in input_data.items():
            if feature in self.feature_columns:
                # Simple heuristic explanations
                if 'attendance' in feature.lower() and isinstance(value, (int, float)):
                    if value < 75:
                        risk_factors.append(f"low {feature} ({value})")
                    else:
                        positive_factors.append(f"good {feature} ({value})")
                
                if 'late' in feature.lower() and isinstance(value, (int, float)):
                    if value > 5:
                        risk_factors.append(f"high {feature} ({value})")
                
                if 'leave' in feature.lower() and isinstance(value, (int, float)):
                    if value > 10:
                        risk_factors.append(f"high {feature} ({value})")
        
        if risk_factors:
            explanation_parts.append(f"Employee shows {', '.join(risk_factors)}")
        
        if positive_factors:
            explanation_parts.append(f"Positive indicators: {', '.join(positive_factors)}")
        
        if not explanation_parts:
            explanation_parts.append("Based on the provided employee data")
        
        explanation_parts.append(f"predicted outcome is '{predicted_outcome}' with {confidence:.1%} confidence")
        
        return ". ".join(explanation_parts) + "."


def discover_apriori_patterns(df: pd.DataFrame, min_support: float = 0.1) -> List[Dict]:
    """
    Discover hidden patterns using Apriori algorithm
    """
    if not APRIORI_AVAILABLE:
        return []
    
    try:
        # Convert dataframe to binary format for Apriori
        # Select only categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        if len(categorical_cols) < 2:
            return []
        
        # Create binary matrix
        df_binary = pd.get_dummies(df[categorical_cols], prefix=categorical_cols)
        
        # Apply Apriori
        frequent_itemsets = apriori(df_binary, min_support=min_support, use_colnames=True)
        
        if len(frequent_itemsets) == 0:
            return []
        
        # Generate association rules
        rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
        
        patterns = []
        for idx, row in rules.head(10).iterrows():
            antecedents = list(row['antecedents'])
            consequents = list(row['consequents'])
            
            patterns.append({
                "pattern": f"{' AND '.join(antecedents)} → {', '.join(consequents)}",
                "support": float(row['support']),
                "confidence": float(row['confidence']),
                "description": f"When {', '.join(antecedents)}, then {', '.join(consequents)} (confidence: {row['confidence']:.1%})"
            })
        
        return patterns
        
    except Exception as e:
        # Apriori may fail on some datasets, return empty list
        return []

