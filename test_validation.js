
function validatePassword(password) {
    if (password.length < 9) return "Password must be at least 9 characters long.";
    if (!/[A-Z]/.test(password)) return "Password must contain at least one uppercase letter.";
    if (!/\d/.test(password)) return "Password must contain at least one number.";
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) return "Password must contain at least one symbol.";
    return null;
}

const tests = [
    { pwd: "short", expected: "Password must be at least 9 characters long." },
    { pwd: "12345678", expected: "Password must be at least 9 characters long." },
    { pwd: "123456789", expected: "Password must contain at least one uppercase letter." }, // No Upper
    { pwd: "ABCDEFGHI", expected: "Password must contain at least one number." }, // No Number
    { pwd: "Abcdefghi", expected: "Password must contain at least one number." }, // No Number
    { pwd: "Abcdefghi1", expected: "Password must contain at least one symbol." }, // No Symbol
    { pwd: "Abcdefghi1!", expected: null }, // Valid (11 chars)
    { pwd: "Weak1!aaaaaaaa", expected: null }, // Valid (>9 chars)
    { pwd: "12345678!", expected: "Password must contain at least one uppercase letter." }, // 9 chars, no upper
];

tests.forEach((t, i) => {
    const result = validatePassword(t.pwd);
    if (result === t.expected) {
        console.log(`Test ${i + 1} Passed: '${t.pwd}' -> ${result}`);
    } else {
        console.error(`Test ${i + 1} FAILED: '${t.pwd}'\n  Expected: ${t.expected}\n  Got:      ${result}`);
    }
});
