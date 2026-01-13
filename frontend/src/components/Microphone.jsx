import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import {
  Mic,
  MicOff
} from 'lucide-react';
import '../App.css';

export default async function Microphone(){
    const [disabled, setDisabled] = useState(true);
    const [isRecording, setIsRecording] = useState(false);

    useEffect(() => {
        // Ask for microhpone access on component mount
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then((stream) => {
                setDisabled(false);
                // Save audio on global window for later use
                window.localStream = stream;

            })
            .catch((err) => {
                console.error("Microphone access denied:", err);
                setDisabled(true);
            });
    })

    // TODO: Add logic to listen for permission changes



    const handleRecording = async () => {
        // Prevent toggling if disabled
        // TODO: Implement modal to inform user to enable microphone access?
        if (disabled) return;
        setIsRecording(!isRecording);
        if (isRecording){
            // TODO: Record user's audio
        } else{
            // TODO: Stop recording and handle audio transcription
        }
    }

    return (
        <button
            disabled={disabled}
            className={`mic-button ${isRecording ? 'recording' : ''}`}
            onClick={() => {
                handleRecording();
            }}
        >
            {disabled ? <MicOff /> : <Mic />}
        </button>
    );
}