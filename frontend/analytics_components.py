"""Analytics page - renders usage statistics in the main content area."""
import streamlit as st
import pandas as pd
from backend.analytics_service import compute_analytics


def render_analytics_page():
    """Render the full analytics dashboard in the main content area."""

    st.markdown("# Analytics")
    st.caption("Your usage overview")

    user = st.session_state.get("user")
    if not user:
        st.info("Sign in to view your analytics.")
        return

    chat_sessions = st.session_state.get("chat_sessions", {})
    stats = compute_analytics(chat_sessions)

    if stats["total_chats"] == 0:
        st.info("No chat data yet. Start a conversation to see your stats!")
        return

    # ── Summary cards ──
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Chats", stats["total_chats"])
    c2.metric("Messages Sent", stats["total_user_msgs"])
    c3.metric("AI Responses", stats["total_assistant_msgs"])
    c4.metric("Avg / Chat", stats["avg_msgs_per_chat"])

    st.markdown("")

    # ── Today snapshot ──
    t1, t2, t3 = st.columns(3)
    t1.metric("Today's Chats", stats["today_chats"])
    t2.metric("Today's Messages", stats["today_msgs"])
    t3.metric("Words Written", f"{stats['total_user_words']:,}")

    st.markdown("")
    st.markdown("---")

    # ── Last 7 days charts ──
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("##### Chats — Last 7 Days")
        if stats["chats_last_7_days"]:
            df_chats = pd.DataFrame({
                "Day": list(stats["chats_last_7_days"].keys()),
                "Chats": list(stats["chats_last_7_days"].values()),
            })
            st.bar_chart(df_chats, x="Day", y="Chats", color="#818cf8", height=220)
        else:
            st.caption("No data")

    with col_right:
        st.markdown("##### Messages — Last 7 Days")
        if stats["msgs_last_7_days"]:
            df_msgs = pd.DataFrame({
                "Day": list(stats["msgs_last_7_days"].keys()),
                "Messages": list(stats["msgs_last_7_days"].values()),
            })
            st.bar_chart(df_msgs, x="Day", y="Messages", color="#34d399", height=220)
        else:
            st.caption("No data")

    st.markdown("---")

    # ── Insights row ──
    i1, i2, i3 = st.columns(3)

    with i1:
        st.markdown("##### Longest Chat")
        if stats["longest_chat_title"]:
            st.markdown(f"**{stats['longest_chat_title']}**")
            st.caption(f"{stats['longest_chat_len']} messages")
        else:
            st.caption("-")

    with i2:
        st.markdown("##### Most Active Day")
        st.markdown(f"**{stats['most_active_day'] or '-'}**")

    with i3:
        st.markdown("##### Characters Written")
        st.markdown(f"**{stats['total_user_chars']:,}**")
        st.caption("your messages")

    # ── Persona usage ──
    if stats["persona_usage"] and len(stats["persona_usage"]) > 1:
        st.markdown("---")
        st.markdown("##### Persona Usage")
        df_persona = pd.DataFrame({
            "Persona": list(stats["persona_usage"].keys()),
            "Chats": list(stats["persona_usage"].values()),
        })
        st.bar_chart(df_persona, x="Persona", y="Chats", color="#f59e0b", height=200)
