import { useEffect, useRef } from 'react';
import { useLoader, useFrame, useThree } from '@react-three/fiber';
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader';
import { Vector3, MathUtils, Box3, BoxHelper, BoxGeometry, MeshBasicMaterial, Mesh, SphereGeometry } from 'three';
import { MeshStandardMaterial } from 'three';
import ARM1 from './/models/robotarm1.obj';
import { useWorldPosition } from './WorldPositionContext';


function setAbsolutePosition(obj, newPosition) {
    if (obj.parent) {
        obj.position.set(
            newPosition.x,
            newPosition.y,
            newPosition.z
        );
        obj.parent.worldToLocal(obj.position);
    } else {
        obj.position.set(newPosition.x, newPosition.y, newPosition.z);
    }
}

function Model1({ targetRotation1, targetRotation2, boxPosition }) {
    const obj = useLoader(OBJLoader, ARM1);
    const { scene } = useThree();
    const { setPosition } = useWorldPosition();
    const boxRef = useRef();
    const pointRef = useRef();

    if (targetRotation1 == null) {
        targetRotation1 = 0;
    }

    console.log(targetRotation1)

    useEffect(() => {
        obj.traverse(child => {
            if (child.isMesh) {
                child.material = new MeshStandardMaterial({ color: 'red' });
            }
        });

        const box = new Mesh(new BoxGeometry(5, 5, 1.82), new MeshBasicMaterial({ color: 0xff0000, wireframe: true }));
        boxRef.current = box;
        box.position.set(...boxPosition);
        box.add(obj); // Add the model as a child of the box
        scene.add(box);

        const point = new Mesh(new SphereGeometry(0.03, 30, 30), new MeshStandardMaterial({ color: 'blue' }));
        pointRef.current = point;
        point.position.set(0, 2, 0); // Position relative to the box
        box.add(point); // Add the point as a child of the box

        return () => {
            scene.remove(box);
        };
    }, [obj, scene, boxPosition]);

    useFrame(() => {
        if (boxRef.current) {
            boxRef.current.rotation.z = MathUtils.lerp(boxRef.current.rotation.z, targetRotation2 || 0, 0.005);
            boxRef.current.rotation.y = MathUtils.lerp(boxRef.current.rotation.y, targetRotation1 || 0, 0.005);
            boxRef.current.position.set(...boxPosition);
        }

        if (pointRef.current) {
            const worldPosition = new Vector3();
            pointRef.current.getWorldPosition(worldPosition);
            setPosition({ x: worldPosition.x.toFixed(4), y: worldPosition.y.toFixed(4), z: worldPosition.z.toFixed(4) }); // Set position in the context
        }
    });

    return (
        <primitive 
            object={obj} 
            position={[0, 0, 0.845]}
            rotation={[0,  -Math.PI, Math.PI / 2]}
            scale={[0.01, 0.01, 0.01]}
        />
    );
}

export default Model1;