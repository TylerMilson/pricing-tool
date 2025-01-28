import streamlit as st

# Function to calculate pricing
def calculate_pricing(connected_users, price_per_user, tiers, manual_syncs, manual_sync_cost, last_tier_price):
    total_cost = 0
    breakdown = []
    remaining_users = connected_users

    # Apply tiers
    for i, (upper_limit, cost_per_user) in enumerate(tiers):
        if remaining_users > 0:
            tier_capacity = min(upper_limit - (tiers[i-1][0] if i > 0 else 0), remaining_users)
            cost_for_tier = tier_capacity * cost_per_user
            breakdown.append(f"**Tier {i+1}:** {tier_capacity:,} users @ ${cost_per_user:.2f}/user → = ${cost_for_tier:,.2f}")
            total_cost += cost_for_tier
            remaining_users -= tier_capacity

    # Final Tier (Always Unbounded)
    if remaining_users > 0 and last_tier_price > 0:
        extra_cost = remaining_users * last_tier_price
        breakdown.append(f"**Final Tier (All Remaining Users):** {remaining_users:,} users @ ${last_tier_price:.2f}/user → = ${extra_cost:,.2f}")
        total_cost += extra_cost

    # Flat Pricing (only used if no tiers are defined)
    elif not tiers:
        total_cost = connected_users * price_per_user
        breakdown.append(f"**Flat Rate:** {connected_users:,} users @ ${price_per_user:.2f}/user → = ${total_cost:,.2f}")

    # Manual Sync Cost
    total_manual_sync_cost = manual_syncs * manual_sync_cost if manual_syncs else 0
    if manual_syncs > 0:
        breakdown.append("---")  # Horizontal line in markdown
        breakdown.append(f"**Manual Syncs:** {manual_syncs:,} syncs @ ${manual_sync_cost:.2f}/sync → = ${total_manual_sync_cost:,.2f}")

    # Final Total
    total_cost += total_manual_sync_cost
    return total_cost, breakdown

# Streamlit UI
st.title("SnapTrade Pricing Calculator")

# Checkbox: Enable Tiered Pricing
use_tiers = st.checkbox("Use Tiered Pricing")

# Checkbox: Enable Manual Syncs
use_manual_syncs = st.checkbox("Include Manual Syncs")

# Always ask for Connected Users
connected_users = st.number_input("Total Connected Users", min_value=0)

# Flat Pricing (only shown if tiered pricing is NOT enabled)
price_per_user = 0.0
last_tier_price = 0  # ✅ Fix: Set Default Value to Avoid Errors

if not use_tiers:
    price_per_user = st.number_input("Price Per User", min_value=0.0)

# **Improved Tier Selection UX**
tiers = []
if use_tiers:
    st.subheader("Tiered Pricing Setup")

    # **New Approach: Users now select total tiers (including the unbounded one)**
    num_tiers = st.number_input("Number of Tiers (Final Tier is Always Unbounded)", min_value=1, max_value=4, value=1, step=1)

    for i in range(num_tiers - 1):  # Leave the last one for the unbounded tier
        limit = st.number_input(f"Tier {i+1} Limit", min_value=0, key=f"limit{i}")
        price = st.number_input(f"Tier {i+1} Price", min_value=0.0, key=f"price{i}")
        if limit and price:
            tiers.append((limit, price))

    # **Always Show Unbounded Tier Price Entry**
    st.markdown("---")  # Adds a visual line below tier selection
    last_tier_price = st.number_input("Final Tier Price (Applies to All Remaining Users)", min_value=0.0)

# **Visual Separator for Manual Syncs**
if use_manual_syncs:
    st.markdown("---")  # Add a line to separate manual syncs visually

# Manual Syncs Section (only shown if checkbox is enabled)
manual_syncs, manual_sync_cost = 0, 0.0
if use_manual_syncs:
    st.subheader("Manual Sync Pricing")
    manual_syncs = st.number_input("Manual Syncs", min_value=0)
    manual_sync_cost = st.number_input("Manual Sync Cost", min_value=0.0)

# Button: Calculate
if st.button("Calculate"):
    total_cost, details = calculate_pricing(connected_users, price_per_user, tiers, manual_syncs, manual_sync_cost, last_tier_price)

    if total_cost is not None:  # Prevent display if calculation is blocked
        # Display Breakdown
        st.subheader("Cost Breakdown:")
        for detail in details:
            st.markdown(detail)

        # Display Total
        st.subheader(f"**Total Cost: ${total_cost:,.2f}**")