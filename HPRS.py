import streamlit as st
import json
import sys
import os

# Add current directory to Python path
sys.path.append(os.path.dirname(__file__))

# Basic configuration
st.set_page_config(
    page_title="Sustainable Shopping Assistant", 
    page_icon="🌱",
    layout="wide"
)

# Initialize session state FIRST
if 'user_prefs' not in st.session_state:
    st.session_state.user_prefs = {
        'priority_order': ['vegan', 'organic', 'fair-trade'],
        'budget_range': [10, 100],
        'avoid_tags': []
    }

# Test imports with better error handling
try:
    from engine.recommender import recommend_products, load_products
    st.success("✅ Recommendation engine loaded!")
except Exception as e:
    st.error(f"❌ Recommendation engine failed: {e}")
    st.write(f"Current directory: {os.path.dirname(__file__)}")
    st.write(f"Engine path exists: {os.path.exists('engine/recommender.py')}")
    st.stop()

try:
    from engine.learning import learner
    st.success("✅ Learning system loaded!")
    
    # Initialize weights if empty
    if not learner.learned_weights:
        learner.initialize_weights(st.session_state.user_prefs['priority_order'])
    
except Exception as e:
    st.error(f"❌ Learning system failed: {e}")
    st.stop()

# Load products
try:
    products = load_products()
    st.success(f"✅ Loaded {len(products)} sustainable products!")
except Exception as e:
    st.error(f"❌ Failed to load products: {e}")
    st.stop()

# Header
st.title("🌱 Sustainable Shopping Assistant")
st.markdown("### Discover products that match your values")

# Sidebar - User Preferences
st.sidebar.header("🎯 Your Values")

# Priority ordering
st.sidebar.subheader("What matters most to you?")
available_tags = ['vegan', 'organic', 'fair-trade', 'biodegradable', 'plastic-free', 'carbon-neutral', 'recycled']

priority_order = st.sidebar.multiselect(
    "Drag to reorder your priorities:",
    available_tags,
    default=st.session_state.user_prefs['priority_order']
)
st.session_state.user_prefs['priority_order'] = priority_order

# Budget
st.sidebar.subheader("💰 Your Budget")
budget_range = st.sidebar.slider(
    "Price range ($)",
    0, 200,
    value=st.session_state.user_prefs['budget_range']
)
st.session_state.user_prefs['budget_range'] = budget_range

# Learning Dashboard
st.sidebar.markdown("---")
st.sidebar.subheader("🧠 System Learning")

learned_weights = learner.get_learned_weights()

# Show ALL tags that are in current priorities
if st.session_state.user_prefs['priority_order']:
    for tag in st.session_state.user_prefs['priority_order']:
        # Get weight or default to 1.0 if not initialized
        weight = learned_weights.get(tag, 1.0)

        if weight > 1.2:
            emoji = "📈"
            status = " (Strong preference)"
        elif weight > 1.0:
            emoji = "↗️" 
            status = " (Growing)"
        elif weight < 0.8:
            emoji = "📉"
            status = " (Low interest)"
        else:
            emoji = "📊"
            status = " (Neutral)"
        
        st.sidebar.write(f"{emoji} **{tag}**: {weight:.1f}x{status}")
        

        # ✅ FIXED Progress bar visualization
        progress = max(0.0, min(1.0, (weight - 0.3) / 1.7))  # No negative values
        st.sidebar.progress(progress)
else:
    st.sidebar.info("🤖 Select some values to start learning!")

# Demo Learning Buttons
st.sidebar.markdown("---")
st.sidebar.subheader("🧪 Demo Learning")

if st.sidebar.button("Simulate: User LOVES Vegan"):
    vegan_products = [p for p in products if 'vegan' in p.get('sustainability_tags', [])]
    for product in vegan_products[:3]:
        learner.track_interaction({
            'action_type': 'purchase',
            'product_tags': product['sustainability_tags'],
            'timestamp': '2024-01-01'
        })
    st.sidebar.success("System learned you're passionate about vegan products!")
    st.rerun()

if st.sidebar.button("Simulate: User IGNORES Carbon-Neutral"):
    # Ensure carbon-neutral is initialized in weights
    if 'carbon-neutral' not in learner.learned_weights:
        learner.learned_weights['carbon-neutral'] = 1.0
    
    carbon_products = [p for p in products if 'carbon-neutral' in p.get('sustainability_tags', [])]
    
    # Stronger learning - more interactions
    for product in carbon_products[:3]:
        learner.track_interaction({
            'action_type': 'view',
            'product_tags': product['sustainability_tags'],
            'timestamp': '2024-01-01'
        })
    
    st.sidebar.info("🔻 Carbon-neutral weight decreased!")
    st.rerun()

if st.sidebar.button("Simulate: User LOVES Biodegradable"):
    if 'biodegradable' not in learner.learned_weights:
        learner.learned_weights['biodegradable'] = 1.0
        
    bio_products = [p for p in products if 'biodegradable' in p.get('sustainability_tags', [])]
    for product in bio_products[:3]:
        learner.track_interaction({
            'action_type': 'purchase',
            'product_tags': product['sustainability_tags'],
            'timestamp': '2024-01-01'
        })
    st.sidebar.success("System learned you love biodegradable!")
    st.rerun()

if st.sidebar.button("Simulate: User LOVES Plastic-Free"):
    if 'plastic-free' not in learner.learned_weights:
        learner.learned_weights['plastic-free'] = 1.0
        
    plastic_free_products = [p for p in products if 'plastic-free' in p.get('sustainability_tags', [])]
    for product in plastic_free_products[:3]:
        learner.track_interaction({
            'action_type': 'purchase',
            'product_tags': product['sustainability_tags'],
            'timestamp': '2024-01-01'
        })
    st.sidebar.success("System learned you love plastic-free!")
    st.rerun()

if st.sidebar.button("Simulate: User LOVES Recycled"):
    if 'recycled' not in learner.learned_weights:
        learner.learned_weights['recycled'] = 1.0
        
    recycled_products = [p for p in products if 'recycled' in p.get('sustainability_tags', [])]
    for product in recycled_products[:3]:
        learner.track_interaction({
            'action_type': 'purchase',
            'product_tags': product['sustainability_tags'],
            'timestamp': '2024-01-01'
        })
    st.sidebar.success("System learned you love recycled!")
    st.rerun()

# Main Content Area
st.markdown("---")

if st.button("🎯 Get Personalized Recommendations"):
    with st.spinner("Finding your perfect sustainable products..."):
        # Get base recommendations
        base_recommendations = recommend_products(st.session_state.user_prefs, products)
        
        # Apply learning to scores
        final_recommendations = []
        for rec in base_recommendations:
            product = rec['product']
            base_score = rec['score']
            
            # Apply learned weights
            adjusted_score = learner.apply_learning_to_score(
                base_score, 
                product.get('sustainability_tags', [])
            )
            
            final_recommendations.append({
                'product': product,
                'base_score': base_score,
                'adjusted_score': adjusted_score
            })
        
        # Sort by adjusted score
        final_recommendations.sort(key=lambda x: x['adjusted_score'], reverse=True)
        
        # Display recommendations
        st.subheader("✨ Your Personalized Sustainable Picks")
        
        for i, rec in enumerate(final_recommendations, 1):
            product = rec['product']
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{i}. {product['name']}**")
                st.markdown(f"*{product['brand']}*")
                st.markdown(f"💰 ${product['price']}")
                st.markdown(f"📝 {product['description']}")
                
                # Display tags with emojis
                tags_display = []
                for tag in product.get('sustainability_tags', []):
                    if tag in st.session_state.user_prefs['priority_order']:
                        tags_display.append(f"**✅ {tag}**")
                    else:
                        tags_display.append(f"✅ {tag}")
                
                st.markdown(" | ".join(tags_display))
            
            with col2:
                # Score visualization
                base_score = rec['base_score']
                adjusted_score = rec['adjusted_score']
                
                st.metric(
                    label="Match Score",
                    value=f"{int(adjusted_score)}",
                    delta=f"{int(adjusted_score - base_score)}"
                )
            
            st.markdown("---")

# Success message
st.balloons()
st.success("🎉 Your Sustainable Shopping Assistant is working perfectly!")
