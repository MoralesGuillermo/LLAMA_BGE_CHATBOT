import React, { useState, useEffect, useRef } from 'react';
import {
  Mic,
  MicOff
} from 'lucide-react';
import '../App.css';

export default function Microphone(){
    // TODO: CLEAN CODE METHODS. SEPARATE CONCERNS FOR BETTER READABILITY
    // TODO: Implement comm with LLM for audio transcription
    const [disabled, setDisabled] = useState(true);
    const [isRecording, setIsRecording] = useState(false);
    let audioChunks = useRef([]);
    let mediaRecorder = useRef(null);
    let speechRecognition = useRef(null);
    // Enable Recording and MediaRecorder setup
    useEffect(() => {
        // Ask for microphone access on component mount
        navigator.mediaDevices.getUserMedia({ audio: true })
        .then((stream) => {
            // Save the audio stream for later use
            mediaRecorder.current = new MediaRecorder(stream); 
            // Add audio chunks when available
            mediaRecorder.current.ondataavailable = (event) => {
                audioChunks.current = [...audioChunks.current, event.data];
            };
            // Handle Stop logic
            mediaRecorder.current.onstop = (event) => {
                const blob = new Blob(audioChunks.current, { type: 'audio/wav' });
                const audioUrl = URL.createObjectURL(blob);
                // For testing: open the recorded audio in a new tab
                window.open(audioUrl); 
                // Clear audio chunks for the next recording
                audioChunks.current = [];
            }
            setDisabled(false);
            })
        .catch((err) => {
            console.error("Microphone access denied:", err);
            setDisabled(true);
        });
    }, []);


    useEffect(() => {
        const addMicPermissionListener = async () => {
            navigator.permissions.query({ name: 'microphone' })
                .then((permissionStatus) => {
                    permissionStatus.onchange = () => {
                        if (permissionStatus.state === 'granted') {
                            setDisabled(false);
                        } else {
                            setDisabled(true);
                        }
                    };
                });
        };
        addMicPermissionListener();
    }, [])

    // Init Speech Recognition service
    useEffect(() => {
        const SpeechRecognition = (window.SpeechRecognition || window.webkitSpeechRecognition);
        if (typeof SpeechRecognition === "undefined") {
            console.error("Speech Recognition API not supported in this browser.");
            return;
        }
        speechRecognition.current = new SpeechRecognition();
        speechRecognition.current.lang = "es-ES";
        speechRecognition.current.onspeechend = () => {
            speechRecognition.current.stop();
            mediaRecorder.current.stop();
            setIsRecording(false);
        }
    }, []);

    const handleRecording = async () => {
        // TODO: Implement modal to inform user to enable microphone access?
        // Prevent toggling if disabled
        if (disabled) return;
        const toggleRecording = !isRecording;
        if (toggleRecording){
            // Start recording
            mediaRecorder.current.start(1000);
            // Start recongnition service to stop on silence
            if (speechRecognition.current)
                speechRecognition.current?.start();
            console.log("Recording started");
        } else{
            // Stop recording
            mediaRecorder.current.stop();
            console.log("Recording stopped");
        }
        setIsRecording(toggleRecording);
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