import React, { useState, useRef } from 'react';
import Modal from 'react-modal';
import { ReactSketchCanvas } from "react-sketch-canvas";
import CircularProgress from '@mui/material/CircularProgress';


Modal.setAppElement('#root'); // Accessibility settings

function DrawingModal({ isOpen, onClose }) {
    const [drawingData, setDrawingData] = useState({});
    const [isLoading, setIsLoading] = useState(false);
    const canvasRef = useRef(null); // Reference to the canvas for direct manipulation

    const handleClearCanvas = () => {
        canvasRef.current.clearCanvas(); // Clears the canvas
    };

    const handleSubmit = () => {
        setIsLoading(true);
        canvasRef.current.exportPaths().then(paths => {
            const dataStr = JSON.stringify(paths);
    
            fetch('http://localhost:5000/api/upload_drawing', {  // Adjust the endpoint as needed
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: dataStr
            })
            .then(response => response.json())
            .then(result => {
                console.log('Success:', result);
                setTimeout(() => {
                    setIsLoading(false); // Hide loading spinner
                    onClose(); // Optionally close the modal on successful upload
                }, 4000);
            })
            .catch(error => {
                console.error('Error:', error);
                setIsLoading(false);
            });
        });
    };    

    return (
        <Modal
            isOpen={isOpen}
            onRequestClose={onClose}
            style={{
                content: {
                    top: '50%',
                    left: '50%',
                    right: 'auto',
                    bottom: 'auto',
                    transform: 'translate(-50%, -50%)',
                    width: '35%',
                    height: '75%'
                },
                overlay: {
                    zIndex: 1000
                }
            }}
        >
            <ReactSketchCanvas
                ref={canvasRef}
                onChange={setDrawingData}
                userId="user1"
                style={{ width: '98%', height: '95%', border: '2px solid #000', marginLeft: '3px' }}
                strokeColor="#a855f7"
            />
            {isLoading && (
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)'
                }}>
                    <CircularProgress />
                </div>
            )}
            <div style={{
                display: 'flex',
                justifyContent: 'flex-end',
                gap: '15px',
                alignItems: 'center',
                marginTop: '8px',
                marginRight: '2px',
                marginBottom: '-10px'
            }}>
                <button onClick={handleClearCanvas}>Cancel</button>
                <button onClick={onClose}>Close</button>
                <button onClick={handleSubmit}>Submit</button>
            </div>
        </Modal>
    );
}

export default DrawingModal;