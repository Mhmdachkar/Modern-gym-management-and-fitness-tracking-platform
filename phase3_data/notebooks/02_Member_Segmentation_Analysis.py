# PHASE 3: Member Segmentation Analysis
# Step 11: Segment members by frequency, class types, subscription duration

"""
This script performs comprehensive member segmentation analysis for a fitness service.
It analyzes members based on:
- Visit frequency and patterns
- Class type preferences
- Subscription duration and value
- RFM (Recency, Frequency, Monetary) analysis
- Demographic characteristics

Designed for Google Colab with clean, modular code structure.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('default')
sns.set_palette("husl")

# Set random seed for reproducibility
np.random.seed(42)

class MemberSegmentationAnalyzer:
    """
    Comprehensive member segmentation analysis class.
    Handles data loading, preprocessing, segmentation, and visualization.
    """
    
    def __init__(self):
        """Initialize the analyzer with empty dataframes."""
        self.members_df = None
        self.sessions_df = None
        self.subscriptions_df = None
        self.packages_df = None
        self.coaches_df = None
        self.member_features = None
        self.segments = None
        self.auto_synthesize_if_missing = True
        
    def load_data(self):
        """
        Load all required datasets for member segmentation.
        Assumes CSV files are in the same directory or accessible via relative paths.
        """
        print("🔄 Loading datasets...")
        
        try:
            # Load core datasets (robust paths for Colab and repo layout)
            def try_read(paths):
                for p in paths:
                    try:
                        return pd.read_csv(p)
                    except Exception:
                        continue
                raise FileNotFoundError(paths[-1])

            self.members_df = try_read([
                'members.csv', '../data/members.csv', '../../phase2_data/data/members.csv', '../../phase2_data/members.csv'
            ])
            self.sessions_df = try_read([
                'sessions.csv', '../data/sessions.csv', '../../phase2_data/data/sessions.csv', '../../phase2_data/sessions.csv'
            ])
            self.subscriptions_df = try_read([
                'subscriptions.csv', '../data/subscriptions.csv', '../../phase2_data/data/subscriptions.csv', '../../phase2_data/subscriptions.csv'
            ])
            self.packages_df = try_read([
                'packages.csv', '../data/packages.csv', '../../phase2_data/data/packages.csv', '../../phase2_data/packages.csv'
            ])
            # Optional datasets
            try:
                self.coaches_df = try_read([
                    'coaches.csv', '../data/coaches.csv', '../../phase2_data/data/coaches.csv', '../../phase2_data/coaches.csv'
                ])
            except Exception:
                self.coaches_df = pd.DataFrame()
            try:
                self.feedback_df = try_read([
                    'feedback_data.csv', '../data/feedback_data.csv', '../../phase3_data/data/feedback_data.csv'
                ])
            except Exception:
                self.feedback_df = pd.DataFrame()
            
            print("✅ All datasets loaded successfully!")
            print(f"   Members: {len(self.members_df)} records")
            print(f"   Sessions: {len(self.sessions_df)} records")
            print(f"   Subscriptions: {len(self.subscriptions_df)} records")
            print(f"   Packages: {len(self.packages_df)} records")
            if isinstance(self.coaches_df, pd.DataFrame) and not self.coaches_df.empty:
                print(f"   Coaches: {len(self.coaches_df)} records")
            if hasattr(self, 'feedback_df') and isinstance(self.feedback_df, pd.DataFrame) and not self.feedback_df.empty:
                print(f"   Feedback: {len(self.feedback_df)} records")
            
        except FileNotFoundError as e:
            print(f"❌ Error loading data: {e}")
            print("Please ensure all CSV files are in the current directory.")
            return False
            
        return True

    def _ensure_dir(self, path):
        import os
        os.makedirs(path, exist_ok=True)

    def validate_or_synthesize_data(self):
        """Ensure CSVs contain required columns and at least minimal rows; synthesize if allowed."""
        print("\n🧪 Validating required columns and minimal rows...")
        from datetime import timedelta
        import numpy as np
        import pandas as pd
        import os

        out_dir_candidates = ["../data", "./data", "."]
        out_dir = next((d for d in out_dir_candidates if os.path.isdir(d)), ".")

        def synth_members(n=20):
            today = datetime.now()
            df = pd.DataFrame({
                'id': np.arange(1, n+1),
                'name': [f'Member {i}' for i in range(1, n+1)],
                'email': [f'member{i}@example.com' for i in range(1, n+1)],
                'created_at': [today - timedelta(days=int(i*5)) for i in range(1, n+1)],
                'dob': [today - timedelta(days=int(25*365 + (i%20)*30)) for i in range(1, n+1)],
                'weight': np.random.normal(75, 10, n).round(1),
                'height': np.random.normal(170, 8, n).round(1),
                'notes': 'Synthetic'
            })
            return df

        def synth_packages():
            df = pd.DataFrame({
                'id': [301,302,303,304,305],
                'package_id': [301,302,303,304,305],
                'name': ['Basic','Standard','Plus','Pro','VIP'],
                'price': [20,35,50,70,100]
            })
            return df

        def synth_subscriptions(members_df, packages_df):
            today = datetime.now()
            rows = []
            for mid in members_df['id'].head(20):
                pkg = int(packages_df.sample(1)['package_id'].iloc[0]) if 'package_id' in packages_df.columns else int(packages_df.sample(1)['id'].iloc[0])
                start = today - timedelta(days=int(np.random.randint(30, 360)))
                end = start + timedelta(days=int(np.random.randint(30, 180)))
                rows.append({'member_id': mid, 'package_id': pkg, 'start_date': start, 'end_date': end})
            return pd.DataFrame(rows)

        def synth_sessions(members_df):
            today = datetime.now()
            class_types = ['HIIT','Yoga','Strength','Spin','Pilates']
            rows = []
            for mid in members_df['id'].head(20):
                k = int(np.random.randint(3, 20))
                for j in range(k):
                    rows.append({
                        'member_id': mid,
                        'session_date': today - timedelta(days=int(np.random.randint(1, 180))),
                        'class_type': class_types[np.random.randint(0, len(class_types))]
                    })
            return pd.DataFrame(rows)

        # Members
        required_members_cols = {'id'}
        if self.members_df is None or self.members_df.empty or not required_members_cols.issubset(self.members_df.columns):
            if self.auto_synthesize_if_missing:
                print("  • Members missing/empty → synthesizing minimal dataset")
                self.members_df = synth_members()
                self.members_df.to_csv(os.path.join(out_dir, 'members.csv'), index=False)
            else:
                raise ValueError('members.csv missing required columns/rows')

        # Packages
        if self.packages_df is None or self.packages_df.empty or (not {'price'}.issubset(set(self.packages_df.columns)) and not {'amount'}.issubset(set(self.packages_df.columns))):
            if self.auto_synthesize_if_missing:
                print("  • Packages missing/empty → synthesizing minimal dataset")
                self.packages_df = synth_packages()
                self.packages_df.to_csv(os.path.join(out_dir, 'packages.csv'), index=False)
            else:
                raise ValueError('packages.csv missing required columns/rows')

        # Subscriptions
        needed_sub_cols = {'member_id'}
        if self.subscriptions_df is None or self.subscriptions_df.empty or not needed_sub_cols.issubset(self.subscriptions_df.columns):
            if self.auto_synthesize_if_missing:
                print("  • Subscriptions missing/empty → synthesizing minimal dataset")
                self.subscriptions_df = synth_subscriptions(self.members_df, self.packages_df)
                self.subscriptions_df.to_csv(os.path.join(out_dir, 'subscriptions.csv'), index=False)
            else:
                raise ValueError('subscriptions.csv missing required columns/rows')

        # Sessions
        needed_sess_cols = {'member_id'}
        if self.sessions_df is None or self.sessions_df.empty or not needed_sess_cols.issubset(self.sessions_df.columns):
            if self.auto_synthesize_if_missing:
                print("  • Sessions missing/empty → synthesizing minimal dataset")
                self.sessions_df = synth_sessions(self.members_df)
                self.sessions_df.to_csv(os.path.join(out_dir, 'sessions.csv'), index=False)
            else:
                raise ValueError('sessions.csv missing required columns/rows')

        print("✅ Validation complete. Required data present (synthetic added if needed).")
    
    def explore_data(self):
        """Display basic information about loaded datasets."""
        print("\n📊 DATASET EXPLORATION")
        print("=" * 50)
        
        # Members dataset
        print("\n👥 MEMBERS DATASET:")
        print(f"Shape: {self.members_df.shape}")
        print(f"Columns: {self.members_df.columns.tolist()}")
        print(f"Sample data:")
        print(self.members_df.head(3))
        
        # Sessions dataset
        print("\n🏃 SESSIONS DATASET:")
        print(f"Shape: {self.sessions_df.shape}")
        print(f"Columns: {self.sessions_df.columns.tolist()}")
        print(f"Sample data:")
        print(self.sessions_df.head(3))
        
        # Subscriptions dataset
        print("\n💳 SUBSCRIPTIONS DATASET:")
        print(f"Shape: {self.subscriptions_df.shape}")
        print(f"Columns: {self.subscriptions_df.columns.tolist()}")
        print(f"Sample data:")
        print(self.subscriptions_df.head(3))
        
        # Data types and missing values
        print("\n🔍 DATA QUALITY CHECK:")
        for name, df in [("Members", self.members_df), 
                        ("Sessions", self.sessions_df), 
                        ("Subscriptions", self.subscriptions_df)]:
            print(f"\n{name}:")
            print(f"  Missing values: {df.isnull().sum().sum()}")
            print(f"  Data types: {df.dtypes.value_counts().to_dict()}")
    
    def preprocess_data(self):
        """
        Clean and preprocess data for segmentation analysis.
        Handles missing values, data types, and creates derived features.
        """
        print("\n🔄 Preprocessing data...")
        
        # Convert timestamps & derive tenure
        if 'created_at' in self.members_df.columns:
            self.members_df['created_at'] = pd.to_datetime(self.members_df['created_at'], errors='coerce')
            self.members_df['member_since'] = self.members_df['created_at'].dt.date
            self.members_df['member_duration_days'] = (datetime.now() - self.members_df['created_at']).dt.days
        elif 'date_joined' in self.members_df.columns:
            self.members_df['date_joined'] = pd.to_datetime(self.members_df['date_joined'], errors='coerce')
            self.members_df['member_since'] = self.members_df['date_joined'].dt.date
            self.members_df['member_duration_days'] = (datetime.now() - self.members_df['date_joined']).dt.days
        
        if 'start_date' in self.subscriptions_df.columns:
            self.subscriptions_df['start_date'] = pd.to_datetime(self.subscriptions_df['start_date'])
            self.subscriptions_df['subscription_duration_days'] = (datetime.now() - self.subscriptions_df['start_date']).dt.days
        
        if 'session_date' in self.sessions_df.columns:
            self.sessions_df['session_date'] = pd.to_datetime(self.sessions_df['session_date'], errors='coerce')
            self.sessions_df['session_month'] = self.sessions_df['session_date'].dt.month
            self.sessions_df['session_year'] = self.sessions_df['session_date'].dt.year
        
        # Handle missing values
        fill_map = {}
        if 'weight' in self.members_df.columns:
            fill_map['weight'] = self.members_df['weight'].median()
        if 'height' in self.members_df.columns:
            fill_map['height'] = self.members_df['height'].median()
        if 'notes' in self.members_df.columns:
            fill_map['notes'] = 'No notes'
        if fill_map:
            self.members_df = self.members_df.fillna(fill_map)
        
        print("✅ Data preprocessing completed!")
        return True
    
    def calculate_member_features(self):
        """
        Calculate comprehensive features for each member including:
        - Visit frequency and patterns
        - Class preferences
        - Subscription metrics
        - RFM scores
        """
        print("\n🔄 Calculating member features...")
        
        # Initialize member features dataframe
        member_ids = self.members_df['id'].unique()
        self.member_features = pd.DataFrame({'member_id': member_ids})
        
        # 1. BASIC MEMBER INFO
        print("   📋 Basic member information...")
        base_cols = [c for c in ['name','email','created_at','date_joined','weight','height','dob'] if c in self.members_df.columns]
        member_info = self.members_df.set_index('id')[base_cols]
        self.member_features = self.member_features.merge(member_info, left_on='member_id', right_index=True, how='left')
        
        # 2. VISIT FREQUENCY ANALYSIS
        print("   🏃 Visit frequency analysis...")
        # Handle different column names for member ID in sessions
        member_id_col = None
        for col in ['member_id', 'user_id']:
            if col in self.sessions_df.columns:
                member_id_col = col
                break
        
        if member_id_col:
            visit_counts = self.sessions_df.groupby(member_id_col).size().reset_index(name='total_visits')
            visit_counts = visit_counts.rename(columns={member_id_col: 'member_id'})
            self.member_features = self.member_features.merge(visit_counts, on='member_id', how='left')
            self.member_features['total_visits'] = self.member_features['total_visits'].fillna(0)
        else:
            self.member_features['total_visits'] = 0
        
        # Calculate visit frequency (visits per month)
        if 'member_duration_days' in self.member_features.columns:
            self.member_features['visits_per_month'] = (
                self.member_features['total_visits'] / 
                (self.member_features['member_duration_days'] / 30)
            ).fillna(0)
        
        # 3. CLASS TYPE PREFERENCES
        print("   🎯 Class type preferences...")
        # Handle different column names for class type and member ID
        class_type_col = None
        for col in ['class_type', 'model', 'workout_type']:
            if col in self.sessions_df.columns:
                class_type_col = col
                break
        
        if class_type_col and member_id_col:
            class_preferences = self.sessions_df.groupby([member_id_col, class_type_col]).size().reset_index(name='class_count')
            class_preferences = class_preferences.rename(columns={member_id_col: 'member_id', class_type_col: 'class_type'})
            
            class_pivot = class_preferences.pivot(index='member_id', columns='class_type', values='class_count').fillna(0)
            
            # Add class preference columns
            for col in class_pivot.columns:
                self.member_features[f'class_{col}_count'] = class_pivot[col]
            
            # Most preferred class type
            most_preferred = class_preferences.loc[class_preferences.groupby('member_id')['class_count'].idxmax()]
            most_preferred_dict = dict(zip(most_preferred['member_id'], most_preferred['class_type']))
            self.member_features['most_preferred_class'] = self.member_features['member_id'].map(most_preferred_dict)

            # Class variety feature
            variety = class_preferences.groupby('member_id')['class_type'].nunique().reset_index(name='class_variety')
            self.member_features = self.member_features.merge(variety, on='member_id', how='left')
        else:
            self.member_features['class_variety'] = 0
            self.member_features['most_preferred_class'] = 'Unknown'
        
        # 4. SUBSCRIPTION ANALYSIS
        print("   💳 Subscription analysis...")
        if len(self.subscriptions_df) > 0:
            # Handle different column names for member ID in subscriptions
            sub_member_id_col = None
            for col in ['member_id', 'user_id']:
                if col in self.subscriptions_df.columns:
                    sub_member_id_col = col
                    break
            
            if sub_member_id_col:
                # Ensure dates
                for dc in ['start_date','end_date']:
                    if dc in self.subscriptions_df.columns:
                    self.subscriptions_df[dc] = pd.to_datetime(self.subscriptions_df[dc], errors='coerce')

            # Determine package key and price
            pkg_key = 'package_id' if 'package_id' in self.packages_df.columns else ('id' if 'id' in self.packages_df.columns else None)
            sub_pkg_key = 'package_id' if 'package_id' in self.subscriptions_df.columns else ('package' if 'package' in self.subscriptions_df.columns else None)
            price_col = 'price' if 'price' in self.packages_df.columns else ('amount' if 'amount' in self.packages_df.columns else None)

            subs = self.subscriptions_df.copy()
            pkgs = self.packages_df.copy()
            if pkg_key and sub_pkg_key and price_col:
                pkgs = pkgs[[pkg_key, price_col]].rename(columns={pkg_key: 'pkg_key', price_col: 'monthly_fee_derived'})
                subs = subs.rename(columns={sub_pkg_key: 'pkg_key'})
                subs = subs.merge(pkgs, on='pkg_key', how='left')
            else:
                subs['monthly_fee_derived'] = 0.0

            # Aggregations
            subscription_info = subs.groupby(sub_member_id_col).agg({
                'pkg_key': 'count',
                'monthly_fee_derived': ['mean','sum']
            }).reset_index()
            subscription_info.columns = [sub_member_id_col,'subscription_count','avg_monthly_fee','total_fees_paid']
            subscription_info = subscription_info.rename(columns={sub_member_id_col: 'member_id'})

                # Duration proxy
                if 'start_date' in subs.columns:
                    subs['subscription_duration_days'] = (subs['end_date'].fillna(datetime.now()) - subs['start_date']).dt.days
                    dur = subs.groupby(sub_member_id_col)['subscription_duration_days'].mean().reset_index()
                    dur = dur.rename(columns={sub_member_id_col: 'member_id'})
                    subscription_info = subscription_info.merge(dur, on='member_id', how='left')
                    subscription_info = subscription_info.rename(columns={'subscription_duration_days':'avg_subscription_duration'})
                else:
                    subscription_info['avg_subscription_duration'] = 0

            self.member_features = self.member_features.merge(subscription_info, on='member_id', how='left')
            for c in ['subscription_count','avg_subscription_duration','avg_monthly_fee','total_fees_paid']:
                if c in self.member_features.columns:
                    self.member_features[c] = self.member_features[c].fillna(0)
            else:
                # Default values if no subscription data
                self.member_features['subscription_count'] = 0
                self.member_features['avg_monthly_fee'] = 0
                self.member_features['avg_subscription_duration'] = 0
                self.member_features['total_fees_paid'] = 0
        
        # 5. RFM ANALYSIS
        print("   📊 RFM analysis...")
        self._calculate_rfm_scores()
        
        # 6. ACTIVITY PATTERNS
        print("   📅 Activity patterns...")
        # Handle different column names for session date
        session_date_col = None
        for col in ['session_date', 'date', 'created_at']:
            if col in self.sessions_df.columns:
                session_date_col = col
                break
        
        if session_date_col and member_id_col:
            # Last visit
            last_visits = self.sessions_df.groupby(member_id_col)[session_date_col].max().reset_index()
            last_visits = last_visits.rename(columns={member_id_col: 'member_id', session_date_col: 'last_visit'})
            self.member_features = self.member_features.merge(last_visits, on='member_id', how='left')
            
            # Days since last visit
            if 'last_visit' in self.member_features.columns:
                self.member_features['days_since_last_visit'] = (
                    datetime.now() - self.member_features['last_visit']
                ).dt.days
        else:
            self.member_features['days_since_last_visit'] = 999  # Default for no sessions
        
        # 7. DEMOGRAPHIC FEATURES
        print("   👤 Demographic features...")
        if 'weight' in self.member_features.columns and 'height' in self.member_features.columns:
            # BMI calculation (if height is in cm, convert to meters)
            self.member_features['bmi'] = (
                self.member_features['weight'] / 
                ((self.member_features['height'] / 100) ** 2)
            )
            
            # Age group (if DOB available)
            if 'dob' in self.members_df.columns:
                self.members_df['dob'] = pd.to_datetime(self.members_df['dob'])
                self.members_df['age'] = (datetime.now() - self.members_df['dob']).dt.days / 365.25
                age_info = self.members_df[['id', 'age']].set_index('id')
                self.member_features = self.member_features.merge(age_info, left_on='member_id', right_index=True, how='left')
                
                # Age groups
                self.member_features['age_group'] = pd.cut(
                    self.member_features['age'], 
                    bins=[0, 25, 35, 45, 55, 100], 
                    labels=['18-25', '26-35', '36-45', '46-55', '55+']
                )
        
        print("✅ Member features calculated!")
        return True
    
    def _calculate_rfm_scores(self):
        """Calculate RFM (Recency, Frequency, Monetary) scores for each member."""
        # Recency: Days since last visit
        if 'days_since_last_visit' in self.member_features.columns:
            recency_scores = pd.qcut(
                self.member_features['days_since_last_visit'], 
                q=5, 
                labels=[5, 4, 3, 2, 1], 
                duplicates='drop'
            )
            self.member_features['recency_score'] = recency_scores.astype(float)
        
        # Frequency: Total visits
        if 'total_visits' in self.member_features.columns:
            frequency_scores = pd.qcut(
                self.member_features['total_visits'], 
                q=5, 
                labels=[1, 2, 3, 4, 5], 
                duplicates='drop'
            )
            self.member_features['frequency_score'] = frequency_scores.astype(float)
        
        # Monetary: Subscription value (using subscription count as proxy)
        if 'subscription_count' in self.member_features.columns:
            monetary_scores = pd.qcut(
                self.member_features['subscription_count'], 
                q=5, 
                labels=[1, 2, 3, 4, 5], 
                duplicates='drop'
            )
            self.member_features['monetary_score'] = monetary_scores.astype(float)
        
        # RFM Score (combined)
        if all(col in self.member_features.columns for col in ['recency_score', 'frequency_score', 'monetary_score']):
            self.member_features['rfm_score'] = (
                self.member_features['recency_score'] + 
                self.member_features['frequency_score'] + 
                self.member_features['monetary_score']
            )
    
    def perform_segmentation(self):
        """
        Perform member segmentation using multiple approaches:
        1. RFM-based segmentation
        2. Activity-based segmentation
        3. Behavioral segmentation
        """
        print("\n🔄 Performing member segmentation...")
        
        # 1. RFM-BASED SEGMENTATION
        print("   📊 RFM-based segmentation...")
        self._rfm_segmentation()
        
        # 2. ACTIVITY-BASED SEGMENTATION
        print("   🏃 Activity-based segmentation...")
        self._activity_segmentation()
        
        # 3. BEHAVIORAL SEGMENTATION
        print("   🎯 Behavioral segmentation...")
        self._behavioral_segmentation()
        
        # 4. COMBINED SEGMENTATION
        print("   🔄 Combined segmentation...")
        self._combined_segmentation()
        
        print("✅ Member segmentation completed!")
        return True
    
    def _rfm_segmentation(self):
        """Create RFM-based segments."""
        if 'rfm_score' in self.member_features.columns:
            # RFM segments
            rfm_conditions = [
                (self.member_features['rfm_score'] >= 12),
                (self.member_features['rfm_score'] >= 9) & (self.member_features['rfm_score'] < 12),
                (self.member_features['rfm_score'] >= 6) & (self.member_features['rfm_score'] < 9),
                (self.member_features['rfm_score'] >= 3) & (self.member_features['rfm_score'] < 6),
                (self.member_features['rfm_score'] < 3)
            ]
            rfm_values = ['Champions', 'Loyal Customers', 'At Risk', 'Can\'t Lose', 'Lost']
            
            self.member_features['rfm_segment'] = np.select(rfm_conditions, rfm_values, default='Unknown')
    
    def _activity_segmentation(self):
        """Create activity-based segments."""
        if 'visits_per_month' in self.member_features.columns:
            # Activity segments based on visit frequency
            activity_conditions = [
                (self.member_features['visits_per_month'] >= 8),
                (self.member_features['visits_per_month'] >= 4) & (self.member_features['visits_per_month'] < 8),
                (self.member_features['visits_per_month'] >= 2) & (self.member_features['visits_per_month'] < 4),
                (self.member_features['visits_per_month'] >= 1) & (self.member_features['visits_per_month'] < 2),
                (self.member_features['visits_per_month'] < 1)
            ]
            activity_values = ['Very Active', 'Active', 'Moderate', 'Occasional', 'Inactive']
            
            self.member_features['activity_segment'] = np.select(activity_conditions, activity_values, default='Unknown')
    
    def _behavioral_segmentation(self):
        """Create behavioral segments based on class preferences and patterns."""
        # Class preference diversity
        class_columns = [col for col in self.member_features.columns if col.startswith('class_') and col.endswith('_count')]
        
        if class_columns:
            self.member_features['class_diversity'] = (self.member_features[class_columns] > 0).sum(axis=1)
            
            # Behavioral segments
            behavior_conditions = [
                (self.member_features['class_diversity'] >= 4),
                (self.member_features['class_diversity'] >= 2) & (self.member_features['class_diversity'] < 4),
                (self.member_features['class_diversity'] == 1)
            ]
            behavior_values = ['Variety Seeker', 'Balanced', 'Specialist']
            
            self.member_features['behavior_segment'] = np.select(behavior_conditions, behavior_values, default='Unknown')
    
    def _combined_segmentation(self):
        """Create a combined segment that considers all factors."""
        # Combine RFM and Activity segments
        if 'rfm_segment' in self.member_features.columns and 'activity_segment' in self.member_features.columns:
            self.member_features['combined_segment'] = (
                self.member_features['rfm_segment'] + ' - ' + self.member_features['activity_segment']
            )
    
    def analyze_segments(self):
        """Analyze and display insights about each segment."""
        print("\n📊 SEGMENT ANALYSIS")
        print("=" * 50)
        
        # RFM Segment Analysis
        if 'rfm_segment' in self.member_features.columns:
            print("\n🎯 RFM SEGMENT ANALYSIS:")
            rfm_analysis = self.member_features.groupby('rfm_segment').agg({
                'member_id': 'count',
                'total_visits': 'mean',
                'visits_per_month': 'mean',
                'subscription_count': 'mean'
            }).round(2)
            rfm_analysis.columns = ['Member Count', 'Avg Total Visits', 'Avg Visits/Month', 'Avg Subscriptions']
            print(rfm_analysis)
        
        # Activity Segment Analysis
        if 'activity_segment' in self.member_features.columns:
            print("\n🏃 ACTIVITY SEGMENT ANALYSIS:")
            activity_analysis = self.member_features.groupby('activity_segment').agg({
                'member_id': 'count',
                'total_visits': 'mean',
                'visits_per_month': 'mean'
            }).round(2)
            activity_analysis.columns = ['Member Count', 'Avg Total Visits', 'Avg Visits/Month']
            print(activity_analysis)
        
        # Behavioral Segment Analysis
        if 'behavior_segment' in self.member_features.columns:
            print("\n🎯 BEHAVIORAL SEGMENT ANALYSIS:")
            behavior_analysis = self.member_features.groupby('behavior_segment').agg({
                'member_id': 'count',
                'class_diversity': 'mean',
                'total_visits': 'mean'
            }).round(2)
            behavior_analysis.columns = ['Member Count', 'Avg Class Diversity', 'Avg Total Visits']
            print(behavior_analysis)
    
    def create_visualizations(self):
        """Create comprehensive visualizations for member segmentation."""
        print("\n🎨 Creating visualizations...")
        
        # Set up the plotting style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # 1. SEGMENT DISTRIBUTION CHARTS
        self._create_segment_distributions()
        
        # 2. FEATURE ANALYSIS CHARTS
        self._create_feature_analysis()
        
        # 3. RFM ANALYSIS CHARTS
        self._create_rfm_analysis()
        
        # 4. ACTIVITY PATTERN CHARTS
        self._create_activity_patterns()
        
        print("✅ Visualizations created!")
    
    def _create_segment_distributions(self):
        """Create charts showing distribution of members across segments."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Member Segment Distributions', fontsize=16, fontweight='bold')
        
        # RFM Segment Distribution
        if 'rfm_segment' in self.member_features.columns:
            rfm_counts = self.member_features['rfm_segment'].value_counts()
            axes[0, 0].pie(rfm_counts.values, labels=rfm_counts.index, autopct='%1.1f%%', startangle=90)
            axes[0, 0].set_title('RFM Segment Distribution')
        
        # Activity Segment Distribution
        if 'activity_segment' in self.member_features.columns:
            activity_counts = self.member_features['activity_segment'].value_counts()
            axes[0, 1].pie(activity_counts.values, labels=activity_counts.index, autopct='%1.1f%%', startangle=90)
            axes[0, 1].set_title('Activity Segment Distribution')
        
        # Behavioral Segment Distribution
        if 'behavior_segment' in self.member_features.columns:
            behavior_counts = self.member_features['behavior_segment'].value_counts()
            axes[1, 0].pie(behavior_counts.values, labels=behavior_counts.index, autopct='%1.1f%%', startangle=90)
            axes[1, 0].set_title('Behavioral Segment Distribution')
        
        # Combined Segment Distribution
        if 'combined_segment' in self.member_features.columns:
            combined_counts = self.member_features['combined_segment'].value_counts().head(10)
            axes[1, 1].barh(range(len(combined_counts)), combined_counts.values)
            axes[1, 1].set_yticks(range(len(combined_counts)))
            axes[1, 1].set_yticklabels(combined_counts.index)
            axes[1, 1].set_title('Top 10 Combined Segments')
            axes[1, 1].set_xlabel('Member Count')
        
        plt.tight_layout()
        plt.savefig('member_segment_distributions.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def _create_feature_analysis(self):
        """Create charts analyzing features across segments."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Feature Analysis Across Segments', fontsize=16, fontweight='bold')
        
        # Visits per month by activity segment
        if 'activity_segment' in self.member_features.columns and 'visits_per_month' in self.member_features.columns:
            self.member_features.boxplot(column='visits_per_month', by='activity_segment', ax=axes[0, 0])
            axes[0, 0].set_title('Visits per Month by Activity Segment')
            axes[0, 0].set_xlabel('Activity Segment')
            axes[0, 0].set_ylabel('Visits per Month')
        
        # Total visits by RFM segment
        if 'rfm_segment' in self.member_features.columns and 'total_visits' in self.member_features.columns:
            self.member_features.boxplot(column='total_visits', by='rfm_segment', ax=axes[0, 1])
            axes[0, 1].set_title('Total Visits by RFM Segment')
            axes[0, 1].set_xlabel('RFM Segment')
            axes[0, 1].set_ylabel('Total Visits')
        
        # Class diversity by behavioral segment
        if 'behavior_segment' in self.member_features.columns and 'class_diversity' in self.member_features.columns:
            self.member_features.boxplot(column='class_diversity', by='behavior_segment', ax=axes[1, 0])
            axes[1, 0].set_title('Class Diversity by Behavioral Segment')
            axes[1, 0].set_xlabel('Behavioral Segment')
            axes[1, 0].set_ylabel('Class Diversity')
        
        # Subscription count by RFM segment
        if 'rfm_segment' in self.member_features.columns and 'subscription_count' in self.member_features.columns:
            self.member_features.boxplot(column='subscription_count', by='rfm_segment', ax=axes[1, 1])
            axes[1, 1].set_title('Subscription Count by RFM Segment')
            axes[1, 1].set_xlabel('RFM Segment')
            axes[1, 1].set_ylabel('Subscription Count')
        
        plt.tight_layout()
        plt.savefig('feature_analysis_across_segments.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def _create_rfm_analysis(self):
        """Create RFM analysis visualizations."""
        if not all(col in self.member_features.columns for col in ['recency_score', 'frequency_score', 'monetary_score']):
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('RFM Analysis', fontsize=16, fontweight='bold')
        
        # RFM Score Distribution
        axes[0, 0].hist(self.member_features['rfm_score'], bins=20, alpha=0.7, color='skyblue')
        axes[0, 0].set_title('RFM Score Distribution')
        axes[0, 0].set_xlabel('RFM Score')
        axes[0, 0].set_ylabel('Frequency')
        
        # Recency vs Frequency
        axes[0, 1].scatter(self.member_features['recency_score'], self.member_features['frequency_score'], 
                           alpha=0.6, color='green')
        axes[0, 1].set_title('Recency vs Frequency')
        axes[0, 1].set_xlabel('Recency Score')
        axes[0, 1].set_ylabel('Frequency Score')
        
        # Frequency vs Monetary
        axes[1, 0].scatter(self.member_features['frequency_score'], self.member_features['monetary_score'], 
                           alpha=0.6, color='orange')
        axes[1, 0].set_title('Frequency vs Monetary')
        axes[1, 0].set_xlabel('Frequency Score')
        axes[1, 0].set_ylabel('Monetary Score')
        
        # RFM Heatmap
        rfm_pivot = self.member_features.groupby(['recency_score', 'frequency_score'])['monetary_score'].mean().unstack()
        sns.heatmap(rfm_pivot, annot=True, cmap='YlOrRd', ax=axes[1, 1])
        axes[1, 1].set_title('RFM Score Heatmap')
        
        plt.tight_layout()
        plt.savefig('rfm_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def _create_activity_patterns(self):
        """Create activity pattern visualizations."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Activity Patterns Analysis', fontsize=16, fontweight='bold')
        
        # Visits per month distribution
        if 'visits_per_month' in self.member_features.columns:
            axes[0, 0].hist(self.member_features['visits_per_month'], bins=20, alpha=0.7, color='lightcoral')
            axes[0, 0].set_title('Visits per Month Distribution')
            axes[0, 0].set_xlabel('Visits per Month')
            axes[0, 0].set_ylabel('Frequency')
        
        # Total visits distribution
        if 'total_visits' in self.member_features.columns:
            axes[0, 1].hist(self.member_features['total_visits'], bins=20, alpha=0.7, color='lightgreen')
            axes[0, 1].set_title('Total Visits Distribution')
            axes[0, 1].set_xlabel('Total Visits')
            axes[0, 1].set_ylabel('Frequency')
        
        # Class diversity distribution
        if 'class_diversity' in self.member_features.columns:
            axes[1, 0].hist(self.member_features['class_diversity'], bins=10, alpha=0.7, color='lightblue')
            axes[1, 0].set_title('Class Diversity Distribution')
            axes[1, 0].set_xlabel('Number of Different Class Types')
            axes[1, 0].set_ylabel('Frequency')
        
        # Age group vs activity (if available)
        if 'age_group' in self.member_features.columns and 'visits_per_month' in self.member_features.columns:
            age_activity = self.member_features.groupby('age_group')['visits_per_month'].mean()
            axes[1, 1].bar(range(len(age_activity)), age_activity.values, color='purple')
            axes[1, 1].set_title('Average Visits per Month by Age Group')
            axes[1, 1].set_xlabel('Age Group')
            axes[1, 1].set_ylabel('Average Visits per Month')
            axes[1, 1].set_xticks(range(len(age_activity)))
            axes[1, 1].set_xticklabels(age_activity.index, rotation=45)
        
        plt.tight_layout()
        plt.savefig('activity_patterns.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_insights(self):
        """Generate actionable insights and recommendations based on segmentation."""
        print("\n💡 ACTIONABLE INSIGHTS & RECOMMENDATIONS")
        print("=" * 60)
        
        # Overall member health
        total_members = len(self.member_features)
        active_members = len(self.member_features[self.member_features['total_visits'] > 0])
        inactive_members = total_members - active_members
        
        print(f"\n📊 OVERALL MEMBER HEALTH:")
        print(f"  • Total members: {total_members}")
        print(f"  • Active members: {active_members} ({active_members/total_members*100:.1f}%)")
        print(f"  • Inactive members: {inactive_members} ({inactive_members/total_members*100:.1f}%)")
        
        # High-value segments
        if 'rfm_segment' in self.member_features.columns:
            champions = len(self.member_features[self.member_features['rfm_segment'] == 'Champions'])
            loyal = len(self.member_features[self.member_features['rfm_segment'] == 'Loyal Customers'])
            
            print(f"\n🏆 HIGH-VALUE SEGMENTS:")
            print(f"  • Champions: {champions} members ({champions/total_members*100:.1f}%)")
            print(f"  • Loyal Customers: {loyal} members ({loyal/total_members*100:.1f}%)")
        
        # At-risk segments
        if 'rfm_segment' in self.member_features.columns:
            at_risk = len(self.member_features[self.member_features['rfm_segment'] == 'At Risk'])
            cant_lose = len(self.member_features[self.member_features['rfm_segment'] == 'Can\'t Lose'])
            lost = len(self.member_features[self.member_features['rfm_segment'] == 'Lost'])
            
            print(f"\n🚨 AT-RISK SEGMENTS:")
            print(f"  • At Risk: {at_risk} members ({at_risk/total_members*100:.1f}%)")
            print(f"  • Can't Lose: {cant_lose} members ({cant_lose/total_members*100:.1f}%)")
            print(f"  • Lost: {lost} members ({lost/total_members*100:.1f}%)")
        
        # Activity insights
        if 'activity_segment' in self.member_features.columns:
            very_active = len(self.member_features[self.member_features['activity_segment'] == 'Very Active'])
            inactive = len(self.member_features[self.member_features['activity_segment'] == 'Inactive'])
            
            print(f"\n🏃 ACTIVITY INSIGHTS:")
            print(f"  • Very Active: {very_active} members ({very_active/total_members*100:.1f}%)")
            print(f"  • Inactive: {inactive} members ({inactive/total_members*100:.1f}%)")
        
        # Recommendations
        print(f"\n💡 STRATEGIC RECOMMENDATIONS:")
        print(f"  1. 🎯 TARGETED RETENTION: Focus on 'At Risk' and 'Can't Lose' segments")
        print(f"  2. 🚀 REACTIVATION CAMPAIGNS: Develop programs for 'Inactive' and 'Lost' members")
        print(f"  3. 🏆 CHAMPION PROGRAMS: Create loyalty programs for 'Champions' and 'Loyal Customers'")
        print(f"  4. 📊 PERSONALIZATION: Use segment insights to customize marketing and class offerings")
        print(f"  5. 🔄 MONITORING: Track segment migration monthly to identify trends")
        
        # Segment-specific actions
        print(f"\n🎯 SEGMENT-SPECIFIC ACTIONS:")
        
        if 'rfm_segment' in self.member_features.columns:
            print(f"  • Champions: Premium services, referral programs, exclusive events")
            print(f"  • Loyal Customers: Cross-selling, upgrade incentives, community building")
            print(f"  • At Risk: Personalized outreach, special offers, feedback collection")
            print(f"  • Can't Lose: Urgent retention campaigns, one-on-one support")
            print(f"  • Lost: Re-engagement campaigns, new member benefits, facility improvements")
    
    def export_results(self):
        """Export all analysis results and segmented data."""
        print("\n💾 Exporting results...")
        
        # Export segmented member data
        if self.member_features is not None:
            self.member_features.to_csv('member_segmentation_results.csv', index=False)
            print("✅ Member segmentation results exported: member_segmentation_results.csv")
        
        # Export segment summaries
        if 'rfm_segment' in self.member_features.columns:
            rfm_summary = self.member_features.groupby('rfm_segment').agg({
                'member_id': 'count',
                'total_visits': ['mean', 'std'],
                'visits_per_month': ['mean', 'std'],
                'subscription_count': ['mean', 'std']
            }).round(3)
            rfm_summary.to_csv('rfm_segment_summary.csv')
            print("✅ RFM segment summary exported: rfm_segment_summary.csv")
        
        if 'activity_segment' in self.member_features.columns:
            activity_summary = self.member_features.groupby('activity_segment').agg({
                'member_id': 'count',
                'total_visits': ['mean', 'std'],
                'visits_per_month': ['mean', 'std']
            }).round(3)
            activity_summary.to_csv('activity_segment_summary.csv')
            print("✅ Activity segment summary exported: activity_segment_summary.csv")
        
        # Export key insights
        insights = {
            'total_members': len(self.member_features),
            'active_members': len(self.member_features[self.member_features['total_visits'] > 0]),
            'avg_visits_per_month': self.member_features['visits_per_month'].mean(),
            'avg_total_visits': self.member_features['total_visits'].mean()
        }
        
        insights_df = pd.DataFrame([insights])
        insights_df.to_csv('member_segmentation_insights.csv', index=False)
        print("✅ Key insights exported: member_segmentation_insights.csv")
        
        print("✅ All results exported successfully!")

def main():
    """
    Main function to run the complete member segmentation analysis.
    Designed for Google Colab with clear progress indicators.
    """
    print("🎯 PHASE 3: MEMBER SEGMENTATION ANALYSIS")
    print("=" * 60)
    print("Step 11: Segment members by frequency, class types, subscription duration")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = MemberSegmentationAnalyzer()
    
    # Step 1: Load data
    if not analyzer.load_data():
        print("❌ Failed to load data. Please check file paths.")
        return
    
    # Ensure required rows/columns exist or synthesize minimal data
    analyzer.validate_or_synthesize_data()

    # Step 2: Explore data
    analyzer.explore_data()
    
    # Step 3: Preprocess data
    if not analyzer.preprocess_data():
        print("❌ Data preprocessing failed.")
        return
    
    # Step 4: Calculate member features
    if not analyzer.calculate_member_features():
        print("❌ Feature calculation failed.")
        return
    
    # Step 5: Perform segmentation
    if not analyzer.perform_segmentation():
        print("❌ Segmentation failed.")
        return
    
    # Step 6: Analyze segments
    analyzer.analyze_segments()
    
    # Step 7: Create visualizations
    analyzer.create_visualizations()
    
    # Step 8: Generate insights
    analyzer.generate_insights()
    
    # Step 9: Export results
    analyzer.export_results()
    
    print("\n🎉 MEMBER SEGMENTATION ANALYSIS COMPLETE!")
    print("=" * 60)
    print("📊 Use the generated insights to improve member retention and engagement!")
    print("📁 Check the exported CSV files for detailed results.")
    print("🖼️  View the generated charts for visual insights.")

if __name__ == "__main__":
    main()
