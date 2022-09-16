import mediapipe as mp
from pathlib import Path
from matchstick import Matchstick
from number import Number
import av
import cv2
import streamlit as st
import logging

from streamlit_webrtc import (
    RTCConfiguration,
    WebRtcMode,
    webrtc_streamer,
)

path = Path(__file__).parent
logger = logging.getLogger(__name__)

#WebRTCの設定
RTC_CONFIGURATION = RTCConfiguration(
    #Google提供のSTUNサーバー
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
    # Mozilla提供のSTUNサーバー
    # {"iceServers": [{"urls": ["stun.services.mozilla.com"]}]}
)


def main():
    st.header("GAMES")

    pages = {
        "マッチ棒": matchstick,
        "数字クイズ": number,  
    }
    page_titles = pages.keys()

    page_title = st.sidebar.selectbox(
        "Choose the game",
        page_titles,
    )
    st.subheader(page_title)

    page_func = pages[page_title]
    page_func()


def matchstick():
    # st.title("QuizGame")
    st.text("マッチ棒を一回だけ動かして正しい式に直してください")
    mp_hands = mp.solutions.hands #モデルの作成
    hands = mp_hands.Hands(
        min_detection_confidence=0.2,
        min_tracking_confidence=0.2,
        max_num_hands = 1
        )
    game = Matchstick()
    
    def callback(frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img,1)
        results = hands.process(img)
        game.combi(img)
        if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    game.move(img, hand_landmarks)
                    game.hand(img, hand_landmarks)
        return av.VideoFrame.from_ndarray(img, format="bgr24")

    webrtc_streamer(
        key="matchstick",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_frame_callback=callback,
        media_stream_constraints={"video": True, "audio": False},
        video_html_attrs={
            "style": {"width": "100%", "margin": "0 auto", "border": "1px yellow solid"},
            "controls": False,
            "autoPlay": True,
        },
        async_processing=True,
    )
    """
    カメラを起動して数秒間は不安定です！数秒待ってプレイしてください
    カメラが固まった場合はカメラを再起動してください
    """

def number():
    st.text("タイルを一回だけ動かして正しい式に直してください")
    mp_hands = mp.solutions.hands #モデルの作成
    hands = mp_hands.Hands(
        min_detection_confidence=0.2,
        min_tracking_confidence=0.2,
        max_num_hands = 1
        )
    game = Number()
    
    def callback(frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")
        img = cv2.flip(img,1)
        #合成
        game.combi(img)
        
        results = hands.process(img)
        if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    #ゲームの処理
                    game.move(img, hand_landmarks)
                    game.hand(img, hand_landmarks)
        return av.VideoFrame.from_ndarray(img, format="bgr24")

    webrtc_streamer(
        key="number",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_frame_callback=callback,
        media_stream_constraints={"video": True, "audio": False},
        video_html_attrs={
            "style": {"width": "100%", "margin": "0 auto", "border": "1px yellow solid"},
            "controls": False,
            "autoPlay": True,
        },
        async_processing=True,
    )
    """
    カメラを起動して数秒間は不安定です！数秒待ってプレイしてください
    カメラが固まった場合はカメラを再起動してください
    """
if __name__ == "__main__":
    import os

    DEBUG = os.environ.get("DEBUG", "false").lower() not in ["false", "no", "0"]

    logging.basicConfig(
        format="[%(asctime)s] %(levelname)7s from %(name)s in %(pathname)s:%(lineno)d: "
        "%(message)s",
        force=True,
    )

    logger.setLevel(level=logging.DEBUG if DEBUG else logging.INFO)

    st_webrtc_logger = logging.getLogger("streamlit_webrtc")
    st_webrtc_logger.setLevel(logging.DEBUG)

    fsevents_logger = logging.getLogger("fsevents")
    fsevents_logger.setLevel(logging.WARNING)
    
    main()
