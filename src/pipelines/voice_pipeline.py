import io

import numpy as np
import streamlit as st

_encoder = None
_voice_import_error = None


def _load_voice_dependencies():
    global _voice_import_error
    try:
        from resemblyzer import VoiceEncoder, preprocess_wav
        import librosa

        return VoiceEncoder, preprocess_wav, librosa
    except Exception as exc:
        _voice_import_error = exc
        return None, None, None


def is_voice_available():
    VoiceEncoder, _, _ = _load_voice_dependencies()
    return VoiceEncoder is not None


def voice_unavailable_message():
    if _voice_import_error:
        return (
            "Voice attendance is not installed. Run "
            "`pip install -r requirements-voice.txt` in a Python 3.10 or 3.11 virtual "
            f"environment. Details: {_voice_import_error}"
        )
    return "Voice attendance is not installed."


def load_voice_encoder():
    global _encoder
    VoiceEncoder, _, _ = _load_voice_dependencies()
    if VoiceEncoder is None:
        raise RuntimeError(voice_unavailable_message())
    if _encoder is None:
        _encoder = VoiceEncoder()
    return _encoder


def get_voice_embedding(audio_bytes):
    try:
        if not audio_bytes or len(audio_bytes) == 0:
            return None

        encoder = load_voice_encoder()
        _, preprocess_wav, librosa = _load_voice_dependencies()
        audio, _ = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        wav = preprocess_wav(audio)
        embedding = encoder.embed_utterance(wav)
        return embedding.tolist()

    except Exception as e:
        st.error(f'Voice error: {str(e)}')
        return None


def identify_speaker(new_embedding, candidates_dict, threshold=0.65):
    if new_embedding is None or not candidates_dict:
        return None, 0.0
    best_sid = None
    best_score = -1.0
    for sid, stored_embedding in candidates_dict.items():
        if stored_embedding:
            similarity = np.dot(new_embedding, stored_embedding)
            if similarity > best_score:
                best_score = similarity
                best_sid = sid
    if best_score >= threshold:
        return best_sid, best_score
    return None, best_score


def process_bulk_audio(audio_bytes, candidates_dict, threshold=0.65):
    try:
        encoder = load_voice_encoder()
        _, preprocess_wav, librosa = _load_voice_dependencies()
        audio, sr = librosa.load(io.BytesIO(audio_bytes), sr=16000)
        segments = librosa.effects.split(audio, top_db=30)
        identified_results = {}
        for start, end in segments:
            if (end - start) < sr * 0.5:
                continue
            segment_audio = audio[start:end]
            wav = preprocess_wav(segment_audio)
            embedding = encoder.embed_utterance(wav)
            sid, score = identify_speaker(embedding, candidates_dict, threshold)
            if sid:
                if sid not in identified_results or score > identified_results[sid]:
                    identified_results[sid] = score
        return identified_results
    except Exception as e:
        st.error(f'Bulk process error: {str(e)}')
        return {}
