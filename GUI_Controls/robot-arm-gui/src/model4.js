import { useRef, useEffect } from 'react';
import { useLoader } from '@react-three/fiber';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';
import BASE from './models/robotbase.obj';
import { MeshStandardMaterial } from 'three';
import React from 'react';
import Model3 from './model3';

function Model4() {
    const obj = useLoader(OBJLoader, BASE);
    const objRef = useRef();

    // Initialize the ref on component mount
    useEffect(() => {
        obj.traverse((child) => {
            if (child.isMesh) {
                child.material = new MeshStandardMaterial({ color: 'yellow' });
            }
        });

        // Assuming obj is not null and is properly loaded
        objRef.current = obj;
    }, [obj]);

    return (
        <>
            <primitive 
                object={obj} 
                ref={objRef} // Make sure ref is passed here
                scale={[0.01, 0.01, 0.01]} 
                position={[0, 1.1, 0]} 
                rotation={[Math.PI / 2, 0, 0]}
            />
        </>
    );
}

export default Model4;
