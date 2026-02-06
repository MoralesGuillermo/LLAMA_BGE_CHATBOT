import React, { useState, useEffect, useRef } from 'react';
import {
  Mic,
  MicOff
} from 'lucide-react';
import '../App.css';

export default function Microphone({ onRecorded }) {
    // TODO: CLEAN CODE METHODS. SEPARATE CONCERNS FOR BETTER READABILITY
    // TODO: Implement comm with LLM for audio transcription
    const [disabled, setDisabled] = useState(true);
    const [isRecording, setIsRecording] = useState(false);
    const audioMimeType = 'audio/opus';
    let audioChunks = useRef([]);
    let mediaRecorder = useRef(null);
    let speechRecognition = useRef(null);
    
    // Media Recorder setup
    useEffect(() => {
        // Ask for microphone access on component mount
        navigator.mediaDevices.getUserMedia({ 
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
            } 
        })
        .then((stream) => {
            // Configure and set the MediaRecorder object
            options = { mimeType: audioMimeType };
            mediaRecorder.current = new MediaRecorder(stream, options); 
            
            // Handle Recording logic. Add chunks when available
            mediaRecorder.current.ondataavailable = (event) => {
                audioChunks.current = [...audioChunks.current, event.data];
            };

            // Handle Stop logic
            mediaRecorder.current.onstop = (event) => {
                const blob = new Blob(audioChunks.current, { type: audioMimeType });
                const audioUrl = URL.createObjectURL(blob);
                // Clear audio chunks for the next recording
                audioChunks.current = [];
            }
            
            // Enable the microphone button if access was granted
            setDisabled(false);
            }
        )
        .catch((err) => {
            // Disable the microphone button if access was denied
            console.error("Microphone access denied:", err);
            setDisabled(true);
        });
    }, []);

    // Listen for microphone permission changes
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

    // Init Speech Recognition service. SR is used to stop recording when user stops speaking
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
        if (disabled) return;

        const toggleRecording = !isRecording;
        if (toggleRecording){
            // Start recording
            mediaRecorder.current.start(1000);
            // Start recongnition service to stop when user stops speaking
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