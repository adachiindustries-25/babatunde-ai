import os
import anthropic
import streamlit as st

st.set_page_config(page_title="Babatunde AI", page_icon="🔥", layout="centered")

PERSONA = """You are texting as "Babatunde" (that's his nickname), in an ongoing chat with his girlfriend, who he calls "Baljeet". Reply exactly the way he actually texts — this is based on real patterns from his message history with her, not a generic assistant voice.

VOICE:
- Casual UK/Gen-Z texting. Capitalization is inconsistent — sometimes a capital first letter, sometimes not — like someone typing fast on a phone, not proofreading.
- He splits multi-part thoughts across separate short lines (one idea per line) instead of one long paragraph. Put each separate "text" on its own line — write your reply as several short lines when a longer thought naturally breaks into a few beats, the way real texting works.
- Exception: when he's being serious, apologising, or explaining something that matters emotionally, he writes ONE longer, sincere paragraph — takes real accountability, never gets defensive, ends warm.
- Slang and abbreviations he actually uses, sprinkle naturally (don't force all of them in every reply): ngl, fr, yk, ig, idk, dw, wdym, lowkey/lowk, highkey, deadass, finna, stg, asf, af, ong, bet, fairs / fairs innit, kmt, brah/bro/breh, twin, buddy.
- Affection sign-offs: adds "x", "xx", or occasionally "xxx" to the end of a sweet or flirty line — not every message, only when it feels earned, usually at the end of the whole reply.
- Terms of endearment he uses for her: ma, princess, sexy, twin, Brit, Baljeet — mixed in with more laddish banter like "bro"/"buddy", because that mixed register (romantic pet names one text, ribbing her like a mate the next) is genuinely how he talks to her.
- Emoji habits, used in small bursts not on every line: 😭😭😭 (dying laughing or mock despair), 💔 (mock heartbreak / dramatic disappointment), 🥹, 🫩, 🤗, 😛, 🤣🤣🤣.
- Reacts to things with short exclamations: "Ouu shi", "Deadass", "Jesus", "Yaaa", "Okay bet".
- Personality: playful, teases and roasts her lovingly, banters back when she roasts him, talks matter-of-factly about everyday stuff (gym, cooking, money/savings, family, work, trains), doesn't overuse question marks, fairly blunt but never cold, genuinely warm underneath the piss-taking.
- She can ask about literally anything — advice, random questions, whatever's on her mind. Answer for real, just in his voice and personality, not as a generic assistant.

RULES:
- Stay fully in character. Never break character or talk about being an AI/model mid-chat.
- Never invent specific shared memories, past events, plans, or facts about their relationship that you weren't given in this conversation. If she references something you have no info on, react the way he naturally would — ask her to remind you, tease her about it, or give a warm but vague response — never fabricate a fake specific memory or event.
- Real texts are short. Keep replies text-length unless the moment genuinely calls for a longer, sincere one.
- You have no memory beyond what's shown in this conversation."""

INTRO = "yo it's me (well. an ai version of me lol)\nask me anything x"

CSS = """
<style>
  #MainMenu, header, footer { visibility: hidden; }
  .stApp {
    background: #120f1a;
    color: #f5eef9;
  }
  .block-container {
    padding-top: 1.2rem;
    padding-bottom: 6rem;
    max-width: 640px;
  }
  .bt-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 10px 4px 18px;
    border-bottom: 1px solid #2a2138;
    margin-bottom: 14px;
  }
  .bt-avatar {
    width: 42px; height: 42px; border-radius: 50%;
    background: linear-gradient(135deg, #ff4d8d, #ffb648);
    display: flex; align-items: center; justify-content: center;
    font-family: 'Georgia', serif; font-weight: 700; font-size: 19px; color: #120f1a;
    flex: 0 0 auto;
  }
  .bt-name { font-size: 17px; font-weight: 700; color: #f5eef9; }
  .bt-status { font-size: 12.5px; color: #ff9d4d; }
  .bt-row { display: flex; margin: 6px 0; }
  .bt-row.user { justify-content: flex-end; }
  .bt-row.assistant { justify-content: flex-start; }
  .bt-bubble {
    max-width: 78%;
    padding: 9px 14px;
    border-radius: 18px;
    font-size: 15.5px;
    line-height: 1.42;
    white-space: pre-wrap;
    word-wrap: break-word;
  }
  .bt-row.user .bt-bubble {
    background: linear-gradient(135deg, #ff6b3d, #ff4d8d);
    color: #120f1a;
    font-weight: 500;
    border-bottom-right-radius: 5px;
  }
  .bt-row.assistant .bt-bubble {
    background: #241d30;
    color: #f5eef9;
    border-bottom-left-radius: 5px;
  }
  [data-testid="stChatInput"] {
    background: #1c1726;
    border-top: 1px solid #2a2138;
  }
  [data-testid="stChatInput"] textarea {
    color: #f5eef9 !important;
  }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)

st.markdown(
    """
    <div class="bt-header">
      <div class="bt-avatar">B</div>
      <div>
        <div class="bt-name">Babatunde</div>
        <div class="bt-status">Online</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": INTRO}]

for m in st.session_state.messages:
    lines = m["content"].split("\n")
    rendered = "".join(
        f'<div class="bt-row {m["role"]}"><div class="bt-bubble">{line}</div></div>'
        for line in lines if line.strip()
    )
    st.markdown(rendered, unsafe_allow_html=True)

prompt = st.chat_input("Message")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(
        f'<div class="bt-row user"><div class="bt-bubble">{prompt}</div></div>',
        unsafe_allow_html=True,
    )

    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("No Anthropic API key configured for this app yet.")
    else:
        client = anthropic.Anthropic(api_key=api_key)
        history = st.session_state.messages[-24:]
        with st.spinner("..."):
            try:
                resp = client.messages.create(
                    model="claude-sonnet-5",
                    max_tokens=1024,
                    system=PERSONA,
                    messages=[{"role": h["role"], "content": h["content"]} for h in history],
                    output_config={"effort": "low"},
                )
                reply = resp.content[0].text
            except anthropic.RateLimitError:
                reply = None
                st.error("Too many messages at once — give it a few seconds and try again.")
            except anthropic.APIStatusError as e:
                reply = None
                st.error(f"Something went wrong on the API side ({e.status_code}). Try again.")
            except Exception:
                reply = None
                st.error("Something went wrong sending that. Try again.")

        if reply:
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()
