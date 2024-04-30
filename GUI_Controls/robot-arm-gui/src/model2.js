import React, { useEffect, useRef, useState } from 'react';
import { useLoader, useFrame, useThree } from '@react-three/fiber';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';
import { Vector3, MathUtils, BoxGeometry, MeshBasicMaterial, Mesh, MeshStandardMaterial } from 'three';
import { useWorldPosition } from './WorldPositionContext';
import ARM2 from './models/robotarm2.obj';

function Model2({ targetRotation1, targetRotation2, targetRotation3, initialBoxPosition }) {
    const obj = useLoader(OBJLoader, ARM2);
    const { scene } = useThree();
    const boxRef = useRef();
    const { position } = useWorldPosition(); // Assumed to be { x, y, z }
    const [startMoving, setStartMoving] = useState(false);

    useEffect(() => {
        obj.traverse(child => {
            if (child.isMesh) {
                child.material = new MeshStandardMaterial({ color: 'green' });
            }
        });

        const box = new Mesh(new BoxGeometry(3, 3, 1.82), new MeshBasicMaterial({ color: 0xff0000, wireframe: true }));
        boxRef.current = box;
        box.position.set(...initialBoxPosition); // Initialize position from prop
        box.add(obj); // Add the model as a child of the box
        scene.add(box);

        return () => {
            scene.remove(box);
        };
    }, [obj, scene, initialBoxPosition]); // Correct the dependencies if initialBoxPosition is constant remove it from here

    useFrame(() => {
        if (boxRef.current) {
            // Perform lerp rotation
            boxRef.current.rotation.z = MathUtils.lerp(boxRef.current.rotation.z, targetRotation2 || 0, 0.01);
            boxRef.current.rotation.y = MathUtils.lerp(boxRef.current.rotation.y, targetRotation1 || 0, 0.01);

            // Check to start moving
            if (!startMoving && (Math.abs(boxRef.current.rotation.z) > 0.01 || Math.abs(boxRef.current.rotation.y) > 0.01)) {
                setStartMoving(true);
            }

            // Move based on updated context position
            if (startMoving) {
                boxRef.current.position.x = MathUtils.lerp(boxRef.current.position.x, initialBoxPosition[0] - position.x, 0.01);
                boxRef.current.position.y = MathUtils.lerp(boxRef.current.position.y, initialBoxPosition[1] + position.y, 0.01);
            }
        }
    });

    return (
        <primitive 
            object={obj} 
            position={[0, 0, -0.1155]}
            rotation={[0, 0, 0]}
            scale={[0.01, 0.01, 0.01]}
        />
    );
}

export default Model2;
