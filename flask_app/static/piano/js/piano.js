/**
 * Key Functionalities
 * 
 * - 
 */
document.addEventListener("DOMContentLoaded", function () {
    // Define key bindings for white and black keys
    const whiteKeyBindings = ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"];
    const blackKeyBindings = ["W", "E", "T", "Y", "U", "O", "P"];

    const sound = {
        65: "http://carolinegabriel.com/demo/js-keyboard/sounds/040.wav",
        87: "http://carolinegabriel.com/demo/js-keyboard/sounds/041.wav",
        83: "http://carolinegabriel.com/demo/js-keyboard/sounds/042.wav",
        69: "http://carolinegabriel.com/demo/js-keyboard/sounds/043.wav",
        68: "http://carolinegabriel.com/demo/js-keyboard/sounds/044.wav",
        70: "http://carolinegabriel.com/demo/js-keyboard/sounds/045.wav",
        84: "http://carolinegabriel.com/demo/js-keyboard/sounds/046.wav",
        71: "http://carolinegabriel.com/demo/js-keyboard/sounds/047.wav",
        89: "http://carolinegabriel.com/demo/js-keyboard/sounds/048.wav",
        72: "http://carolinegabriel.com/demo/js-keyboard/sounds/049.wav",
        85: "http://carolinegabriel.com/demo/js-keyboard/sounds/050.wav",
        74: "http://carolinegabriel.com/demo/js-keyboard/sounds/051.wav",
        75: "http://carolinegabriel.com/demo/js-keyboard/sounds/052.wav",
        79: "http://carolinegabriel.com/demo/js-keyboard/sounds/053.wav",
        76: "http://carolinegabriel.com/demo/js-keyboard/sounds/054.wav",
        80: "http://carolinegabriel.com/demo/js-keyboard/sounds/055.wav",
        186: "http://carolinegabriel.com/demo/js-keyboard/sounds/056.wav"
    };

    const whiteKeys = document.querySelectorAll(".key.white");
    const blackKeys = document.querySelectorAll(".key.black");

    const keyMap = {}; // Map keys to their corresponding elements

    // white key labels)
    whiteKeys.forEach((key, index) => {
        key.dataset.key = whiteKeyBindings[index]; // Store key in dataset
        key.innerHTML = `<span class="key-label">${whiteKeyBindings[index]}</span>`; // Add label
        keyMap[whiteKeyBindings[index]] = { element: key, type: "white" };

        key.addEventListener("mouseover", function () {
            let keyLabel = key.querySelector(".key-label");
            keyLabel.style.opacity = 1; // Make label visible on hover
        });

        key.addEventListener("mouseout", function () {
            let keyLabel = key.querySelector(".key-label");
            keyLabel.style.opacity = 0; // Hide label on mouse out
        });
    });

    // black key labels
    blackKeys.forEach((key, index) => {
        if (blackKeyBindings[index] !== "") { // Avoid empty placeholders
            key.dataset.key = blackKeyBindings[index]; // Store key in dataset
            key.innerHTML = `<span class="key-label">${blackKeyBindings[index]}</span>`; // Add label
            keyMap[blackKeyBindings[index]] = { element: key, type: "black" };

            key.addEventListener("mouseover", function () {
                let keyLabel = key.querySelector(".key-label");
                keyLabel.style.opacity = 1; // Make label visible on hover
            });

            key.addEventListener("mouseout", function () {
                let keyLabel = key.querySelector(".key-label");
                keyLabel.style.opacity = 0; // Hide label on mouse out
            });
        }
    });

    // vars for The Great Old One
    const sequence = "WESEEYOU";
    let typedSequence = "";
    let pianoAwakened = false;

    // key pressed
    document.addEventListener("keydown", function (event) {
        if (pianoAwakened) return; // Disable further key presses after the piano awakens

        let key = event.key.toUpperCase();
        typedSequence += key;

        if (typedSequence.includes(sequence)) {
            awakenGreatOldOne();
        }

        if (keyMap[key]) {
            let { element, type } = keyMap[key];
            let label = element.querySelector(".key-label");

            // Add pressed class and show label when key is pressed
            element.classList.add(type === "white" ? "white-pressed" : "black-pressed");
            label.style.opacity = 1; // label stays visible when key is pressed
            
            let keyCode = event.keyCode;
            if (sound[keyCode]) {
                let soundUrl = sound[keyCode];
                let audio = new Audio(soundUrl);
                audio.play(); // Play the sound for the key pressed
            }
        }
    });

    // key up
    document.addEventListener("keyup", function (event) {
        let key = event.key.toUpperCase();
        if (keyMap[key]) {
            let { element, type } = keyMap[key];
            let label = element.querySelector(".key-label");

            // Remove pressed class and hide label when key is released
            element.classList.remove(type === "white" ? "white-pressed" : "black-pressed");
            label.style.opacity = 0; // Hide label when key is released
        }
    });

    function awakenGreatOldOne() {
        // Play sound
        const creepyAudio = new Audio("https://orangefreesounds.com/wp-content/uploads/2020/09/Creepy-piano-sound-effect.mp3?_=1");
        creepyAudio.play();
    
        // Gradually fade the piano
        const pianoContainer = document.querySelector(".piano-container");
        pianoContainer.style.transition = "opacity 2s";
        pianoContainer.style.opacity = "0";
    
        // Display the Great Old One as an overlay
        setTimeout(function () {
            const overlay = document.createElement("div");
            overlay.className = "great-old-one";
    
            // Create the image element for the Great Old One
            const greatOldOneImage = document.createElement("img");
            greatOldOneImage.src = "../static/piano/images/texture.jpeg"; 
            greatOldOneImage.className = "great-old-one-img"; 
            greatOldOneImage.alt = "The Great Old One image";
    
            // Append the image to the overlay
            overlay.appendChild(greatOldOneImage);
    
            // Add the overlay to the body
            document.body.appendChild(overlay);
        }, 1000); // Wait for the piano to fade out before showing the image
    
        // Stop the piano from responding to key presses
        pianoAwakened = true;
    }
    
    
    
});
