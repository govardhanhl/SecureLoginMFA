const password = document.getElementById("password");
const strength = document.getElementById("strength");

if (password) {
    password.addEventListener("input", () => {
        const value = password.value;
        if (value.length < 6) {
            strength.innerText = "Weak password";
            strength.style.color = "red";
        } else if (!/[A-Z]/.test(value) || !/\d/.test(value)) {
            strength.innerText = "Moderate password";
            strength.style.color = "orange";
        } else {
            strength.innerText = "Strong password";
            strength.style.color = "green";
        }
    });
}
