import mediapipe as mp
from pathlib import Path
from matchstick import Matchstick
import av
import cv2
import numpy as np
import pydub
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
        "選択クイズ": app_video_filters,  
        "もじぴったん": app_audio_filter,
        "5sec_Late": app_media_constraints,  
        "Customize UI texts": app_customize_ui_texts,
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
    st.title("QuizGame")
    """
    マッチ棒を一回だけ動かして正しい式に直してください
    """
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
        game.combi(img)
        
        results = hands.process(img)
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

def app_video_filters():
    """Video transforms with OpenCV"""

    _type = st.radio("Select transform type", ("noop", "cartoon", "edges", "rotate"))

    def callback(frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="bgr24")

        if _type == "noop":
            pass
        elif _type == "cartoon":
            # prepare color
            img_color = cv2.pyrDown(cv2.pyrDown(img))
            for _ in range(6):
                img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
            img_color = cv2.pyrUp(cv2.pyrUp(img_color))

            # prepare edges
            img_edges = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img_edges = cv2.adaptiveThreshold(
                cv2.medianBlur(img_edges, 7),
                255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY,
                9,
                2,
            )
            img_edges = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)

            # combine color and edges
            img = cv2.bitwise_and(img_color, img_edges)
        elif _type == "edges":
            # perform edge detection
            img = cv2.cvtColor(cv2.Canny(img, 100, 200), cv2.COLOR_GRAY2BGR)
        elif _type == "rotate":
            # rotate image
            rows, cols, _ = img.shape
            M = cv2.getRotationMatrix2D((cols / 2, rows / 2), frame.time * 45, 1)
            img = cv2.warpAffine(img, M, (cols, rows))

        return av.VideoFrame.from_ndarray(img, format="bgr24")

    webrtc_streamer(
        key="opencv-filter",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_frame_callback=callback,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )

    st.markdown(
        "This demo is based on "
        "https://github.com/aiortc/aiortc/blob/2362e6d1f0c730a0f8c387bbea76546775ad2fe8/examples/server/server.py#L34. "  # noqa: E501
        "Many thanks to the project."
    )

def app_audio_filter():
    gain = st.slider("Gain", -10.0, +20.0, 1.0, 0.05)

    def process_audio(frame: av.AudioFrame) -> av.AudioFrame:
        raw_samples = frame.to_ndarray()
        sound = pydub.AudioSegment(
            data=raw_samples.tobytes(),
            sample_width=frame.format.bytes,
            frame_rate=frame.sample_rate,
            channels=len(frame.layout.channels),
        )

        sound = sound.apply_gain(gain)
        channel_sounds = sound.split_to_mono()
        channel_samples = [s.get_array_of_samples() for s in channel_sounds]
        new_samples: np.ndarray = np.array(channel_samples).T
        new_samples = new_samples.reshape(raw_samples.shape)

        new_frame = av.AudioFrame.from_ndarray(new_samples, layout=frame.layout.name)
        new_frame.sample_rate = frame.sample_rate
        return new_frame

    webrtc_streamer(
        key="audio-filter",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        audio_frame_callback=process_audio,
        async_processing=True,
    )

def app_media_constraints():
    """A sample to configure MediaStreamConstraints object"""
    frame_rate = 5
    webrtc_streamer(
        key="media-constraints",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        media_stream_constraints={
            "video": {"frameRate": {"ideal": frame_rate}},
        },
        video_html_attrs={
            "style": {"width": "50%", "margin": "0 auto", "border": "5px yellow solid"},
            "controls": False,
            "autoPlay": True,
        },
    )
    st.write(f"The frame rate is set as {frame_rate}. Video style is changed.")

def app_customize_ui_texts():
    webrtc_streamer(
        key="custom_ui_texts",
        rtc_configuration=RTC_CONFIGURATION,
        translations={
            "start": "開始",
            "stop": "停止",
            "select_device": "デバイス選択",
            "media_api_not_available": "Media APIが利用できない環境です",
            "device_ask_permission": "メディアデバイスへのアクセスを許可してください",
            "device_not_available": "メディアデバイスを利用できません",
            "device_access_denied": "メディアデバイスへのアクセスが拒否されました",
        },
    )

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
