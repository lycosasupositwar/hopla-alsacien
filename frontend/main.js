const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('container').appendChild(renderer.domElement);

const geometry = new THREE.SphereGeometry(0.1, 32, 32);
const material = new THREE.MeshBasicMaterial({ color: 0xff0000 });
const pointsGroup = new THREE.Group();
scene.add(pointsGroup);

camera.position.z = 5;

function addPoint() {
    const l = parseFloat(document.getElementById('l').value);
    const a = parseFloat(document.getElementById('a').value);
    const b = parseFloat(document.getElementById('b').value);
    const text = document.getElementById('text').value;

    fetch('http://localhost:3000/add-point', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ l, a, b, text }),
    })
    .then(response => response.text())
    .then(data => {
        console.log(data);
        updatePoints();
    });
}

function updatePoints() {
    fetch('http://localhost:3000/get-points')
        .then(response => response.json())
        .then(points => {
            pointsGroup.clear();
            points.forEach(point => {
                const sphere = new THREE.Mesh(geometry, material);
                sphere.position.set(point.a, point.b, point.l);
                pointsGroup.add(sphere);
            });
        });
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

animate();
updatePoints();
