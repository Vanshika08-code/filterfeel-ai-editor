import streamlit as st
from mood_filter import get_filter_for_mood, gpt_based_mood_filter, generate_caption_for_mood, recommend_music_for_mood
from image_editor import apply_filter
from PIL import Image
import os
import io
import re

# Page config
st.set_page_config(page_title="FilterFeel", page_icon="🎭", layout="wide")
st.title("🎭 FilterFeel - AI Mood-Based Photo Editor")
st.write("Upload your photo and enter your mood to get a matching filter, creative caption, and music suggestion.")

# API Key check
openai_key = os.getenv("OPENAI_API_KEY", "")
if not openai_key or not openai_key.startswith("sk-"):
    st.error("OpenAI API key not set. Please set it in your environment variables.")
else:
    # Sidebar input
    with st.sidebar:
        st.title("💭 Mood and Photo Input")

        # Mood input
        preset_moods = ["😊 Happy", "😢 Sad", "😤 Angry", "😌 Calm", "🤩 Excited", "✍️ Enter your own"]
        selected_mood = st.selectbox("Choose a mood or write your own:", preset_moods)
        custom_mood = ""
        if selected_mood == "✍️ Enter your own":
            custom_mood = st.text_input("Enter your custom mood:")
        user_mood = custom_mood if selected_mood == "✍️ Enter your own" else selected_mood
        # 🎨 Mood-Based Background Color Setter
def set_mood_background(mood):
    mood = mood.lower()
    if "happy" in mood:
        color = "#FFF9C4"  # Yellowish
    elif "sad" in mood:
        color = "#BBDEFB"  # Blue shades
    elif "angry" in mood:
        color = "#FFCDD2"  # Reddish
    elif "calm" in mood or "relax" in mood:
        color = "#C8E6C9"  # Soft green
    elif "excite" in mood:
        color = "#FFD180"  # Orange-peach
    else:
        color = "#F5F5F5"  # Neutral gray

    st.markdown(f"""
        <style>
        .stApp {{
            background-color: {color};
        }}
        </style>
    """, unsafe_allow_html=True)

# Call the function to set background color
set_mood_background(user_mood)
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
# 📌 Tooltip-enhanced filter choice
st.markdown("**Choose a filter type:**")
filter_choice = st.radio(
    label="",
    options=[
        "🧠 GPT-Based – Uses AI creativity for unique filter",
        "⚙️ Rule-Based – Predefined filters based on logic"
    ]
)

# Clean the value for processing
if "GPT" in filter_choice:
    filter_choice = "GPT-Based"
else:
    filter_choice = "Rule-Based"

submitted = st.form(key="mood_form").form_submit_button("✨ Get Mood Filter")

    # Store results in session state
if "results" not in st.session_state:
    st.session_state["results"] = None

    # Submission handling
    if submitted:
        if not user_mood.strip():
            st.warning("Please enter your mood!")
        elif not uploaded_file:
            st.warning("Please upload an image!")
        elif len(user_mood.strip()) < 3 or re.fullmatch(r"[0-9\s\W_]+", user_mood):
            st.warning("Please enter a meaningful mood (at least 3 letters, not just numbers/symbols).")
        else:
            with st.spinner("Analyzing your mood and processing your image..."):
                try:
                    # Apply selected filter only
                    if filter_choice == "Rule-Based":
                        applied_filter = get_filter_for_mood(user_mood)
                    else:
                        applied_filter = gpt_based_mood_filter(user_mood)

                    # Other outputs
                    caption = generate_caption_for_mood(user_mood)
                    music_title, music_youtube, music_spotify = recommend_music_for_mood(user_mood)

                    image = Image.open(uploaded_file)
                    filtered_image = apply_filter(image, applied_filter)

                    # Store results
                    st.session_state["results"] = {
                        "filter_choice": filter_choice,
                        "applied_filter": applied_filter,
                        "caption": caption,
                        "music_title": music_title,
                        "music_youtube": music_youtube,
                        "music_spotify": music_spotify,
                        "image": image,
                        "filtered_image": filtered_image
                    }
                except Exception as e:
                    st.error(f"Something went wrong during processing: {str(e)}")
                    st.stop()

    # Show results
    results = st.session_state.get("results")
    if results:
        st.success("Here are your mood-based enhancements!")
        st.balloons()

        st.markdown(f"**Applied Filter ({results['filter_choice']}):** `{results['applied_filter']}`")
        st.markdown(f"**Caption:** _{results['caption']}_")
        st.markdown(f"**Music Recommendation:** _{results['music_title']}_")
        st.markdown(f"[▶️ YouTube]({results['music_youtube']}) | [🎵 Spotify]({results['music_spotify']})")

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📤 Original Image")
            st.image(results["image"], use_column_width=True)
        with col2:
            st.subheader(f"🎨 Filtered Image ({results['filter_choice']})")
            st.image(results["filtered_image"], use_column_width=True)
            # 🌟 Mood Quote Mapping
def get_mood_quote(mood):
    mood = mood.lower()
    if "happy" in mood:
        return "“Happiness is contagious.”"
    elif "sad" in mood:
        return "“It’s okay to not be okay.”"
    elif "angry" in mood:
        return "“Speak when you are calm, not when you are angry.”"
    elif "calm" in mood or "relax" in mood:
        return "“In the calm is the clarity.”"
    elif "excite" in mood:
        return "“Let your excitement lead the way.”"
    elif "love" in mood:
        return "“Where there is love, there is life.”"
    elif "sleep" in mood:
        return "“Even the moon needs rest.”"
    elif "peace" in mood or "serene" in mood:
        return "“Peace begins with a smile.”"
    elif "stress" in mood:
        return "“Breathe. You’ve got this.”"
    elif "focus" in mood:
        return "“Focus on the step in front of you, not the whole staircase.”"
    else:
        return "“Every mood tells a story.”"

# ✨ Display quote
quote = get_mood_quote(user_mood)
st.markdown(f"<div style='padding: 1em; background-color: #f9f9f9; border-left: 5px solid #ccc; font-style: italic;'>{quote}</div>", unsafe_allow_html=True)
st.markdown("### ⬇️ Download")
buf = io.BytesIO()
if results and results.get("filtered_image") is not None:
    try:
        results["filtered_image"].save(buf, format="PNG")
        byte_im = buf.getvalue()
        st.download_button(
            label="Download Filtered Image",
            data=byte_im,
            file_name="filtered_image.png",
            mime="image/png"
        )
    except Exception as e:
        st.warning(f"⚠️ Could not prepare image for download. Error: {e}")
else:
    st.warning("⚠️ Filtered image not available. Try again with a different mood or image.")
st.markdown("---")
col3, col4 = st.columns(2)
with col3:
    if st.button("🔁 Try Again"):
        st.session_state["results"] = None
        st.stop()

with col4:
    if st.button("🗑️ Clear Results"):
        st.session_state["results"] = None
        st.success("Results cleared! You can start fresh now.")
        st.stop()
    else:
        st.info("Fill the input panel and submit to see results here.")
